import gzip,hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;records=[]
for p in (r/'vectors').glob('*.vcd'):
    h=hashlib.sha256(p.read_bytes()).hexdigest();z=p.with_suffix('.vcd.gz')
    with p.open('rb') as src,gzip.open(z,'wb',compresslevel=1) as dst:shutil.copyfileobj(src,dst)
    with gzip.open(z,'rb') as src:assert hashlib.sha256(src.read()).hexdigest()==h
    records.append({'path':str(z.relative_to(r)),'sha256_uncompressed':h,'bytes_uncompressed':p.stat().st_size,'bytes_compressed':z.stat().st_size});p.unlink()
(r/'evidence/vcd-compression.json').write_text(json.dumps(records,indent=2)+'\n')
