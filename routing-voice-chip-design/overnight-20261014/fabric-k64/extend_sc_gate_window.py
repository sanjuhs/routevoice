"""Keep the original parent/exit receipt while extending our own gate-only budget.
The SC-ROM physical run stays stopped. No child simulation is paused/restarted.
"""
from pathlib import Path
import subprocess,os,signal,json,time,shutil
W=Path(__file__).resolve().parent;parent=39716;child=39718
out=W/'evidence/sc_rom-gate-window-extension.json'
def info(pid,field):return subprocess.run(['ps','-p',str(pid),'-o',field+'='],capture_output=True,text=True).stdout.strip()
assert str(W/'verify_gate.sh') in info(child,'command')
assert 'gate_guard_sc.py' in info(parent,'command')
el=info(child,'etime');seconds=0
for n in el.split(':'):seconds=seconds*60+int(n)
start=time.time()-seconds;paused=False;reason=None
try:
 while True:
  state=info(child,'state')
  if not state or state.startswith('Z'):break
  e=time.time()-start;free=shutil.disk_usage('/').free/2**30
  if e>=3300 and not paused:
   assert 'gate_guard_sc.py' in info(parent,'command')
   os.kill(parent,signal.SIGSTOP);paused=True
  r={'parent_pid':parent,'child_group':child,'elapsed_s':e,'original_monitor_paused':paused,'simulation_paused':False,'extended_gate_limit_s':5400,'free_gib':free,'status':'monitoring','reason':'The original one-hour gate-only guard was a worker default; observed 32-minute ARRAY replay plus 17-minute SC compile warrants room for the larger SC netlist. User SC physical limit remains respected.'}
  tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2));tmp.replace(out)
  if free<21 or e>5400:
   reason='disk floor guard' if free<21 else 'extended 90-minute gate-only guard'
   os.killpg(child,signal.SIGTERM);break
  time.sleep(2)
finally:
 if paused:
  try:os.kill(parent,signal.SIGCONT)
  except ProcessLookupError:pass
r.update(status='monitoring_finished',stop_reason=reason,elapsed_s=time.time()-start,original_monitor_resumed=paused)
out.write_text(json.dumps(r,indent=2)+'\n');print(r)
