"""Transparent bounded extension of this worker's existing TT subprocess wait."""
from pathlib import Path
import argparse,datetime,hashlib,inspect,json,os,shutil,signal,subprocess,time
W=Path(__file__).resolve().parent;O=W/'r1280-g09-fullcontrol-guarded/typical-120ns-s32'
p=argparse.ArgumentParser();p.add_argument('--parent',type=int,required=True);p.add_argument('--child',type=int,required=True);a=p.parse_args();receipt=O/'watchdog-extension.json';assert not receipt.exists()
def ps(pid):return subprocess.run(['ps','-p',str(pid),'-o','pid=,ppid=,state=,etime=,command='],capture_output=True,text=True).stdout.strip()
pa=ps(a.parent);ch=ps(a.child);pf=pa.split(None,4);cf=ch.split(None,4)
assert 'timing/guarded_full_control_tt.py --directory r1280-g09-fullcontrol-guarded' in pa and 'T' not in pf[2]
assert int(cf[1])==a.parent and cf[4]=='ngspice -b test.cir'
cwd=subprocess.run(['/usr/sbin/lsof','-a','-p',str(a.child),'-d','cwd','-Fn'],capture_output=True,text=True,check=True).stdout;assert '\nn'+str(O.resolve())+'\n' in cwd
parts=[int(v) for v in pf[3].split(':')];elapsed=sum(v*60**i for i,v in enumerate(reversed(parts)));assert elapsed<1200
source=inspect.getsource(subprocess.Popen._wait);assert source.index('self._try_wait(os.WNOHANG)')<source.index('remaining = self._remaining_time(endtime)')
deadline=time.monotonic()+2400-elapsed-3
report={'authorization':'Parent explicitly authorized safe owned-watchdog extension to absolute2400s, preserving native TT circuit/tolerances/process. Stop only identified Python wait; resume on native exit or absolute bound. User22GiB disk floor unchanged.','parent_pid':a.parent,'child_pid':a.child,'parent_process':pa,'child_process':ch,'child_cwd':cwd,'original_timeout_seconds':1200,'new_absolute_timeout_seconds':2400,'elapsed_parent_before_stop_seconds':elapsed,'deadline_utc':datetime.datetime.fromtimestamp(time.time()+2400-elapsed-3,datetime.timezone.utc).isoformat(),'subprocess_wait_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'actions':[],'minimum_free_gib':None,'status':'prepared'}
def save(action):
 report['actions'].append({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'action':action});receipt.write_text(json.dumps(report,indent=2)+'\n')
def interrupted(signum,frame):raise RuntimeError(f'External guard interrupted by signal {signum}; restoring original wait')
signal.signal(signal.SIGTERM,interrupted);stopped=False
try:
 save('Validated owned parent/native child/cwd and wait-before-timeout implementation')
 os.kill(a.parent,signal.SIGSTOP);stopped=True;report['status']='guarding';save('SIGSTOP sent only to Python watchdog; original native TT process continues')
 while True:
  free=shutil.disk_usage(W).free/2**30;report['minimum_free_gib']=free if report['minimum_free_gib'] is None else min(free,report['minimum_free_gib']);child=ps(a.child)
  if not child or 'Z' in child.split(None,4)[2]:report['status']='native_exited';save('Native child exited; restoring parent to reap native result');break
  fields=child.split(None,4);assert int(fields[1])==a.parent and fields[4]=='ngspice -b test.cir'
  if free<22.2:
   os.kill(a.child,signal.SIGTERM);report['status']='disk_guard';save('22.2GiB reserve reached; SIGTERM sent only to owned native TT process');break
  if time.monotonic()>=deadline:
   report['status']='absolute_timeout';save('Absolute2400s bound reached; restore original expired wait to terminate/reap owned child');break
  time.sleep(2)
finally:
 if stopped:
  os.kill(a.parent,signal.SIGCONT);save('SIGCONT sent to original watchdog; original runner owns exit/status/trace analysis')
print('W6-STATUS: owned TT watchdog extension ended',report['status'],flush=True)
