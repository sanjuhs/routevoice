from pathlib import Path
import sys,json,subprocess,shutil,time,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parent;R=B.parents[3];W=B/sys.argv[1];kind=sys.argv[2] if len(sys.argv)>2 else 'bank0'
assert shutil.disk_usage('/').free>=22*2**30
name='decoded-bank0' if kind=='bank0' else 'decoded-tile';top='RV_DECODED_BANK_00_0' if kind=='bank0' else 'RV_K64_DECODED_TILE_00'
cmd=['nice','-n','10','klayout','-b','-r',str(R/'experiments/taalas-access/main.drc')]
for key,value in dict(input=W/(name+'.gds'),report=W/(name+'.lyrdb'),topcell=top,feol='true',beol='true',conn_drc='true',offgrid='true',metal_top='11K',metal_level='5LM',mim_option='B',run_mode='deep',thr=2).items():cmd+=['-rd',f'{key}={value}']
(W/(name+'-command.json')).write_text(json.dumps(cmd,indent=2));start=time.monotonic()
with (W/(name+'-drc.log')).open('w') as f:r=subprocess.run(cmd,cwd=W,stdout=f,stderr=subprocess.STDOUT)
result={'returncode':r.returncode,'wall_seconds':time.monotonic()-start,'scope':'GF180 FEOL BEOL connectivity offgrid, deep2threads; excludes density/antenna'}
if r.returncode==0:
 root=ET.parse(W/(name+'.lyrdb')).getroot();items=root.findall('./items/item');cats={}
 for item in items:
  c=item.findtext('category');cats[c]=cats.get(c,0)+1
 result['drc_markers']=len(items);result['categories']=cats
(W/(name+'-checks.json')).write_text(json.dumps(result,indent=2));print(result,flush=True)
