#!/usr/bin/env python3
"""Optional one-CPU gzip copies; raw VCDs are never removed or modified."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('--vcd', action='append', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if hasattr(os, 'sched_getaffinity'):
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
args.output.mkdir(parents=True, exist_ok=False)
shutil.copyfile(Path(__file__).resolve(), args.output / 'compress_traces.py')
start = time.monotonic()
results = []
for source in args.vcd:
    target = source.with_suffix(source.suffix + '.gz')
    if target.exists():
        raise RuntimeError('Refusing to overwrite ' + str(target))
    before = source.stat()
    if shutil.disk_usage(source.parent).free < 9 * 2**30:
        raise RuntimeError('Insufficient guarded remote disk space')
    command = ['gzip', '-1', '-n', '-c', str(source)]
    stop_reason = None
    with target.open('xb') as output, (args.output / (source.stem + '-gzip.log')).open('w') as log:
        process = subprocess.Popen(command, stdout=output, stderr=log, start_new_session=True)
        while process.poll() is None:
            if time.monotonic() - start >= 600:
                stop_reason = 'Shared 600-second compression bound'
            if shutil.disk_usage(source.parent).free < 9 * 2**30:
                stop_reason = '9 GiB disk guard to preserve 8 GiB floor'
            if stop_reason:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                break
            time.sleep(1)
        code = process.wait()
    after = source.stat()
    receipt = {'source_path': str(source), 'gzip_path': str(target), 'command': command,
               'exit_code': code, 'stop_reason': stop_reason, 'gzip_bytes': target.stat().st_size,
               'source_unchanged_stat': (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
               'raw_source_retained': source.exists(), 'gzip_sha256': None,
               'decompressed_sha256': None, 'integrity_verified': False}
    if code == 0 and stop_reason is None:
        compressed_hash = hashlib.sha256()
        with target.open('rb') as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                compressed_hash.update(block)
        raw_hash = hashlib.sha256()
        with gzip.open(target, 'rb') as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                raw_hash.update(block)
        receipt.update(gzip_sha256=compressed_hash.hexdigest(), decompressed_sha256=raw_hash.hexdigest(),
                       integrity_verified=True)
    results.append(receipt)
    (args.output / (source.stem + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)
    if stop_reason:
        break
(args.output / 'results.json').write_text(json.dumps({'results': results,
    'wall_seconds': time.monotonic() - start, 'local_copy_size_limit_bytes': 200_000_000,
    'minimum_local_free_GiB_after_copy': 22.5,
    'raw_sources_preserved': True}, indent=2) + '\n')
