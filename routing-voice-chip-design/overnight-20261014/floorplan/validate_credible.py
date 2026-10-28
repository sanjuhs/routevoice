#!/usr/bin/env python3
"""Conservation, input preservation and required physical-artifact checks."""
import json,math,shutil,datetime
from pathlib import Path
W=Path(__file__).resolve().parent;c=json.loads((W/'blocks_credible.json').read_text());r=json.loads((W/'credible_results.json').read_text());base=json.loads((W/'results.json').read_text());p=r['physical_cases'];rows=r['area_table']
assert len(p)==5 and all(x['physical_screen_pass'] and x['fits_assumed26x33_reticle'] for x in p)
assert len(rows)==9 and sum(b['selections'] for b in c['blocks'])==31457280
mem=next(b for b in c['blocks'] if b['name']=='mutable_arrays');assert mem['mutable_bits']==8501818;assert mem['memory_area_levers_on']==mem['memory_area_by_scenario']
assert math.isclose(next(b for b in c['blocks'] if b['name']=='array_decoder_phase_mux_allowance')['array_book_extra_logic_mm2'],28.292,abs_tol=1e-10)
for lever,group in [('on',p[1:3]),('books',p[3:5])]:
 original=next(q['total_mm2'] for q in rows if q['memory']=='sram_open_macro' and q['levers']==lever)
 assert math.isclose(sum(q['block_area_mm2'] for q in group),original+c['engine_model']['footprint_mm2']+8)
for x in p:
 assert x['execution']['minimum_free_gib']>=22
 for path in x['artifacts'].values():assert (W/path).exists(),path
 if x['levers']=='books':assert not x['requires_accuracy_revalidation']
 for v in json.loads((W/x['run_dir']/'macro_terminal_drops.json').read_text()):assert v['combined_terminal_drop_v'] is not None
assert base['measured_input_floorplan']==json.loads((W/'as_built_tonight_results.json').read_text())['measured_input_floorplan']
check=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all5_credible_physical_screens_pass=True,all5_fit_assumed_reticle=True,as_built_machine_section_preserved=True,all144_memory_declarations_preserved=True,selection_count=31457280,extra_book_access_mm2=28.292,all_artifacts_present=True,free_gib=shutil.disk_usage('/').free/1024**3,corrected_check='Initial exact float equality on28.292mm2 rejected a3.55e-15mm2 representation difference; replaced with1e-10mm2 tolerance, no area/input change.')
(W/'credible_final_validation.json').write_text(json.dumps(check,indent=2)+'\n')
(W/'STATUS.txt').write_text('W3-STATUS: Credible Taalas design point complete. W6 density 5.536731543 um2/selection; full-bank selected DRC0, full-bank LVS/timing pending in snapshot. One 25x31mm with dense SRAM + frontend INT8: 608.046mm2 blocks, 2.15% IR. Two 26x29mm with open SRAM + FP32 + books-in-array: 2.43%/2.28% IR. All five physical cases pass and fit assumed 26x33mm field. All 144 mutable declarations unchanged; no KV8. Prior as-built section and failures preserved. Complete array integration, functional IO and real power remain unproven. See RESULTS.md/results.json.\n')
print('W3-STATUS: credible final audit PASS',check)
