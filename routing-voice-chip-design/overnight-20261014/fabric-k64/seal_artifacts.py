"""Refresh reproducibility manifests after the final report edits; no external writes."""
from pathlib import Path
import hashlib,json
W=Path(__file__).resolve().parent
def entry(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return {'path':str(p.relative_to(W)),'bytes':p.stat().st_size,'sha256':h.hexdigest()}
cloud=W/'evidence/cloud-inputs.json'
if cloud.exists():
 data=[entry(W/x['path']) for x in json.loads(cloud.read_text())]
 cloud.write_text(json.dumps(data,indent=2)+'\n')
 (W/'evidence/cloud-file-list.txt').write_text(''.join(x['path']+'\n' for x in data))
files=[]
for directory in ['rtl','hf','configs','vectors','tb']:
 files.extend(p for p in (W/directory).rglob('*') if p.is_file())
files.extend(p for p in W.iterdir() if p.is_file() and p.suffix in ['.py','.sh','.tcl','.md'])
if (W/'results.json').exists():files.append(W/'results.json')
files=sorted(set(files));data=[entry(p) for p in files]
(W/'evidence/reproduction-inputs.json').write_text(json.dumps(data,indent=2)+'\n')
(W/'evidence/reproduction-file-list.txt').write_text(''.join(x['path']+'\n' for x in data))
delivery=['RESULTS.md','results.json','CLOUD-REQUEST.md','ARRAY-CONTINUATION.md','evidence/array_port-placed.png','evidence/reproduction-inputs.json','evidence/cloud-inputs.json','evidence/array_port-v2-bounded-stop.json']
if all((W/p).exists() for p in delivery):
 (W/'evidence/final-delivery.json').write_text(json.dumps([entry(W/p) for p in delivery],indent=2)+'\n')
print('W2b-STATUS: Reproduction manifest sealed:',len(data),'source/config/vector/document files')
