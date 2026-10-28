"""Transparent APFS compression of completed activity evidence and executable."""
from pathlib import Path
import subprocess,hashlib,json,time,shutil
W=Path(__file__).resolve().parent
assert json.loads((W/'evidence/array_port-activity-guard.json').read_text())['returncode']==0
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
records=[]
for rel in ['evidence/array_port-mapped-speech.saif','activity-array_port/sim']:
 p=W/rel;before=p.stat();h=sha(p);tmp=W/'tmp'/('compressed-activity-'+p.name)
 assert not tmp.exists()
 if shutil.disk_usage('/').free<22.5*2**30:break
 subprocess.run(['nice','-n','10','ditto','--hfsCompression',str(p),str(tmp)],check=True)
 assert sha(tmp)==h and sha(p)==h
 if tmp.stat().st_blocks<before.st_blocks:tmp.replace(p)
 else:tmp.unlink()
 records.append({'path':rel,'sha256':h,'logical_bytes':before.st_size,'blocks_before':before.st_blocks,'blocks_after':p.stat().st_blocks,'exact_bytes_verified':True,'epoch':time.time()})
(W/'evidence/transparent-activity-compression.json').write_text(json.dumps(records,indent=2)+'\n')
print('W2b-STATUS: Completed activity paths and bytes preserved; GiB freed',sum((r['blocks_before']-r['blocks_after'])*512/2**30 for r in records))
