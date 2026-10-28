from pathlib import Path
import json,subprocess,shutil,time,xml.etree.ElementTree as ET,hashlib
W=Path(__file__).resolve().parent;R=W.parents[3]
assert shutil.disk_usage('/').free>=22*2**30
cmd=['nice','-n','10','klayout','-b','-r',str(R/'experiments/taalas-access/main.drc')]
for key,value in dict(input=W/'partial-full-readout.gds',report=W/'full-readout.lyrdb',topcell='RV_K64_PARTIAL_READOUT_1280x320',feol='true',beol='true',conn_drc='true',offgrid='true',metal_top='11K',metal_level='5LM',mim_option='B',run_mode='deep',thr=2).items():cmd+=['-rd',f'{key}={value}']
(W/'drc-command.json').write_text(json.dumps(cmd,indent=2)+'\n');start=time.monotonic()
try:
 with (W/'drc.log').open('w') as f:r=subprocess.run(cmd,cwd=W,stdout=f,stderr=subprocess.STDOUT,timeout=420)
 status={'process_returncode':r.returncode,'wall_seconds':time.monotonic()-start,'hierarchical_run_mode':'deep','threads':2,'scope':'KLayout GF180 FEOL+BEOL+connectivity+offgrid; density/antenna excluded'}
 if r.returncode==0:
  root=ET.parse(W/'full-readout.lyrdb').getroot();items=root.findall('./items/item');cat={}
  for item in items:
   c=item.findtext('category');cat[c]=cat.get(c,0)+1
  status['drc_markers']=len(items);status['categories']=cat
except subprocess.TimeoutExpired:status={'status':'timeout_preserved','timeout_seconds':420,'wall_seconds':time.monotonic()-start}
(W/'drc-result.json').write_text(json.dumps(status,indent=2)+'\n');print(status,flush=True)
