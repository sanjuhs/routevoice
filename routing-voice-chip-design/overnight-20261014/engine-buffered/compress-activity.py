import gzip,shutil,json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent;p=W/'evidence/array_port-mapped-speech-w9-frozen.saif';out=p.with_suffix('.saif.gz')
assert not out.exists()
with p.open('rb') as src,out.open('wb') as raw:
 with gzip.GzipFile(filename='',mode='wb',compresslevel=3,fileobj=raw,mtime=0) as dst:shutil.copyfileobj(src,dst,1024*1024)
with out.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
r={'path':str(out),'bytes':out.stat().st_size,'sha256':h,'uncompressed_bytes':p.stat().st_size}
(W/'evidence/activity-compression.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
