#!/usr/bin/env python3
"""Run independent annotation-only processes within one 600-second budget."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('--lib', action='append', type=Path, required=True)
parser.add_argument('--macro-lib', type=Path, required=True)
parser.add_argument('--netlist', type=Path, required=True)
parser.add_argument('--top', default='rv_k64_projection_complete')
parser.add_argument('--clock-port', default='clk')
parser.add_argument('--vcd', action='append', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if hasattr(os, 'sched_getaffinity'):
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
sta = shutil.which('sta')
if not sta:
    raise SystemExit('OpenSTA executable not found in PATH')
script = Path(__file__).resolve().with_name('annotation_only.tcl')
args.output.mkdir(parents=True, exist_ok=False)
frozen_script = args.output / "annotation_only.tcl"
shutil.copyfile(script, frozen_script)
shutil.copyfile(Path(__file__).resolve(), args.output / "run_annotation_only.py")
script = frozen_script.resolve()

def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()

hashes = {str(path.resolve()): sha(path) for path in [*args.lib, args.macro_lib, args.netlist, script]}
version = subprocess.run([sta, '-version'], text=True, capture_output=True, timeout=20)
(args.output / 'sta-version.txt').write_text(version.stdout + version.stderr)
start = time.monotonic()
results = []
for vcd in args.vcd:
    output = args.output / vcd.stem
    output.mkdir()
    env = os.environ.copy()
    env.update(W8_LIB_LIST='\n'.join(str(p.resolve()) for p in args.lib),
               W8_MACRO_LIB=str(args.macro_lib.resolve()), W8_NETLIST=str(args.netlist.resolve()),
               W8_TOP=args.top, W8_CLOCK_PORT=args.clock_port, W8_VCD=str(vcd.resolve()), W8_OUT_DIR=str(output.resolve()))
    command = [sta, '-no_splash', '-exit', str(script)]
    (output / 'invocation.json').write_text(json.dumps({
        'command': command, 'environment': {key: value for key, value in env.items() if key.startswith('W8_')},
        'source_hashes': hashes, 'scope': 'tb/dut', 'SPEF_read': False, 'SDC_read': False,
        'cpu_affinity': sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
        'annotation_clock_period_ns': 20, 'entire_annotation_budget_seconds': 600}, indent=2) + '\n')
    begun = time.monotonic()
    timeout = max(0.001, 600 - (begun - start))
    timed_out = False
    with (output / 'opensta.log').open('w') as log:
        process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                returncode = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                returncode = process.wait()
    (output / 'exit.txt').write_text(str(returncode) + '\n')
    log_text = (output / 'opensta.log').read_text(errors='replace')
    result = {'vcd_path': str(vcd.resolve()), 'exit_code': returncode, 'timed_out': timed_out,
              'wall_seconds': time.monotonic() - begun, 'coverage': None,
              'scope': 'tb/dut', 'read_vcd_name_rewriting': False, 'power_reported': False,
              'timing_reported': False, 'design_stage': 'matching mapped synthesis netlist'}
    report = output / 'activity-annotation.rpt'
    errors = [line for line in log_text.splitlines() if re.match(r'^Error\b', line) or 'W8-ANNOTATION-ONLY: ERROR' in line]
    result['error_lines'] = errors
    if returncode == 0 and not timed_out and not errors and report.exists():
        categories = {}
        for line in report.read_text().splitlines():
            match = re.fullmatch(r'\s*([A-Za-z_][A-Za-z_ -]*)\s+(\d+)\s*', line)
            if match:
                categories[match[1].strip()] = int(match[2])
        if 'vcd' not in categories or 'unannotated' not in categories or not sum(categories.values()):
            result['parse_error'] = 'Unexpected native annotation report; inspect preserved raw report.'
        else:
            total = sum(categories.values())
            result['coverage'] = {'categories': categories, 'total_reported_pins': total,
                'direct_vcd_pins': categories['vcd'], 'direct_vcd_pin_fraction': categories['vcd'] / total,
                'meaning': 'Native OpenSTA activity-source pin counts, not switching coverage or power accuracy.'}
    results.append(result)
    (output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    if timed_out:
        break
summary = {'scope': 'annotation-only, mapped design, zero-delay unmodified VCD', 'results': results,
           'all_requested_checks_completed': len(results) == len(args.vcd) and all(r['coverage'] is not None for r in results),
           'wall_seconds': time.monotonic() - start, 'source_hashes': hashes,
           'power_W': None, 'routed_timing': None, 'SPEF_read': False,
           'limitations': ['Mapped activity coverage does not establish routed-netlist coverage.',
               'No SDF glitches, physical timing, or array internal energy established.']}
(args.output / 'results.json').write_text(json.dumps(summary, indent=2) + '\n')
