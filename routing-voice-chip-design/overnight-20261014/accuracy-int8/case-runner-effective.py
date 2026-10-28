def run_case(task):
    stage, name, item, p = task
    case_id = f'{name}-input-{item["input_index"]:03}'
    directory = BUILD / stage / case_id; directory.mkdir(parents=True)
    request = {**{k: item[k] for k in ('id', 'role', 'condition', 'seed', 'reference', 'signal_file', 'signal_file_sha256', 'input_float32_sha256')},
        'case_id': case_id, 'model': name, 'model_directory': p['models'][name]['directory'],
        'model_files': p['models'][name]['files'], 'native_library_sha256': p['native_library_sha256'],
        'trace': False, 'save_returned_pcm': name == 'original'}
    request_path = directory / 'request.json'; write_new(request_path, request)
    env = os.environ.copy(); env.update(p['BLAS_environment']); env['MOONSHINE_ORT_SINGLE_THREAD'] = '1'
    start = time.monotonic()
    with (directory / 'native.log').open('x') as output:
        try:
            process = subprocess.run([sys.executable, str(WORK / 'isolate_native_worker_singlethread.py'), str(request_path)],
                cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT, timeout=p['maximum_seconds_per_process'])
            status = {'case_id': case_id, 'exit_code': process.returncode}
        except subprocess.TimeoutExpired:
            status = {'case_id': case_id, 'timeout': True}
    status.update({'elapsed_seconds': time.monotonic()-start, 'log_sha256': sha(directory / 'native.log'),
                   'close_complete': 'AUDIT_CLOSE_COMPLETE' in (directory / 'native.log').read_text()})
    row = None
    if (directory / 'result.json').exists():
        row = json.loads((directory / 'result.json').read_text())
        assert row['request_sha256'] == sha(request_path)
        assert row['input_float32_sha256'] == item['input_float32_sha256']
        assert row['edits'] == edits(row['reference'], row['hypothesis'])['edits']
        row.update({'input_index': item['input_index'], 'partitions': item['partitions'], 'speaker': item['speaker']})
        canonical = [{k: line[k] for k in ('start_time', 'duration', 'samples', 'input_float32_sha256', 'is_complete')} for line in row['lines']]
        row['segment_pcm_boundary_sha256'] = digest(canonical)
        status['result_sha256'] = sha(directory / 'result.json')
    return status, row
