#!/usr/bin/env python3
"""Finish an interrupted Verilator build without regenerating its unchanged C++."""
import hashlib,json,os,re,shutil,signal,subprocess,sys,time
from pathlib import Path
r=Path(__file__).resolve().parent;v=sys.argv[1];path=r/'evidence'/f'{v}.gate-verification.json';old=json.loads(path.read_text());assert old.get('stop_reason') and not old.get('verification');backup=path.with_name(path.name+'.before-resume');assert not backup.exists();shutil.copy2(path,backup)
netlist=Path(old['netlist']);assert hashlib.sha256(netlist.read_bytes()).hexdigest()==old['netlist_sha256'];obj=r/'tb'/f'gate_obj_{v}';assert (obj/'Vtb.mk').exists()
receipt={k:old[k] for k in ['variant','level','netlist','netlist_sha256','clock_period_ns']};receipt.update(previous_attempt=str(backup.relative_to(r)),thread_caps={'build':2,'simulation':1},phases=[],minimum_free_gib=22.7);start=time.time();reason=None
for phase,args in [('compile',['make','-C',str(obj),'-f','Vtb.mk','-j','2']),('simulate',[str(obj/'Vtb')])]:
 if shutil.disk_usage(r).free<22.7*1024**3:reason='free disk below auxiliary 22.7 GiB margin';break
 log=r/'logs'/f'{v}.gate-resume-{phase}.log';entry={'phase':phase,'command':['nice','-n','10']+args,'log':str(log.relative_to(r))};receipt['phases'].append(entry)
 with log.open('w') as f:
  env=os.environ.copy();env.update(TMPDIR=str(r/'tmp'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
  p=subprocess.Popen(entry['command'],cwd=r,stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  try:
   while p.poll() is None:
    if shutil.disk_usage(r).free<22.7*1024**3:reason='free disk below auxiliary 22.7 GiB margin';break
    if time.time()-start>1200:reason='1200 second time bound';break
    time.sleep(3)
  except BaseException as e:reason=f'interrupted: {e}'
  if reason:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=15)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  entry['exit_code']=p.returncode
 if reason or p.returncode:break
 if phase=='simulate':
  m=re.search(r'VERIFICATION PASS vectors=(\d+) random=(\d+) checks=(\d+) failures=(\d+)',log.read_text())
  if m:receipt['verification']=dict(zip(['vectors_passed','random_vectors','exact_comparisons','failures'],map(int,m.groups())))
receipt.update(elapsed_seconds=time.time()-start,stop_reason=reason)
if (obj/'Vtb').exists():receipt['executable_sha256']=hashlib.sha256((obj/'Vtb').read_bytes()).hexdigest()
path.write_text(json.dumps(receipt,indent=2)+'\n');print('W2-STATUS: resumed gate check',json.dumps(receipt));raise SystemExit(0 if receipt.get('verification',{}).get('failures')==0 else 1)
