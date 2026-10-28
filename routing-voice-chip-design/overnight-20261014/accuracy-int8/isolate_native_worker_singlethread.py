#!/usr/bin/env python3
"""One immutable audio input, one fresh native controller, one preserved result."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

import numpy as np
from moonshine_voice import Transcriber, ModelArch
from stt_metrics import edits, words


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    request_path = Path(sys.argv[1])
    request = json.loads(request_path.read_text())
    out = request_path.parent / 'result.json'
    if out.exists():
        raise ValueError('Do not replace an isolated inference result')
    assert os.environ.get('MOONSHINE_ORT_SINGLE_THREAD') == '1'
    assert sha(request['signal_file']) == request['signal_file_sha256']
    signal = np.load(request['signal_file'])
    assert signal.dtype == np.float32 and signal.ndim == 1
    assert hashlib.sha256(signal.tobytes()).hexdigest() == request['input_float32_sha256']
    for item in request['model_files']:
        assert sha(item['path']) == item['sha256']
    options = {'log_ort_run': 'true'} if request['trace'] else None
    begin = time.perf_counter()
    native = Transcriber(request['model_directory'], ModelArch.TINY_STREAMING, options=options)
    assert sha(native._lib._name) == request['native_library_sha256']
    load_seconds = time.perf_counter() - begin
    before = resource.getrusage(resource.RUSAGE_SELF)
    ctypes.CDLL(None).fflush(None)
    print('AUDIT_CALL_BEGIN ' + json.dumps({'ordinal': 0, 'id': request['id']}), flush=True)
    start = time.perf_counter()
    transcript = native.transcribe_without_streaming(signal.tolist(), 16000, flags=0)
    elapsed = time.perf_counter() - start
    ctypes.CDLL(None).fflush(None)
    print('AUDIT_CALL_END ' + json.dumps({'ordinal': 0, 'id': request['id']}), flush=True)
    after = resource.getrusage(resource.RUSAGE_SELF)
    hypothesis = ' '.join(line.text for line in transcript.lines)
    lines = []
    for index, line in enumerate(transcript.lines):
        audio = np.asarray(line.audio_data, dtype=np.float32)
        item = {'text': line.text, 'start_time': line.start_time, 'duration': line.duration,
                'is_complete': line.is_complete, 'samples': len(audio),
                'input_float32_sha256': hashlib.sha256(audio.tobytes()).hexdigest()}
        if request['save_returned_pcm']:
            path = request_path.parent / f'line-{index}.npy'
            np.save(path, audio, allow_pickle=False)
            item.update({'saved_pcm_path': str(path), 'saved_pcm_file_sha256': sha(path)})
        lines.append(item)
    result = {k: request[k] for k in ('case_id', 'model', 'id', 'role', 'condition', 'seed', 'reference', 'input_float32_sha256')}
    result.update({'hypothesis': hypothesis, 'normalized_tokens': words(hypothesis), **edits(request['reference'], hypothesis),
                   'lines': lines, 'request_sha256': sha(request_path), 'worker_sha256': sha(__file__),
                   'native_library_sha256': sha(native._lib._name), 'native_api_version': native.get_version(),
                   'load_seconds': load_seconds, 'compute_seconds': elapsed, 'audio_seconds': len(signal)/16000,
                   'process_cpu_seconds': after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                   'voluntary_context_switches': after.ru_nvcsw - before.ru_nvcsw,
                   'involuntary_context_switches': after.ru_nivcsw - before.ru_nivcsw,
                   'system_load_average': os.getloadavg(), 'options': options, 'flags': 0,
                   'process_id': os.getpid(), 'isolation': 'One audio clip/condition in a fresh native process; no previous utterance or VAD state.'})
    with out.open('x') as output:
        output.write(json.dumps(result, indent=2) + '\n'); output.flush(); os.fsync(output.fileno())
    print('AUDIT_CLOSE_BEGIN', flush=True)
    native.close()
    print('AUDIT_CLOSE_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
