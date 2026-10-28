#!/usr/bin/env python3
"""Match literal VCD cell scopes to flattened gate-netlist instances.

This checks name presence, not OpenSTA annotation coverage. It reads no VCD
value changes and does not rewrite the trace or the netlist.
"""
import argparse
import collections
import hashlib
import json
import os
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--netlist', type=Path, required=True)
parser.add_argument('--vcd', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--cell-prefix', default='gf180mcu_fd_sc_mcu7t5v0__')
args = parser.parse_args()
if hasattr(os, 'sched_getaffinity'):
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
source = args.netlist.read_bytes()
pattern = re.compile(r'^\s*(' + re.escape(args.cell_prefix) + r'\w+)\s+(\\?\S+)\s*\(', re.M)
instances = {name.lstrip('\\'): cell for cell, name in pattern.findall(source.decode())}
if not instances:
    raise SystemExit('No matching standard-cell instances found; inspect netlist syntax.')
stack = []
matched = set()
family_count = collections.Counter()
pin_count = 0
samples = []
header_complete = False
with args.vcd.open('rb') as trace:
    for line in trace:
        tokens = line.split()
        if not tokens:
            continue
        if tokens[0] == b'$scope':
            stack.append(tokens[2].decode())
            name = stack[-1].lstrip('\\')
            if name in instances and name not in matched:
                matched.add(name)
                family_count[instances[name]] += 1
        elif tokens[0] == b'$upscope':
            stack.pop()
        elif tokens[0] == b'$var' and stack:
            name = stack[-1].lstrip('\\')
            if name in instances:
                pin_count += 1
                cell = instances[name]
                if len(samples) < 32 and (not samples or samples[-1]['instance'] == name or len({x['cell'] for x in samples}) < 8):
                    samples.append({'scope_literal': '/'.join(stack), 'instance': name,
                                    'cell': cell, 'pin_reference_literal': b' '.join(tokens[4:-1]).decode(),
                                    'width': int(tokens[2]), 'value_identifier': tokens[3].decode()})
        elif tokens[0] == b'$enddefinitions':
            header_complete = True
            break
result = {
    'netlist_path': str(args.netlist),
    'netlist_sha256': hashlib.sha256(source).hexdigest(),
    'vcd_path': str(args.vcd),
    'header_complete': header_complete,
    'standard_cell_instances_in_netlist': len(instances),
    'standard_cell_instances_with_exact_literal_leaf_scope': len(matched),
    'direct_variable_declarations_in_matched_leaf_scopes': pin_count,
    'matched_cell_types': dict(sorted(family_count.items())),
    'literal_pin_samples': samples,
    'name_normalization': 'Strip Verilog escape backslash only; no VCD rewrite or hierarchy remapping.',
    'OpenSTA_annotation_coverage_measured': False,
    'warning': 'Header instance and declaration counts are not timing-pin coverage or verified activity annotation.'
}
args.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('header_complete', 'standard_cell_instances_in_netlist',
    'standard_cell_instances_with_exact_literal_leaf_scope', 'direct_variable_declarations_in_matched_leaf_scopes')}))
