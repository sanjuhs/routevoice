#!/usr/bin/env python3
"""Inventory unavailable checkpoint views without silently assuming they exist."""
import json
from pathlib import Path
r=Path(__file__).resolve().parent;missing={};states=0

def paths(x):
 if isinstance(x,str) and x.startswith('/'):yield Path(x)
 elif isinstance(x,dict):
  for k,v in x.items():
   if k!='metrics':yield from paths(v)
 elif isinstance(x,list):
  for v in x:yield from paths(v)
for s in (r/'runs').glob('*/*/state_out.json'):
 states+=1
 for p in paths(json.loads(s.read_text())):
  if not p.exists():missing.setdefault(str(p),[]).append(str(s.relative_to(r)))
markers={str(p.relative_to(r)):p.read_text().strip() for p in (r/'runs').glob('*/MOVED-TO-SSD.txt')}
out={'completed_state_files_checked':states,'missing_unique_paths':len(missing),'missing':missing,'external_archive_markers':markers,'own_lossless_archives':['evidence/superseded-placement-views.tar.gz','evidence/pre-cts-views.tar.gz'],'note':'Missing archived views must be restored into the internal workspace before checkpoint replay. Regeneration from original source/RTL is also supported. This audit does not move or modify any views.'}
(r/'evidence/checkpoint-path-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('W2-STATUS: checkpoint path audit',states,'states,',len(missing),'archived/unavailable unique paths')
