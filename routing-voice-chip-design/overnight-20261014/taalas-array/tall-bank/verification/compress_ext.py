from pathlib import Path
import gzip,hashlib,json,shutil,os
P=Path(__file__).resolve().parent;O=P/'bank3-v1';src=O/'W5_TALL_BANK_FLAT.ext';dst=src.with_suffix('.ext.gz')
assert json.loads((O/'extract-process.json').read_text())['status']=='finished'
assert json.loads((O/'extract-process.json').read_text())['returncode']==0
assert src.exists() and not dst.exists()
def digest(file):
 h=hashlib.sha256()
 with file.open('rb') as f:
  for buf in iter(lambda:f.read(2**20),b''):h.update(buf)
 return h.hexdigest()
original_sha=digest(src);size=src.stat().st_size
with src.open('rb') as f,gzip.open(dst,'wb',compresslevel=6) as z:shutil.copyfileobj(f,z,2**20)
h=hashlib.sha256();count=0
with gzip.open(dst,'rb') as z:
 for buf in iter(lambda:z.read(2**20),b''):h.update(buf);count+=len(buf)
assert h.hexdigest()==original_sha and count==size
receipt=dict(original_path=src.name,original_sha256=original_sha,original_bytes=size,compressed_path=dst.name,compressed_sha256=digest(dst),compressed_bytes=dst.stat().st_size,decoded_bytes=count,decoded_sha256=h.hexdigest(),verified_lossless=True,reason='Free internal working space after successful Magic extraction; all LVS and capacitance SPICE files remain live.',restore_command='gzip -dc W5_TALL_BANK_FLAT.ext.gz > W5_TALL_BANK_FLAT.ext',restore_working_directory=str(O),original_removed_after_verification=True)
(O/'ext-compression-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');src.unlink();print(receipt,flush=True)
