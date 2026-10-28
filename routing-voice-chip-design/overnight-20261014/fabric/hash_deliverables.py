#!/usr/bin/env python3
"""Hash replay inputs, preserving the earlier manifest and checking frozen sources."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
out=r/'evidence/input-hashes.json';prior=r/'evidence/input-hashes.prior.json'
if out.exists() and not prior.exists():prior.write_bytes(out.read_bytes())
files=set()
for pattern in ['*.py','*.sh','*.tcl']:
 files.update(r.glob(pattern))
for folder in ['rtl','tb','configs','vectors']:
 files.update(p for p in (r/folder).rglob('*') if p.is_file())
files.update((r/'runs').glob('*/resolved.json'))
records={}
for p in sorted(files):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 records[str(p.relative_to(r))]={'sha256':h.hexdigest(),'bytes':p.stat().st_size}
old=json.loads(prior.read_text()) if prior.exists() else {}
protected=[k for k in old if k.startswith(('rtl/','tb/','vectors/')) and k in records]
changed=[k for k in protected if old[k]['sha256']!=records[k]['sha256']]
assert not changed, f'Previously hashed numerical source changed: {changed}'
out.write_text(json.dumps(records,indent=2)+'\n')
print(f'W2-STATUS: Hashed {len(records)} replay inputs; {len(protected)} previously recorded numerical sources unchanged.')
