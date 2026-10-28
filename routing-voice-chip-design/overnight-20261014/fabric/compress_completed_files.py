#!/usr/bin/env python3
"""Hash-verified macOS transparent compression; paths/readable bytes unchanged."""
import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
r=Path(__file__).resolve().parent
allowed={'.sdf','.v','.def','.odb','.lib','.spef','.json','.rpt','.log','.gds','.lef'}
roots=[]
for run in (r/'runs').iterdir():
 receipt=r/'evidence'/f'{run.name}.supervisor.json'
 if receipt.exists() and json.loads(receipt.read_text()).get('exit_code') is not None:roots.append(run)
 else:roots.extend(p.parent for p in run.glob('*/state_out.json'))
if '--pdk' in sys.argv:roots.append(r/'pdks')
paths=set(p for base in roots for p in base.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix in allowed and p.stat().st_size>5_000_000 and not (p.stat().st_flags&32))
if '--activity-inputs' in sys.argv:
 for receipt in (r/'evidence').glob('*-activity.supervisor.json'):
  q=json.loads(receipt.read_text())
  if q.get('exit_code')!=0:continue
  source=r/'evidence'/receipt.name.replace('.supervisor.json','-input.json')
  if not source.exists():continue
  p=Path(json.loads(source.read_text())['vcd'])
  if p.is_file() and p.parent==r/'tmp' and not (p.stat().st_flags&32):paths.add(p)
if '--gate-executables' in sys.argv:
 commands=subprocess.check_output(['ps','-axo','command'],text=True)
 for p in (r/'tb').rglob('Vtb'):
  if p.is_file() and p.stat().st_mtime<time.time()-300 and str(p) not in commands and not (p.stat().st_flags&32):paths.add(p)
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
changes=[];before=shutil.disk_usage(r).free
for p in sorted(paths):
 h=digest(p);size=p.stat().st_size;blocks=p.stat().st_blocks*512;t=p.with_name(p.name+'.w2compressed')
 subprocess.run(['ditto','--hfsCompression',str(p),str(t)],check=True)
 assert t.stat().st_size==size and digest(t)==h and digest(p)==h
 info={'path':str(p.relative_to(r)),'sha256':h,'bytes':size,'before_allocated_bytes':blocks,'after_allocated_bytes':t.stat().st_blocks*512,'flags':t.stat().st_flags}
 os.replace(t,p);changes.append(info)
receipt={'unix':time.time(),'method':'ditto --hfsCompression, SHA256 verified before atomic replace; transparent POSIX reads retain identical bytes','free_before_bytes':before,'free_after_bytes':shutil.disk_usage(r).free,'changes':changes}
(r/'evidence'/f'transparent-compression-{int(time.time())}.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('W2-STATUS: Transparently compressed and hash-verified',len(changes),'completed files; free GiB',round(shutil.disk_usage(r).free/1024**3,2))
