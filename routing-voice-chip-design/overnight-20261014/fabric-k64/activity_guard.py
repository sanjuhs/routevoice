from pathlib import Path
import subprocess,time,os,signal,json,shutil,sys
W=Path(__file__).resolve().parent;v=sys.argv[1];start=time.time()
f=W/'evidence'/f'{v}-activity-guard.json'
p=subprocess.Popen(['bash',str(W/'run_gate_activity.sh'),v],start_new_session=True,stdout=(W/'logs'/f'{v}-activity-guard.log').open('w'),stderr=subprocess.STDOUT)
reason=None
while p.poll() is None:
 free=shutil.disk_usage('/').free/2**30
 state={'pid':p.pid,'variant':v,'elapsed_s':time.time()-start,'free_gib':free,'status':'running','compile_threads':2,'simulation_threads':1,'time_limit_s':3600,'disk_guard_gib':22}
 t=f.with_suffix('.tmp');t.write_text(json.dumps(state,indent=2));t.replace(f)
 if free<22 or time.time()-start>3600:
  reason='disk headroom guard below22GiB' if free<22 else 'one-hour activity run guard'
  try:os.killpg(p.pid,signal.SIGTERM)
  except ProcessLookupError:pass
  try:p.wait(timeout=15)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  break
 time.sleep(2)
state.update(status='completed' if p.returncode==0 else 'failed_or_stopped',returncode=p.returncode,reason=reason,elapsed_s=time.time()-start)
t=f.with_suffix('.tmp');t.write_text(json.dumps(state,indent=2));t.replace(f);print(state)
