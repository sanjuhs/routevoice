#!/usr/bin/env python3
"""Restore the pinned model into this workspace, validating every byte stream."""
import hashlib,json,subprocess,tempfile,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];dest=ROOT/'models/artifacts';dest.mkdir(parents=True,exist_ok=True)
lock=json.loads((ROOT/'models/source.json').read_text())
for item in lock['files']:
    target=dest/item['path']
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'] and target.stat().st_size==item['bytes']:continue
    fd,tmp=tempfile.mkstemp(dir=dest);os.close(fd)
    try:
        subprocess.run(['curl','-4','-fL','--retry','3','--connect-timeout','20','--max-time','600',lock['artifact_base']+'/'+item['path'],'-o',tmp],check=True)
        data=Path(tmp).read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise RuntimeError('Artifact integrity failure: '+item['path'])
        os.replace(tmp,target)
    finally:
        if Path(tmp).exists():Path(tmp).unlink()
print('Verified all pinned Moonshine files')
