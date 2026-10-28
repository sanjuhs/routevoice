"""Sequential lossless archival of the completed 64-row native extraction and four proof netlists."""
from pathlib import Path
import datetime,gzip,hashlib,json,os,shutil,subprocess,time
P=Path(__file__).resolve().parent;o=P/'r64-v2';names=['W6_PITCH_BANK_FLAT.ext','extracted.spice','canonical.spice','reference.spice','reference-wrong-width.spice'];receipt=o/'slice-evidence-compression.json'
assert not receipt.exists()
assert json.loads((o/'full-bank-netgen-result.json').read_text())['pass']
assert json.loads((o/'negative-width-netgen-result.json').read_text())['negative_control_rejected']
report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorization='Parent explicitly requested sequential archival of these five completed 64-row evidence files; process inventory confirmed no EDA jobs, and each file is checked for readers.',status='started',files=[],minimum_free_gib=None)
def save():receipt.write_text(json.dumps(report,indent=2)+'\n')
def reserve():
 free=shutil.disk_usage(o).free/2**30;report['minimum_free_gib']=free if report['minimum_free_gib'] is None else min(free,report['minimum_free_gib']);assert free>=22.01,free
def no_readers(raw,entry):
 result=subprocess.run(['lsof',str(raw)],capture_output=True,text=True)
 assert result.returncode==1 and not result.stdout.strip(),result.stdout
 entry.setdefault('reader_checks',[]).append(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
def digest(stream):
 h=hashlib.sha256();n=0
 while chunk:=stream.read(1024*1024):reserve();h.update(chunk);n+=len(chunk)
 return h.hexdigest(),n
save()
for name in names:
 raw=o/name;dest=o/(name+'.gz');assert raw.is_file() and not dest.exists();before=raw.stat();start=time.monotonic();e=dict(native=name,archive=dest.name,status='started',raw_removed=False);report['files'].append(e);save();reserve();no_readers(raw,e)
 h=hashlib.sha256();n=0
 with raw.open('rb') as source,dest.open('xb') as out:
  with gzip.GzipFile(filename='',mode='wb',fileobj=out,compresslevel=6,mtime=0) as z:
   while chunk:=source.read(1024*1024):reserve();h.update(chunk);n+=len(chunk);z.write(chunk)
  out.flush();os.fsync(out.fileno())
 e.update(native_sha256=h.hexdigest(),native_bytes=n,archive_bytes=dest.stat().st_size)
 with gzip.open(dest,'rb') as z:roundsha,roundbytes=digest(z)
 e.update(decompressed_sha256=roundsha,decompressed_bytes=roundbytes)
 assert roundsha==h.hexdigest() and roundbytes==n
 with dest.open('rb') as z:e['archive_sha256'],_=digest(z)
 now=raw.stat();assert (before.st_size,before.st_mtime_ns)==(now.st_size,now.st_mtime_ns)
 no_readers(raw,e);e['status']='verified_before_raw_removal';save();raw.unlink()
 e.update(status='complete',raw_removed=True,recovered_bytes=n-dest.stat().st_size,elapsed_seconds=time.monotonic()-start);save()
 print('W6-STATUS: verified archived '+name+' recovered '+str(e['recovered_bytes'])+' bytes',flush=True)
report.update(status='complete',recovered_bytes=sum(e['recovered_bytes'] for e in report['files']),reproduction='For each required file run gzip -dc NAME.gz > NAME in this directory, then verify SHA256 equals native_sha256 before rerunning compare/Netgen. Allocate native_bytes plus22GiB reserve; no regeneration of original extraction is required.')
save();print('W6-STATUS: five 64-row evidence archives complete',json.dumps(report),flush=True)
