"""Export existing full-bank native .ext through official Magic ext2spice."""
import argparse,gzip,hashlib,itertools,json,os,shutil,sys,threading
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'verification'))
from verify import PDK,run,tool
P=Path(__file__).resolve().parent
NATIVE=P.parent/'verification/r1280-v2'
p=argparse.ArgumentParser();p.add_argument('--run',default='fullbank-caps');p.add_argument('--gzip',action='store_true');a=p.parse_args()
o=P/a.run;assert o.parent==P
native_result=json.loads((NATIVE/'extract-process.json').read_text());assert native_result['returncode']==0 and native_result['status']=='finished',native_result
ext=NATIVE/'W6_PITCH_BANK_FLAT.ext';output=o/('extracted-cap.spice.gz' if a.gzip else 'extracted-cap.spice')
assert ext.exists() and not output.exists()
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
before=sha(ext);target=output.name;consumer=None;anchor=None;stream_hash=hashlib.sha256();stream_count=[0];errors=[]
if a.gzip:
 fifo=o/'extracted-cap.pipe';partial=o/'extracted-cap.spice.gz.part'
 assert not fifo.exists() and not partial.exists()
 os.mkfifo(fifo);anchor=os.open(fifo,os.O_RDWR|os.O_NONBLOCK);target=fifo.name
 def consume():
  try:
   with fifo.open('rb') as inp,gzip.open(partial,'wb',compresslevel=1) as dst:
    while block:=inp.read(1024*1024):
     assert shutil.disk_usage(P).free>22*2**30+2*1024*1024,'Disk floor reserve reached'
     stream_hash.update(block);stream_count[0]+=len(block);dst.write(block)
  except BaseException as e:errors.append(repr(e))
 consumer=threading.Thread(target=consume);consumer.start()
(o/'export-caps.tcl').write_text(f'ext2spice lvs\next2spice cthresh 0\next2spice -p {NATIVE} -o {target} W6_PITCH_BANK_FLAT\nquit -noprompt\n')
try:
 result=run([tool('magic'),'-dnull','-noconsole','-rcfile',str(PDK/'libs.tech/magic/gf180mcuD.magicrc'),'export-caps.tcl'],o,'export-caps',900)
finally:
 if anchor is not None:os.close(anchor)
 if consumer is not None:consumer.join(timeout=60)
if a.gzip:
 assert not consumer.is_alive() and not errors,errors
 assert result['returncode']==0 and stream_count[0]>0,result
 partial.rename(output);fifo.unlink()
assert result['returncode']==0 and output.exists(),result
assert sha(ext)==before,'Native extraction changed'
def devices(path):
 op=gzip.open if path.suffix=='.gz' else open
 with op(path,'rb') as f:
  yield from (l for l in f if l.startswith(b'X'))
count=0
original=NATIVE/'extracted.spice'
if not original.exists():original=NATIVE/'extracted.spice.gz'
for old,new in itertools.zip_longest(devices(original),devices(output)):
 assert old==new,('Device line changed during capacitance export',old,new)
 count+=1
decompressed=hashlib.sha256();size=0
with (gzip.open(output,'rb') if a.gzip else output.open('rb')) as f:
 while block:=f.read(8*1024*1024):decompressed.update(block);size+=len(block)
if a.gzip:assert decompressed.hexdigest()==stream_hash.hexdigest() and size==stream_count[0]
report=dict(**result,method='Official ext2spice lvs followed by cthresh0 on previously saved native .ext; no new geometry extraction.',native_ext_sha256=before,native_extraction_process_result=native_result,native_ext_path=str(ext),artifact=str(output),artifact_sha256=sha(output),bytes=output.stat().st_size,spice_uncompressed_sha256=decompressed.hexdigest(),uncompressed_bytes=size,device_lines=count,device_lines_byte_identical_to_lvs_export=True,
 native_ext_unchanged=True,producer_stream_sha256=stream_hash.hexdigest() if a.gzip else None,producer_uncompressed_bytes=stream_count[0] if a.gzip else None,gzip_roundtrip_stream_identity=True if a.gzip else None,
 compression='FIFO to one Python gzip thread; raw producer-stream SHA256 equals independently decompressed artifact SHA256; parent authorized2CPU bound' if a.gzip else None)
(o/'export-caps-result.json').write_text(json.dumps(report,indent=2)+'\n')
print('W6-STATUS: full-bank official capacitance export',report,flush=True)
