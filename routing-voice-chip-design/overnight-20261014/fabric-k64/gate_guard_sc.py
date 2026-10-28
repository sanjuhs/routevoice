from pathlib import Path
import os,signal,subprocess,time,json,shutil
W=Path(__file__).resolve().parent
v='sc_rom';net=W/'runs/sc_rom-v2/06-yosys-synthesis/rv_k64_sc_rom.nl.v'
p=subprocess.Popen(['bash',str(W/'verify_gate.sh'),v,str(net)],start_new_session=True,stdout=(W/'logs/sc_rom-gate-guard-output.log').open('w'),stderr=subprocess.STDOUT)
started=time.time();paused=False;reason=None
while p.poll() is None:
 costs=[]
 for variant in ['array_port','sc_rom']:
  try:g=json.loads((W/'evidence'/f'{variant}-guard.json').read_text())
  except (json.JSONDecodeError,FileNotFoundError):costs.append(3);continue
  if g['status']!='running':costs.append(0);continue
  ds=sorted(x.name for x in (W/'runs'/f'{variant}-v2').iterdir() if x.is_dir() and x.name[:2].isdigit())
  stage=ds[-1]
  costs.append(1 if 'yosys' in stage else 2 if 'sta' in stage else 3)
 want_pause=sum(costs)+2>6
 if want_pause!=paused:os.killpg(p.pid,signal.SIGSTOP if want_pause else signal.SIGCONT);paused=want_pause
 state={'pid':p.pid,'elapsed_s':time.time()-started,'paused_for_thread_budget':paused,'physical_worker_thread_budget':costs,'gate_threads':1,'status':'running'}
 (W/'evidence/sc_rom-gate-guard.json').write_text(json.dumps(state,indent=2))
 if shutil.disk_usage('/').free<21*2**30 or time.time()-started>5400:
  reason='disk or 90-minute gate replay guard';os.killpg(p.pid,signal.SIGCONT);os.killpg(p.pid,signal.SIGTERM);p.wait();break
 time.sleep(2)
state.update(status='completed' if p.returncode==0 else 'failed_or_stopped',returncode=p.returncode,reason=reason,elapsed_s=time.time()-started)
(W/'evidence/sc_rom-gate-guard.json').write_text(json.dumps(state,indent=2));print(state)
