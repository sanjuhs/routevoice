#!/usr/bin/env python3
"""Losslessly archive bulky views of the superseded pre-CTS views only."""
import hashlib,json,tarfile,time
from pathlib import Path
r=Path(__file__).resolve().parent
old=r/'runs/rv_fixed_proj64x320_rom-util30'
paths=sorted(p for d in old.iterdir() if d.is_dir() and d.name[:2].isdigit() and 1<=int(d.name[:2])<=22 for p in d.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix in {'.odb','.def','.v','.sdc'} and p.stat().st_size>1000000)
if not paths:raise SystemExit('No eligible files')
# Preserve synthesis/STA inputs used by the active continuation and all logs/reports.
archive=r/'evidence/pre-cts-views.tar.gz'
if archive.exists():raise SystemExit('Refusing to overwrite archive')
manifest={str(p.relative_to(r)):{'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'bytes':p.stat().st_size} for p in paths}
with tarfile.open(archive,'w:gz',compresslevel=1) as t:
 for p in paths:t.add(p,arcname=str(p.relative_to(r)),recursive=False)
with tarfile.open(archive,'r:gz') as t:
 for m in t:
  assert hashlib.file_digest(t.extractfile(m),'sha256').hexdigest()==manifest[m.name]['sha256'],m.name
receipt={'archive':str(archive.relative_to(r)),'verified_members':manifest,'archive_sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'restore_command':'tar -xzf evidence/pre-cts-views.tar.gz -C .','uncompressed_bytes':sum(v['bytes'] for v in manifest.values()),'archive_bytes':archive.stat().st_size}
(r/'evidence/pre-cts-views.json').write_text(json.dumps(receipt,indent=2)+'\n')
for p in paths:
 assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==manifest[str(p.relative_to(r))]['sha256']
 p.unlink()
print('W2-STATUS: Archived and SHA256-verified',len(paths),'superseded views;',receipt['uncompressed_bytes'],'bytes uncompressed;',receipt['archive_bytes'],'archive bytes')
