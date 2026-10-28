"""Parent-authorized replacement of only our idle watchdog guard, if needed.

Preserves original stopped subprocess owner and live Magic child. Old guard
is stopped/killed before the replacement monitor loop begins; no EDA restart.
"""
from pathlib import Path
import argparse,datetime,json,os,shutil,signal,subprocess,time
P=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--parent',type=int,required=True);p.add_argument('--child',type=int,required=True);p.add_argument('--prior-guard',type=int,required=True);a=p.parse_args()
o=P/'r1280-v2';receipt=o/'watchdog-extension-5400.json';assert not receipt.exists()
def ps(pid):
 return subprocess.run(['ps','-p',str(pid),'-o','pid=,ppid=,state=,etime=,command='],capture_output=True,text=True).stdout.strip()
pa=ps(a.parent);ch=ps(a.child);old=ps(a.prior_guard)
assert 'verification/verify.py extract' in pa and '--rows 1280 --run r1280-v2' in pa and 'T' in pa.split(None,4)[2]
cf=ch.split(None,4);assert int(cf[1])==a.parent and 'magicdnull' in cf[4]
assert 'verification/extend_owned_wait.py' in old and f'--parent {a.parent} --child {a.child}' in old
cwd=subprocess.run(['lsof','-a','-p',str(a.child),'-d','cwd','-Fn'],capture_output=True,text=True,check=True).stdout
assert '\nn'+str(o.resolve())+'\n' in cwd
elapsed=sum(int(v)*60**i for i,v in enumerate(reversed(cf[3].split(':'))));assert 2950<=elapsed<3550
deadline=time.monotonic()+5400-elapsed-2
report=dict(authorization='Parent authorized transparent5400s absolute extension near50min only if one active guard preserves original native-exit and22GiB disk protections.',prior_receipt='watchdog-extension.json',prior_guard_pid=a.prior_guard,replacement_guard_pid=os.getpid(),parent_pid=a.parent,child_pid=a.child,parent_process=pa,child_process=ch,prior_guard_process=old,elapsed_before_handoff_seconds=elapsed,absolute_bound_seconds=5400,actions=[],minimum_free_gib=None)
def save(action):
 report['actions'].append(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),action=action))
 receipt.write_text(json.dumps(report,indent=2)+'\n')
owns=False
try:
 save('Verified existing stopped subprocess owner, live Magic child and old guard; prepared single-owner handoff')
 os.kill(a.prior_guard,signal.SIGSTOP);owns=True
 for _ in range(100):
  if 'T' in ps(a.prior_guard).split(None,4)[2]:break
  time.sleep(.01)
 else:raise AssertionError('Old guard did not reach stopped state')
 save('Stopped only old idle guard; original watchdog remains stopped and Magic remains running')
 os.kill(a.prior_guard,signal.SIGKILL)
 save('Killed only stopped old guard before entering replacement monitor; original source/receipt retained')
 while True:
  free=shutil.disk_usage(P).free/2**30
  report['minimum_free_gib']=free if report['minimum_free_gib'] is None else min(free,report['minimum_free_gib'])
  child=ps(a.child)
  if not child or 'Z' in child.split(None,4)[2]:
   save('Native Magic exited; resume original watchdog to reap native status');break
  assert int(child.split(None,4)[1])==a.parent and 'magicdnull' in child
  if free<22.2:
   os.kill(a.child,signal.SIGTERM);save('Disk reserve22.2GiB reached; SIGTERM only owned Magic child');break
  left=deadline-time.monotonic()
  if left<=0:
   save('Absolute5400s bound reached; resume original watchdog to enforce timeout');break
  time.sleep(min(5,left))
finally:
 if owns:
  try:os.kill(a.parent,signal.SIGCONT);save('Resumed original subprocess owner; no fabricated native exit status')
  except ProcessLookupError:save('Original subprocess owner already exited; consult its native result, no status invented')
print('W6-STATUS: owned5400s guard finished; native result belongs to original subprocess runner',flush=True)
