"""Preserve failed SC activity compiler outputs losslessly, with no pass credit."""
from pathlib import Path
import json,hashlib,tarfile,time,shutil
W=Path(__file__).resolve().parent
g=json.loads((W/'evidence/sc_rom-activity-guard.json').read_text())
assert g['status']=='failed_or_stopped' and g['returncode']!=0
d=W/'activity-sc_rom';files=sorted(p for p in d.rglob('*') if p.is_file())
archive=W/'evidence/sc_rom-activity-failed-build.tar.gz'
assert not archive.exists() and shutil.disk_usage('/').free>21*2**30
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
records=[{'path':str(p.relative_to(d)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
with tarfile.open(archive,'w:gz',compresslevel=1) as t:
 for p in files:t.add(p,arcname=str(p.relative_to(d)),recursive=False)
with tarfile.open(archive,'r:gz') as t:
 for rec in records:
  f=t.extractfile(rec['path']);h=hashlib.sha256()
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  assert h.hexdigest()==rec['sha256']
for p in files:p.unlink()
(W/'evidence/sc_rom-activity-failed-build-archive.json').write_text(json.dumps({'epoch':time.time(),'failed_attempt':True,'pass_credit':False,'guard':g,'archive':str(archive.relative_to(W)),'archive_sha256':sha(archive),'verified_lossless':True,'files':records},indent=2)+'\n')
print('W2b-STATUS: Failed SC activity compiler outputs preserved losslessly; no SAIF/pass produced.')
