from pathlib import Path
import gzip,json,hashlib,time
W=Path(__file__).resolve().parent
m=W/'evidence/synthesis-archives.json';records=json.loads(m.read_text()) if m.exists() else []
for v in ['array_port','sc_rom']:
 d=W/'runs'/f'{v}-v2/06-yosys-synthesis'
 assert (d/'state_out.json').exists()
 for p in [d/'yosys-synthesis.log',d/f'rv_k64_{v}.nl.v.json']:
  if not p.exists():continue
  z=p.with_suffix(p.suffix+'.gz');h=hashlib.sha256();n=p.stat().st_size
  with p.open('rb') as f,gzip.open(z,'wb',compresslevel=1) as g:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b);g.write(b)
  q=hashlib.sha256()
  with gzip.open(z,'rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):q.update(b)
  assert h.digest()==q.digest()
  records.append({'path':str(p.relative_to(W)),'gzip':str(z.relative_to(W)),'bytes':n,'gzip_bytes':z.stat().st_size,'sha256_uncompressed':h.hexdigest(),'verified_lossless':True,'epoch':time.time()})
  p.unlink();m.write_text(json.dumps(records,indent=2)+'\n')
print('W2b-STATUS: Completed synthesis logs/JSON archived losslessly; raw gate netlists preserved.')
