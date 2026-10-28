#!/usr/bin/env python3
"""Preserve V2 tool logs at the original two-hour continuation deadline."""
import json,os,signal,subprocess,time
from datetime import datetime
from pathlib import Path
r=Path(__file__).resolve().parent
# Original supervisor PID79711 start verified using ps -p 79711 -o lstart=.
deadline=datetime.fromisoformat('2026-10-14T05:58:54+05:30').timestamp()+7200
record={'reason':'Original V2 continuation time budget; stop leaf OpenROAD 12 seconds before deadline so LibreLane closes its buffered log. Not a tool-reported routing violation.','deadline_unix':deadline,'start_time_source':'ps -p 79711 -o lstart= returned Wed Oct 14 05:58:54 2026, Asia/Kolkata.','signals':[]}
finished=False
while time.time()<deadline-12:
 p=r/'evidence/dp-signoff-thread-cap-continuation.json'
 if p.exists():
  q=json.loads(p.read_text())
  if 'continuation_returncode' in q or q.get('decision','').startswith('No successful'):
   finished=True;break
 time.sleep(min(5,max(.01,deadline-12-time.time())))
record['action_unix']=time.time();record['already_finished']=finished
if not finished:
 for line in subprocess.check_output(['ps','-axo','pid,command'],text=True).splitlines():
  fields=line.strip().split(None,1)
  if len(fields)!=2:continue
  pid,command=fields
  for tag in ['route200','postgrt-capped']:
   run='rv_fixed_proj320_dp-'+tag
   if f'/runs/{run}/' in command and ('openroad -' in command or '.openroad-wrapped' in command):
    try:os.kill(int(pid),signal.SIGTERM);record['signals'].append({'pid':int(pid),'signal':'SIGTERM','command':command});record['run']=run
    except ProcessLookupError:pass
(r/'evidence/dp-time-limit-log-preservation.json').write_text(json.dumps(record,indent=2)+'\n')
print('W2-STATUS: V2 deadline log-preservation controller ended; stopped',len(record['signals']),'tools.',flush=True)
