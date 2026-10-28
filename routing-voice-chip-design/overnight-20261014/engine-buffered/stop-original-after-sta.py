import os,signal,time,json,subprocess
from pathlib import Path
W=Path(__file__).resolve().parent
state=W/'runs/buf-v4/26-openroad-stamidpnr/state_out.json'
while not state.exists():time.sleep(10)
root=int((W/'evidence/flow-v4.pid').read_text());p=Path(f'/proc/{root}/cmdline')
if p.exists():
 assert b'run-flow-v4.sh' in p.read_bytes()
 rows=[tuple(map(int,l.split())) for l in subprocess.check_output(['ps','-eo','pid=,ppid='],text=True).splitlines()]
 owned={root}
 while True:
  expanded=owned|{pid for pid,ppid in rows if ppid in owned}
  if expanded==owned:break
  owned=expanded
 for pid in sorted(owned,reverse=True):
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 (W/'evidence/buf-v4-sta-completed-continuation.json').write_text(json.dumps({'completed_state':str(state),'stopped_owned_pids':sorted(owned),'reason':'Read-only STA completed; physical continuation already running from identical placed database.'},indent=2)+'\n')
print('W9-STATUS: original mid-PNR STA completed and original flow stopped; physical continuation owns later stages')
