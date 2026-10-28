from pathlib import Path
import argparse,json,shutil,subprocess,time,xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent;R=W.parent.parents[1]
p=argparse.ArgumentParser();p.add_argument('--rows',type=int,required=True);p.add_argument('--which',choices=['assembly','timing-subbank'],required=True);a=p.parse_args()
O=W/f'r{a.rows}';g=json.loads((O/'geometry.json').read_text());key=a.which.replace('-','_')
assert shutil.disk_usage('/').free>=22*2**30
tool=shutil.which('klayout') or str(next(Path('/nix/store').glob('*klayout*/bin/klayout')))
cmd=[tool,'-b','-r',str(R/'experiments/taalas-access/main.drc')]
opts={'input':O/f'{a.which}.gds','report':O/f'{a.which}.lyrdb','topcell':g['tops'][key],'feol':'true','beol':'true','conn_drc':'true','offgrid':'true','metal_top':'11K','metal_level':'5LM','mim_option':'B','run_mode':'deep','thr':'2'}
for k,v in opts.items():cmd+=['-rd',f'{k}={v}']
(O/f'{a.which}-drc-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
t=time.monotonic()
with (O/f'{a.which}-drc.log').open('w') as f:r=subprocess.run(['nice','-n','10']+cmd,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
assert r.returncode==0
root=ET.parse(O/f'{a.which}.lyrdb').getroot();items=root.findall('./items/item');counts={}
for i in items:
 c=i.findtext('category');counts[c]=counts.get(c,0)+1
d={'gds_sha256':g['gds_sha256'][f'{a.which}.gds'],'markers':len(items),'categories':counts,'seconds':time.monotonic()-t,'scope':'GF180 FEOL BEOL connectivity offgrid; density/antenna excluded','threads':2}
(O/f'{a.which}-drc.json').write_text(json.dumps(d,indent=2)+'\n');print('W5-STATUS:',a.rows,a.which,'DRC',json.dumps(d),flush=True)
