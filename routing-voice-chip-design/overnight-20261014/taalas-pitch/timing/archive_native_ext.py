"""Lossless archival of idle native timing extraction intermediates."""
from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,os
W=Path(__file__).resolve().parent;records=[]
def readers(path):
 p=subprocess.run(['/usr/sbin/lsof','-F','pn','--',str(path)],capture_output=True,text=True)
 assert p.returncode in (0,1),p.stderr
 assert not p.stdout,('Live reader',p.stdout)
def digest(path,compressed=False):
 h=hashlib.sha256();n=0
 with (gzip.open(path,'rb') if compressed else path.open('rb')) as f:
  while b:=f.read(8*1024*1024):h.update(b);n+=len(b)
 return h.hexdigest(),n
for path in sorted(W.glob('r1280-g*/W6_TIMING_*.ext')):
 assert shutil.disk_usage('/').free>=22*2**30
 readers(path);target=path.with_suffix(path.suffix+'.gz');partial=target.with_suffix(target.suffix+'.part');assert not target.exists() and not partial.exists();before=digest(path)
 with path.open('rb') as src,gzip.open(partial,'wb',compresslevel=1) as dst:
  while b:=src.read(8*1024*1024):
   assert shutil.disk_usage('/').free>=22*2**30;dst.write(b)
 assert digest(partial,True)==before;assert digest(path)==before;readers(path);partial.rename(target)
 receipt={'original_path':str(path),'archive_path':str(target),'native_sha256':before[0],'native_bytes':before[1],'archive_sha256':digest(target)[0],'archive_bytes':target.stat().st_size,'roundtrip_sha256_and_bytes_match':True,'no_open_readers_before_and_after':True,'raw_removed_after_validation':True,'restoration':'Decompress this gzip to its original .ext name before re-exporting native extraction. Timing MOS/C/decks/traces untouched.'}
 path.unlink();path.with_suffix(path.suffix+'.archive.json').write_text(json.dumps(receipt,indent=2)+'\n');records.append(receipt)
(W/'native-extraction-archives.json').write_text(json.dumps(records,indent=2)+'\n');print('W6-STATUS: idle timing native extractions archived',len(records),'files; savedbytes',sum(x['native_bytes']-x['archive_bytes'] for x in records))
