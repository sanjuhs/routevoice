"""Bounded parent-authorized extension of this worker's extraction watchdog.

Stop only the identified Python watchdog; never stop/restart the Magic child.
Resume the parent when the child is a zombie so subprocess can reap native
status, or at the new absolute deadline so its original timeout can fire.
"""
from pathlib import Path
import argparse,datetime,hashlib,inspect,json,os,shutil,signal,subprocess,time
P=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--parent',type=int,required=True);p.add_argument('--child',type=int,required=True);a=p.parse_args()
o=P/'r1280-v2';receipt=o/'watchdog-extension.json';assert not receipt.exists()
def ps(pid):
 r=subprocess.run(['ps','-p',str(pid),'-o','pid=,ppid=,state=,etime=,command='],capture_output=True,text=True)
 return r.stdout.strip()
pa=ps(a.parent);ch=ps(a.child)
assert 'verification/verify.py extract' in pa and '--rows 1280 --run r1280-v2' in pa
cf=ch.split(None,4);assert int(cf[1])==a.parent and 'magicdnull' in cf[4]
cwd=subprocess.run(['lsof','-a','-p',str(a.child),'-d','cwd','-Fn'],capture_output=True,text=True,check=True).stdout
assert '\nn'+str(o.resolve())+'\n' in cwd,cwd
pf=pa.split(None,4);parts=[int(v) for v in pf[3].split(':')];elapsed=sum(v*60**i for i,v in enumerate(reversed(parts)))
assert elapsed<1800
deadline=time.monotonic()+3600-elapsed-2
source=inspect.getsource(subprocess.Popen._wait)
assert source.index('self._try_wait(os.WNOHANG)')<source.index('remaining = self._remaining_time(endtime)')
report=dict(authorization='Parent explicitly authorized safe SIGSTOP of owned Python watchdog only, external3600s absolute bound, then SIGCONT to reap native Magic status. User22GiB disk and<=4thread guards unchanged.',
 parent_pid=a.parent,child_pid=a.child,parent_process=pa,child_process=ch,child_cwd=cwd,
 original_timeout_seconds=1800,new_absolute_timeout_seconds=3600,elapsed_before_stop_seconds=elapsed,
 subprocess_wait_source_sha256=hashlib.sha256(source.encode()).hexdigest(),actions=[],minimum_free_gib=None)
def save(action):
 report['actions'].append(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),action=action))
 receipt.write_text(json.dumps(report,indent=2)+'\n')
stopped=False
try:
 save('Verified own watchdog and Magic child PIDs/cwd; extension prepared')
 os.kill(a.parent,signal.SIGSTOP);stopped=True;save('Sent SIGSTOP only to Python watchdog parent; Magic continues')
 while True:
  free=shutil.disk_usage(P).free/2**30
  report['minimum_free_gib']=free if report['minimum_free_gib'] is None else min(free,report['minimum_free_gib'])
  child=ps(a.child)
  if not child or 'Z' in child.split(None,4)[2]:
   save('Magic child exited; resume watchdog to reap native status');break
  assert int(child.split(None,4)[1])==a.parent and 'magicdnull' in child
  if free<22.2:
   os.kill(a.child,signal.SIGTERM);save('Disk reserve22.2GiB reached; sent SIGTERM to owned Magic child');break
  if time.monotonic()>=deadline:
   save('New absolute3600s bound reached; resume watchdog to enforce original timeout');break
  time.sleep(10)
finally:
 if stopped:
  os.kill(a.parent,signal.SIGCONT);save('Sent SIGCONT to watchdog; native status remains owned by original subprocess runner')
print('W6-STATUS: owned extraction watchdog extension completed; native result remains in extract-process.json',flush=True)
