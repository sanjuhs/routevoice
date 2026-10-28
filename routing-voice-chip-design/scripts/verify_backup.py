#!/usr/bin/env python3
"""Verify remote archive hashes without re-downloading multi-GB backup files."""
import argparse
import json
import socket
from pathlib import Path
import urllib3.util.connection
from huggingface_hub import HfApi

p=argparse.ArgumentParser();p.add_argument('--ipv4',action='store_true');a=p.parse_args()
if a.ipv4:urllib3.util.connection.allowed_gai_family=lambda:socket.AF_INET
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'reports/backup-manifest.json').read_text())
api=HfApi();info=api.repo_info('sanjuhs/route-voice-hardware-backup',repo_type='dataset',files_metadata=True)
files={s.rfilename:s for s in info.siblings}
checks=[]
for record in manifest:
    key='2026-09-06-pre-routing/'+record['file']
    f=files.get(key)
    if f is None:raise RuntimeError('Missing remote file: '+key)
    if f.size != record['bytes']:raise RuntimeError('Remote size mismatch: '+key)
    if f.lfs:
        remote=f.lfs.sha256
    else:
        from huggingface_hub import hf_hub_download
        import hashlib
        local=hf_hub_download(info.id,key,repo_type='dataset',revision=info.sha)
        remote=hashlib.sha256(Path(local).read_bytes()).hexdigest()
    if remote!=record['sha256']:raise RuntimeError('Remote SHA256 mismatch: '+key)
    checks.append({'file':key,'bytes':f.size,'sha256':remote})
p=root/'reports/backup-status.json';status=json.loads(p.read_text());status.update(huggingface_upload='verified',huggingface_commit=info.sha,huggingface_files=checks)
p.write_text(json.dumps(status,indent=2)+'\n');print(json.dumps({'status':'verified','commit':info.sha,'files':len(checks)}))
