#!/usr/bin/env python3
"""Compare refreshed physical inputs against the immutable inputs of completed runs."""
import datetime
import json
from pathlib import Path
from area_models import configure

W = Path(__file__).resolve().parent
cfg = json.loads((W / 'blocks_final.json').read_text())
checks = []
keys = ['blocks', 'scenarios', 'memory_scenarios', 'engine_model', 'vdd',
        'sram_packing_overhead', 'binary_rom_um2_per_bit', 'binary_rom_periphery_factor',
        'macro_halo_um', 'maximum_tile_area_mm2', 'pad_current_budget_a', 'pad_current_margin']
for run in json.loads((W / 'final_runs.json').read_text()):
    old = json.loads((W / 'runs' / run['name'] / 'blocks_snapshot.json').read_text())
    new = configure(cfg, run['memory'], 'lossless')
    physical_changes = [k for k in keys if old[k] != new[k]]
    hash_changes = [k for k, v in cfg['final_source_hashes'].items()
                    if old['final_source_hashes'][k]['sha256'] != v['sha256']]
    checks.append(dict(run=run['name'], run_snapshot_utc=old['final_snapshot_utc'],
                       refreshed_snapshot_utc=cfg['final_snapshot_utc'],
                       changed_source_files=hash_changes, changed_physical_inputs=physical_changes,
                       rerun_required=bool(physical_changes)))
assert not any(c['rerun_required'] for c in checks), checks
result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), checks=checks,
              qualification='W6 timing/verification metadata refreshed; physical area, power, memory and engine inputs match all four completed runs. No EDA rerun required.')
(W / 'final_input_refresh_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print('W3-STATUS: refreshed source audit PASS; all four physical input sets unchanged')
