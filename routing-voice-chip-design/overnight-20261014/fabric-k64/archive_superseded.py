"""Losslessly compress completed, superseded large views; never active state inputs.
Restore a historical run point with `gunzip path.gz` before using its state JSON.
"""
from pathlib import Path
import json,gzip,hashlib,os,time,sys
W=Path(__file__).resolve().parent
variant=sys.argv[1];run=W/'runs'/f'{variant}-v2'
steps=sorted(p for p in run.iterdir() if p.is_dir() and p.name[:2].isdigit())
protected=set()
def refs(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k!='metrics':refs(v)
 elif isinstance(x,list):
  for v in x:refs(v)
 elif isinstance(x,str):protected.add(x)
for step in steps[-3:]:
 for n in ['state_in.json','state_out.json']:
  p=step/n
  if p.exists():refs(json.loads(p.read_text()))
manifest=W/'evidence/superseded-archives.json';records=json.loads(manifest.read_text()) if manifest.exists() else []
freed=0
for step in steps[:-3]:
 if not (step/'state_out.json').exists() or int(step.name[:2])<=6:continue
 for p in step.rglob('*'):
  if not p.is_file() or str(p) in protected or p.suffix not in ['.v','.odb','.def','.sdf'] or p.stat().st_size<20_000_000:continue
  before=p.stat();h=hashlib.sha256();z=p.with_name(p.name+'.gz')
  if z.exists():continue
  with p.open('rb') as f,gzip.open(z,'wb',compresslevel=1) as g:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b);g.write(b)
  check=hashlib.sha256()
  with gzip.open(z,'rb') as g:
   for b in iter(lambda:g.read(1024*1024),b''):check.update(b)
  after=p.stat()
  assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  assert check.digest()==h.digest()
  records.append({'path':str(p.relative_to(W)),'gzip':str(z.relative_to(W)),'sha256_uncompressed':h.hexdigest(),'bytes':before.st_size,'gzip_bytes':z.stat().st_size,'verified_lossless':True,'time':time.time()})
  p.unlink();freed+=before.st_size-z.stat().st_size
  manifest.write_text(json.dumps(records,indent=2)+'\n')
print('Archived superseded views; freed GiB',round(freed/2**30,3))
