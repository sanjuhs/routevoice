"""Bounded local process guard; controls only its own child process group."""
from pathlib import Path
import subprocess,time,os,signal,json,shutil,sys
W=Path(__file__).resolve().parent
variant=sys.argv[1];tag=sys.argv[2] if len(sys.argv)>2 else 'v1';start=time.time();limit=9000 if variant=='sc_rom' else 14400
prior=0
if tag!='v1':
 receipt=json.loads((W/'evidence'/f'{variant}-v1-manual-stop.json').read_text());prior=receipt['guard_snapshot']['elapsed_s']
log=(W/'logs'/f'{variant}-{tag}-flow.log').open('w')
p=subprocess.Popen(['bash',str(W/'run_flow.sh'),variant,tag],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
reason=None
while p.poll() is None:
 free=shutil.disk_usage('/').free
 state={'pid':p.pid,'variant':variant,'elapsed_s':time.time()-start+prior,'free_gib':free/2**30,'time_limit_s':limit,'status':'running'}
 (W/'evidence'/f'{variant}-guard.json').write_text(json.dumps(state,indent=2))
 if free<21*2**30:reason='disk safety guard below 21 GiB (20 GiB hard floor)'
 if time.time()-start+prior>limit:reason='bounded runtime limit'
 if reason:
  os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=15)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  break
 time.sleep(2)
state.update(status='stopped' if reason else 'completed',returncode=p.returncode,reason=reason,elapsed_s=time.time()-start+prior,free_gib=shutil.disk_usage('/').free/2**30)
(W/'evidence'/f'{variant}-guard.json').write_text(json.dumps(state,indent=2));log.close()
print(json.dumps(state))
