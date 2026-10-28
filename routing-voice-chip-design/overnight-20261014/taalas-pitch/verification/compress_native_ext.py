"""Archive exactly the completed native full-bank .ext after verified roundtrip."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,shutil,subprocess,time
P=Path(__file__).resolve().parent;o=P/'r1280-v2';raw=o/'W6_PITCH_BANK_FLAT.ext';dest=raw.with_suffix('.ext.gz');receipt=o/'native-ext-compression.json'
expected='73b3502c7294f325537d86a8b62a5b94ae75d93224c933e23dffc143c00c3717'
assert raw.is_file() and not dest.exists() and not receipt.exists()
assert json.loads((o/'extract-process.json').read_text())['returncode']==0
start=time.monotonic();before=raw.stat();report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorization='Parent requested only this .ext archive; timing confirmed no current or planned readers.',native_path=str(raw),archive_path=str(dest),expected_native_sha256=expected,status='started',raw_removed=False,minimum_free_gib=None)
def save():receipt.write_text(json.dumps(report,indent=2)+'\n')
def reserve():
 free=shutil.disk_usage(o).free/2**30;report['minimum_free_gib']=free if report['minimum_free_gib'] is None else min(free,report['minimum_free_gib']);assert free>=22.2,free
def no_readers():
 result=subprocess.run(['lsof',str(raw)],capture_output=True,text=True)
 assert result.returncode==1 and not result.stdout.strip(),result.stdout
 report.setdefault('reader_checks',[]).append(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
def digest(stream):
 h=hashlib.sha256();n=0
 while chunk:=stream.read(4*1024*1024):reserve();h.update(chunk);n+=len(chunk)
 return h.hexdigest(),n
save();reserve();no_readers();h=hashlib.sha256();n=0
with raw.open('rb') as source,dest.open('xb') as out:
 with gzip.GzipFile(filename='',mode='wb',fileobj=out,compresslevel=6,mtime=0) as z:
  while chunk:=source.read(4*1024*1024):reserve();h.update(chunk);n+=len(chunk);z.write(chunk)
 out.flush();os.fsync(out.fileno())
report.update(source_sha256=h.hexdigest(),native_bytes=n,archive_bytes=dest.stat().st_size)
assert h.hexdigest()==expected
with gzip.open(dest,'rb') as z:roundsha,roundbytes=digest(z)
report.update(decompressed_sha256=roundsha,decompressed_bytes=roundbytes)
assert roundsha==expected and roundbytes==n
with dest.open('rb') as z:report['archive_sha256'],_=digest(z)
now=raw.stat();assert (before.st_size,before.st_mtime_ns)==(now.st_size,now.st_mtime_ns)
no_readers();report['status']='verified_before_raw_removal';save()
raw.unlink();report.update(status='complete',raw_removed=True,recovered_bytes=n-dest.stat().st_size,elapsed_seconds=time.monotonic()-start,reproduction='Restore losslessly with gzip -dc W6_PITCH_BANK_FLAT.ext.gz > W6_PITCH_BANK_FLAT.ext, then verify SHA256 matches expected_native_sha256 before using ext2spice. Allocate at least native_bytes plus the22GiB reserve before restoration.')
save();print('W6-STATUS: native .ext losslessly archived, roundtrip SHA256 verified',json.dumps(report),flush=True)
