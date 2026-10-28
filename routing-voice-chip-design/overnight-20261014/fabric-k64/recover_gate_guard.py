"""Monitor an already-running gate process after a status-file reader race.
An adopted process's OS exit status is not available; report that explicitly.
"""
from pathlib import Path
import os,signal,subprocess,time,json,shutil,sys,re
W=Path(__file__).resolve().parent;v=sys.argv[1]
f=W/'evidence'/('gate-guard.json' if v=='array_port' else 'sc_rom-gate-guard.json')
g=json.loads(f.read_text());pid=g['pid']
receipt=W/'evidence'/f'{v}-gate-monitor-recovery.json'
receipt.write_text(json.dumps({'prior_guard':g,'reason':'Monitor JSONDecodeError from non-atomic physical-status write; child simulation remained active. Adopted monitoring preserves that run.','recovered_epoch':time.time(),'os_exit_status_available':False},indent=2)+'\n')
def elapsed():
 s=subprocess.run(['ps','-p',str(pid),'-o','etime='],capture_output=True,text=True).stdout.strip()
 if not s:return None
 days=0
 if '-' in s:d,s=s.split('-');days=int(d)
 vals=list(map(int,s.split(':')));sec=0
 for n in vals:sec=sec*60+n
 return days*86400+sec
base=elapsed();assert base is not None
start=time.time()-base;reason=None
while True:
 command=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True).stdout
 if str(W/'verify_gate.sh') not in command:break
 e=time.time()-start;free=shutil.disk_usage('/').free/2**30
 state={'pid':pid,'elapsed_s':e,'free_gib':free,'status':'running','adopted_after_monitor_failure':True,'os_exit_status_available':False,'gate_threads':1}
 t=f.with_suffix('.tmp');t.write_text(json.dumps(state,indent=2));t.replace(f)
 if free<21 or e>3600:
  reason='disk guard below 21 GiB' if free<21 else 'one-hour total gate replay guard'
  try:os.killpg(pid,signal.SIGCONT);os.killpg(pid,signal.SIGTERM)
  except ProcessLookupError:pass
  break
 time.sleep(2)
log=W/'logs'/f'{v}-gate-simulation.log';s=log.read_text() if log.exists() else ''
normal='PASS gate vectors=54 outputs=17280' in s and 'Verilog $finish' in s and '- Verilator: cpu ' in s
state.update(status='functional_completion_observed' if normal and reason is None else 'failed_or_stopped',reason=reason,returncode=None,normal_finish_in_log=normal,elapsed_s=time.time()-start)
t=f.with_suffix('.tmp');t.write_text(json.dumps(state,indent=2));t.replace(f);print(state)
