#!/usr/bin/env python3
"""Preserve final completed DEF/netlist as lossless compact checkpoint artifacts."""
import argparse, gzip, hashlib, json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--state',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
w=Path(__file__).resolve().parents[1];state=Path(a.state);s=json.loads(state.read_text());records=[]
assert a.tag.replace('-','').isalnum()
for kind in ['def','nl']:
 source=Path(s[kind]);dest=w/'evidence'/(a.tag+('.def.gz' if kind=='def' else '.nl.v.gz'))
 assert source.is_file() and not dest.exists()
 h=hashlib.sha256()
 with source.open('rb') as src,gzip.open(dest,'wb',compresslevel=1) as out:
  for data in iter(lambda:src.read(1024**2),b''):h.update(data);out.write(data)
 records.append({'kind':kind,'source':str(source),'source_bytes':source.stat().st_size,'source_sha256':h.hexdigest(),
                 'gzip':dest.name,'gzip_bytes':dest.stat().st_size,'gzip_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
r={'scope':'Last completed physical checkpoint, not routed/signoff layout','state':str(state),'files':records}
(w/'evidence'/(a.tag+'-checkpoint.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
