import hashlib,json,tarfile
from pathlib import Path
W=Path(__file__).resolve().parent
files=set()
for tag in ['buf-v2','buf-v3','buf-v4']:
 d=W/'runs'/tag/'01-yosys-synthesis'
 assert (d/'state_out.json').exists()
 files.update(p for p in d.iterdir() if p.is_file())
for sub in ['rtl','tb','vectors','configs']:
 files.update(p for p in (W/sub).rglob('*') if p.is_file())
files.update(p for p in (W/'evidence').rglob('*') if p.is_file() and p.suffix not in ['.saif'])
files.update(p for p in W.iterdir() if p.is_file() and p.suffix in ['.py','.sh','.tcl','.md','.json'])
files.add(W/'logs/rtl-full-simulation.log');files.add(W/'logs/rtl-full-compile.log')
manifest=[]
for p in sorted(files):
 with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 manifest.append({'path':str(p.relative_to(W)),'bytes':p.stat().st_size,'sha256':h})
p=W/'synthesis-checkpoint-manifest.json';p.write_text(json.dumps(manifest,indent=2)+'\n');files.add(p)
target=W/'synthesis-checkpoint.tar.gz'
assert not target.exists()
with tarfile.open(target,'w:gz',compresslevel=3) as out:
 for p in sorted(files):out.add(p,arcname=str(p.relative_to(W)),recursive=False)
with target.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
r={'bytes':target.stat().st_size,'sha256':h,'files':len(files)}
(W/'synthesis-checkpoint-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
