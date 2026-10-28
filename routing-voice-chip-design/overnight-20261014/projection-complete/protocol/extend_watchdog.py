from pathlib import Path
import os,signal,time,subprocess,json
W=Path(__file__).resolve().parent;D=W/'ss-120ns'; parent=80495;child=80571
for pid,needle in [(parent,'protocol/run.py'),(child,'ngspice -b test.cir')]:
 text=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True);assert needle in text,(pid,text)
start=(D/'ngspice.log').stat().st_birthtime;deadline=start+720
record={'parent_authorization':'Parent message: safely extend existing watchdog to720s without restarting native job,2026-10-14','method':'Suspend only Python waiting launcher; independent supervisor enforces720s from log birth before ngspice launch. Resume after child becomes zombie/exits; CPython3.12 _wait checks waitpid before timeout. Native simulation is not restarted or suspended.','launcher_pid':parent,'ngspice_pid':child,'original_limit_seconds':480,'new_limit_seconds':720,'guard_start_epoch':start,'extension_epoch':time.time(),'deadline_epoch':deadline}
(D/'watchdog-extension.json').write_text(json.dumps(record,indent=2));os.kill(parent,signal.SIGSTOP)
try:
 while True:
  p=subprocess.run(['ps','-p',str(child),'-o','state='],capture_output=True,text=True)
  if p.returncode!=0 or p.stdout.strip().startswith('Z'):record['outcome']='native child completed';break
  if time.time()>=deadline:
   os.kill(child,signal.SIGKILL);record['outcome']='native child killed at720s bounded deadline';break
  time.sleep(2)
finally:
 os.kill(parent,signal.SIGCONT);record['supervisor_completed_epoch']=time.time();(D/'watchdog-extension.json').write_text(json.dumps(record,indent=2));print(record['outcome'],flush=True)
