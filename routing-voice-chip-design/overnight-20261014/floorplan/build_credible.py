#!/usr/bin/env python3
"""W6 measured geometry plus frozen W3 memory/engine ledger; no KV quantization."""
import json,hashlib,datetime,copy,math
from pathlib import Path
W=Path(__file__).resolve().parent;R=W.parent.parent
cfg=json.loads((W/'as_built_tonight_blocks.json').read_text())
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');snap=W/'inputs'/('pitch-'+stamp);snap.mkdir()
paths=['overnight-20261014/taalas-pitch/results.json','overnight-20261014/taalas-pitch/RESULTS.md','overnight-20261014/taalas-array/tall-bank/timing/results.json','overnight-20261014/fabric-k64/results.json'];hashes={};data={}
for s in paths:
 raw=(R/s).read_bytes();dest=snap/s;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);hashes[s]=dict(sha256=hashlib.sha256(raw).hexdigest(),snapshot=str(dest.relative_to(W)))
 if s.endswith('.json'):data[s]=json.loads(raw)
current_engine=data[paths[3]]['variants']['array_port'];current_foot=current_engine.get('routed_area_mm2') or current_engine['synthesis']['cell_area_mm2']/.5
assert math.isclose(current_foot,cfg['engine_model']['footprint_mm2']), 'W2b footprint changed: refresh engine model and rerun credible outlines before continuing'
pitch=data[paths[0]];density=pitch['area']['um2_per_selection_including_analog_readout'];verify={str(k):{q:v for q,v in d.items() if q!='geometry'} for k,d in pitch['layouts'].items()}
status=f"MEASURED GDS rectangle; full-bank DRC={verify['1280'].get('selected_drc')}, LVS={verify['1280'].get('lvs')};64-row DRC={verify['64'].get('selected_drc',{}).get('drc_markers')}; see pitch_verification for exact scope"
cfg.update(scope='Credible Taalas design-point conditional component floorplan; partial W6 macro, memory port mapping and whole-top power/timing unqualified',scenarios=dict(pitch1280v2=dict(selection_um2=density,periphery_factor=1,status=status)),selected_scenario='pitch1280v2',pitch_source_hashes=hashes,pitch_snapshot_utc=stamp,pitch_verification=verify,pitch_timing=pitch.get('timing'),pitch_missing=pitch.get('missing'),pitch_area_source=pitch['area'],levers_definition=dict(off='FP32 frontend, binary books, original mutable state',on='INT8 frontend + books_in_array; original mutable state; requires frontend accuracy re-validation',books='FP32 frontend + books_in_array; original mutable state; no numerical changes'))
cfg['source_hashes'].update(hashes)
for b in cfg['blocks']:
 if 'memory_area_levers_on' in b:b['memory_area_levers_on']=copy.deepcopy(b['memory_area_by_scenario'])
 if b['selections']:
  b['source']=paths[0]+'; frozen selection counts in W3 as-built ledger'
  b['area_status']='MEASURED W6 1280-row rectangle incl.readout; ASSUMED uniform density across model shapes/padding; qualification in pitch_verification'
 if b['name']=='array_decoder_phase_mux_allowance':
  b['array_book_extra_logic_mm2']=56.584*(cfg['books_bytes']*8/4)/31457280
  b['area_status']='ASSUMED transfer of 56.584mm2 October nonreceiver component subtotal (1.79876um2/selection). Not separately measured W5 integrated periphery. Receiver strips already in W6 rectangle; not added again.'
# Same dynamic activity assumptions; shrinking geometry is not evidence of reduced power.
cfg['pitch_policy']='Keep144-array inventory, ordinary registers, engines, dynamic logic and assumed watts unchanged. NoKV8 or codebook dedup. Books reserve7864320B; actualused7765892B not substituted without access/remapping proof.'
(W/'blocks_credible.json').write_text(json.dumps(cfg,indent=2)+'\n');(snap/'hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('W3-STATUS: W6 hash snapshot',stamp,'density',density,'um2/selection; mutable inventory unchanged; frontend INT8 is sole numerical lever')
