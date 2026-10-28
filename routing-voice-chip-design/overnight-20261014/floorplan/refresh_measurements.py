#!/usr/bin/env python3
import json,hashlib,shutil
from pathlib import Path
W=Path(__file__).resolve().parent
cfg=json.loads((W/'blocks.json').read_text()); evidence=[]
for worker in ['fabric','fabric-k64']:
 p=W.parent/worker/'results.json'
 if not p.exists(): evidence.append(dict(worker=worker,status='not yet available'));continue
 data=json.loads(p.read_text());digest=hashlib.sha256(p.read_bytes()).hexdigest();(W/'inputs').mkdir(exist_ok=True);dest=W/'inputs'/f'{worker}-{digest[:12]}.json';shutil.copy2(p,dest)
 candidates=[]
 for name,v in data.get('variants',{}).items():
  if v.get('um2_per_weight') is not None and v.get('weight_positions',0)>=102400:
   candidates.append(dict(name=name,um2_per_weight=v['um2_per_weight'],power_mw=v.get('power_mw'),weight_positions=v['weight_positions'],power_corner=v.get('power_corner')))
 evidence.append(dict(worker=worker,sha256=digest,snapshot=str(dest.relative_to(W)),candidates=candidates,status='measured values found' if candidates else 'No usable measured area/power; placeholders retained'))
 # Whole primitive footprint as conservative fabric envelope; datapath separately charged, explicitly overcounts.
 if candidates:
  v=max(candidates,key=lambda v:v['um2_per_weight']);cfg['scenarios']['stdcell'].update(selection_um2=v['um2_per_weight'],status=f'MEASURED primitive extrapolation from {worker}/{v["name"]}; contains some datapath, separately charged datapath makes this conservative; shape transfer unverified')
  if v['power_mw'] is not None and v.get('power_corner') and '3v30' in str(v['power_corner']):
   for b in cfg['blocks']:
    if 'fabric' in b['name']:
     b['power_w']=v['power_mw']/1000*b['selections']/v['weight_positions'];b['power_status']='W2 primitive linear power extrapolation at matching3.3V; activity/shape transfer unverified'
mem=W.parent/'synth/stat_mem.txt'
if mem.exists():shutil.copy2(mem,W/'inputs/stat_mem.txt')
cfg['measurement_evidence']=evidence;cfg['yosys_inventory_available']=mem.exists();(W/'blocks.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('W3-STATUS: refreshed sibling inputs:',json.dumps(evidence))
