"""Archive completed compiler outputs; preserve executable and all evidence."""
from pathlib import Path
import json,hashlib,tarfile,sys,time
W=Path(__file__).resolve().parent;v=sys.argv[1];kind='activity' if '--activity' in sys.argv else 'gate'
if kind=='gate':
 r=json.loads((W/'evidence/gate-correctness.json').read_text());passed=r[v]['status']=='pass'
else:
 r=json.loads((W/'evidence'/f'{v}-activity-guard.json').read_text());passed=r.get('returncode')==0 and 'PASS gate_activity vectors=1 outputs=320' in (W/'logs'/f'{v}-activity-simulation.log').read_text()
if not passed:
 assert '--completed-compile' in sys.argv
 log=(W/'logs'/f'{v}-{kind}-compile.log').read_text()
 assert '- Verilator: Built from ' in log and '- Verilator: Walltime ' in log
d=W/f'{kind}-{v}';files=sorted(p for p in d.rglob('*') if p.is_file())
archive=W/'evidence'/f'{v}-{kind}-build.tar.gz';assert not archive.exists()
records=[{'path':str(p.relative_to(d)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
with tarfile.open(archive,'w:gz',compresslevel=1) as t:
 for p in files:t.add(p,arcname=str(p.relative_to(d)),recursive=False)
with tarfile.open(archive,'r:gz') as t:
 for rec in records:
  f=t.extractfile(rec['path']);h=hashlib.sha256()
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  assert h.hexdigest()==rec['sha256']
for p in files:
 if p.name!='sim':p.unlink()
(W/'evidence'/f'{v}-{kind}-build-archive.json').write_text(json.dumps({'epoch':time.time(),'kind':kind,'archive':str(archive.relative_to(W)),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'verified_lossless':True,'functional_pass_at_archive':passed,'preserved_executable':str((d/'sim').relative_to(W)),'files':records},indent=2)+'\n')
print('W2b-STATUS: Completed gate build archived losslessly; executable preserved:',v)
