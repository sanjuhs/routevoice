"""Preserve old pre-PNR reports compactly; never touch active ARRAY-PORT SDF views."""
from pathlib import Path
import gzip,json,hashlib,time
W=Path(__file__).resolve().parent
assert json.loads((W/'evidence/sc_rom-guard.json').read_text())['status']=='stopped'
manifest=W/'evidence/old-sta-archives.json';records=json.loads(manifest.read_text()) if manifest.exists() else []
freed=0
for v in ['array_port','sc_rom']:
 d=W/'runs'/f'{v}-v2/12-openroad-staprepnr'
 for p in sorted(d.rglob('*')):
  allowed=p.suffix in ['.rpt','.log'] or (v=='sc_rom' and p.suffix=='.sdf')
  if not p.is_file() or not allowed or p.stat().st_size<10_000_000:continue
  z=p.with_name(p.name+'.gz');assert not z.exists();before=p.stat();h=hashlib.sha256()
  with p.open('rb') as f,gzip.open(z,'wb',compresslevel=1) as g:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b);g.write(b)
  q=hashlib.sha256()
  with gzip.open(z,'rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):q.update(b)
  assert q.digest()==h.digest() and before.st_mtime_ns==p.stat().st_mtime_ns
  records.append({'path':str(p.relative_to(W)),'gzip':str(z.relative_to(W)),'bytes':before.st_size,'gzip_bytes':z.stat().st_size,'sha256_uncompressed':h.hexdigest(),'verified_lossless':True,'epoch':time.time()})
  p.unlink();freed+=before.st_size-z.stat().st_size
  manifest.write_text(json.dumps(records,indent=2)+'\n')
print('W2b-STATUS: Old pre-PNR reports archived losslessly; freed GiB',round(freed/2**30,3))
