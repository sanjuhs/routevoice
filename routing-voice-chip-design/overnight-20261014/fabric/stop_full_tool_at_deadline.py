#!/usr/bin/env python3
"""Allow LibreLane to flush routing logs shortly before the fixed full-ROM deadline."""
import json,os,signal,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
b=json.loads((r/'evidence/full-rom-physical-budget.json').read_text());deadline=b['start_unix']+b['remaining_physical_seconds']
run='rv_fixed_proj320_rom-route-util20-density35-noinflate-200ns'
while time.time()<deadline-12:time.sleep(min(5,max(.01,deadline-12-time.time())))
record={'reason':'Existing full-ROM time budget; stop leaf OpenROAD 12 seconds before supervisor deadline to permit LibreLane log buffer closure. This is not a tool-reported routing violation.','deadline_unix':deadline,'action_unix':time.time(),'run':run,'signals':[]}
for line in subprocess.check_output(['ps','-axo','pid,command'],text=True).splitlines():
 fields=line.strip().split(None,1)
 if len(fields)!=2:continue
 pid,command=fields
 if f'/runs/{run}/' in command and ('openroad -' in command or '.openroad-wrapped' in command):
  try:os.kill(int(pid),signal.SIGTERM);record['signals'].append({'pid':int(pid),'signal':'SIGTERM','command':command})
  except ProcessLookupError:pass
(r/'evidence/full-rom-time-limit-log-preservation.json').write_text(json.dumps(record,indent=2)+'\n')
print('W2-STATUS: Full-ROM deadline log-preservation action:',len(record['signals']),'tool processes stopped.',flush=True)
