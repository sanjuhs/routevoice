"""Historical, withdrawn controller. Original proposal four-hour cap applies."""
raise SystemExit('Do not run: extension withdrawn before effect; preserve the approved 14400s physical cap.')
from pathlib import Path
import subprocess,os,signal,json,time,shutil
W=Path(__file__).resolve().parent
f=W/'evidence/array_port-guard.json';out=W/'evidence/array_port-window-extension.json'
for attempt in range(10):
 try:g=json.loads(f.read_text());break
 except json.JSONDecodeError:time.sleep(.02)
assert g['status']=='running';child=g['pid']
def info(pid,field):return subprocess.run(['ps','-p',str(pid),'-o',field+'='],capture_output=True,text=True).stdout.strip()
parent=int(info(child,'ppid'));assert 'fabric-k64/supervise.py array_port v2' in info(parent,'command')
start=time.time()-g['elapsed_s'];paused=False;reason=None
try:
 while True:
  state=info(child,'state')
  if not state or state.startswith('Z'):break
  assert int(info(child,'ppid'))==parent
  e=time.time()-start;free=shutil.disk_usage('/').free/2**30
  if e>=14100 and not paused:
   assert 'fabric-k64/supervise.py array_port v2' in info(parent,'command')
   os.kill(parent,signal.SIGSTOP);paused=True
  r={'parent_pid':parent,'child_group':child,'elapsed_s_including_v1':e,'original_monitor_paused':paused,'eda_paused':False,'extended_array_limit_s':21600,'free_gib':free,'disk_guard_gib':21,'status':'monitoring','reason':'Four hours was a worker default, not the user SC-ROM budget. Continue ARRAY-PORT within the authorized overnight run; retain disk and thread limits. SC-ROM physical remains stopped.'}
  t=out.with_suffix('.tmp');t.write_text(json.dumps(r,indent=2));t.replace(out)
  if free<21 or e>21600:
   reason='disk floor guard' if free<21 else 'six-hour cumulative overnight ARRAY bound'
   try:os.killpg(child,signal.SIGTERM)
   except ProcessLookupError:pass
   break
  time.sleep(2)
finally:
 if paused:
  try:os.kill(parent,signal.SIGCONT)
  except ProcessLookupError:pass
r.update(status='monitoring_finished',stop_reason=reason,elapsed_s_including_v1=time.time()-start,original_monitor_resumed=paused)
out.write_text(json.dumps(r,indent=2)+'\n');print(r)
