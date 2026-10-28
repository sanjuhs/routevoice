#!/usr/bin/env python3
"""Final inventory conservation, provenance, and physical-artifact audit."""
import datetime
import json
import math
import shutil
from pathlib import Path
W = Path(__file__).resolve().parent
c = json.loads((W / 'blocks_final.json').read_text())
r = json.loads((W / 'final_design_point.json').read_text())
base = json.loads((W / 'results.json').read_text())
old = json.loads((W / 'pre_lossless_results.json').read_text())
p = r['physical_cases']
assert len(p) == 4 and all(x['physical_screen_pass'] for x in p)
assert [x['fits_assumed26x33_reticle'] for x in p] == [False, True, True, True]
assert all(not x['requires_accuracy_revalidation'] for x in p)
assert sum(b['selections'] for b in c['blocks']) == 31457280
mem = next(b for b in c['blocks'] if b['name'] == 'mutable_arrays')
assert mem['mutable_bits'] == 8501818
assert next(b for b in c['blocks'] if b['name'] == 'frontend_native_int8_lossless')['rom_bytes'] == 2090240
assert c['frontend_native_int8_lossless']['fp32_multiply_add_resources'] == 1
assert json.loads((W / 'lossless_payload_audit.json').read_text())['total_bytes'] == 2090240
original = next(q['total_mm2'] for q in r['area_table'] if q['memory'] == 'sram_open_macro')
assert math.isclose(sum(q['block_area_mm2'] for q in p[2:]), original + c['engine_model']['footprint_mm2'] + 8)
for x in p:
    assert x['execution']['exit_code'] == 0 and x['execution']['minimum_free_gib'] >= 22
    for path in x['artifacts'].values():
        assert (W / path).is_file() and (W / path).stat().st_size > 0, path
    drops = json.loads((W / x['run_dir'] / 'macro_terminal_drops.json').read_text())
    assert len(drops) > 0 and all(v['combined_terminal_drop_v'] is not None for v in drops)
for key in ['measured_input_floorplan', 'credible_taalas_design_point']:
    if key in old:
        assert base[key] == old[key], key
assert all(q['unchanged'] for q in r['final_source_check'])
refresh = json.loads((W / 'final_input_refresh_audit.json').read_text())
assert all(not q['rerun_required'] for q in refresh['checks'])
free = shutil.disk_usage('/').free / 1024**3
assert free >= 22
check = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), all_four_physical_screens_pass=True,
             reticle_fits=[x['fits_assumed26x33_reticle'] for x in p], source_hashes_current=True,
             selections=31457280, mutable_bits=8501818, inventory_declarations=144,
             frontend_bytes=2090240, no_numerical_change=True, all_artifacts_present=True,
             earlier_machine_sections_preserved=True, free_gib=free,
             combined_ir_percent=[100*x['combined_worst_bound_v']/3.3 for x in p])
dest = W / 'final_validation.json'
if dest.exists() and not (W / 'pre_lossless_final_validation.json').exists():
    shutil.copyfile(dest, W / 'pre_lossless_final_validation.json')
dest.write_text(json.dumps(check, indent=2) + '\n')
(W / 'STATUS.txt').write_text('W3-STATUS: Final lossless frontend / measured bit-cell design point complete. '
    'Large open-bitcell macros: one 29x31 mm, misses assumed reticle. Smaller foundry cell: one 25x31 mm. '
    'Existing open SRAM: two 25x29 mm dies, no numerical change. All four abstract placement/PDN/IR screens PASS. '
    'Combined IR percentages: ' + ', '.join(f'{v:.2f}' for v in check['combined_ir_percent']) + '. '
    'State-reduction packing threshold 165220 B (161.35 KiB), not a physical lower bound. '
    'Full macro timing, functional IO and real power remain unproven. See RESULTS.md/results.json.\n')
print('W3-STATUS: final conservation/artifact audit PASS', json.dumps(check))
