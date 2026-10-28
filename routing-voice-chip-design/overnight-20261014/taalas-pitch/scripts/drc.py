from pathlib import Path
import argparse,json,subprocess,os,shutil,xml.etree.ElementTree as ET
W=Path(__file__).resolve().parents[1];R=W.parents[1]
p=argparse.ArgumentParser();p.add_argument('directory');args=p.parse_args();O=W/args.directory
assert shutil.disk_usage('/').free>=22*2**30
geo=json.loads((O/'geometry.json').read_text());kl=str(next(Path('/nix/store').glob('*klayout*/bin/klayout')))
opts={'input':str(O/'bank.gds'),'report':str(O/'bank.lyrdb'),'topcell':geo['top'],'feol':'true','beol':'true','conn_drc':'true','offgrid':'true','metal_top':'11K','metal_level':'5LM','mim_option':'B','run_mode':'deep','thr':'1'}
cmd=[kl,'-b','-r',str(R/'experiments/taalas-access/main.drc')]
for key,value in opts.items():cmd+=['-rd',f'{key}={value}']
(O/'drc-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with (O/'drc.log').open('w') as f:res=subprocess.run(['nice','-n','10']+cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,timeout=1800,env=dict(os.environ,TMPDIR=str(W/'tmp')))
assert res.returncode==0,res.returncode
root=ET.parse(O/'bank.lyrdb').getroot();items=root.findall('./items/item');counts={}
for x in items:
 name=x.findtext('category');counts[name]=counts.get(name,0)+1
report={'drc_markers':len(items),'categories':counts,'scope':'selected GF180 FEOL BEOL connectivity off-grid; density and antenna excluded','gds_sha256':geo['gds_sha256'],'top':geo['top']}
(O/'drc-result.json').write_text(json.dumps(report,indent=2)+'\n');print('W6-STATUS:',args.directory,'selected DRC',json.dumps(report),flush=True)
