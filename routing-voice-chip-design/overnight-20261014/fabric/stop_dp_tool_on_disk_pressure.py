#!/usr/bin/env python3
"""Preserve buffered logs before the existing 22GiB group-stop guard triggers."""
import json,os,shutil,signal,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;threshold=22.35
record={'reason':'Disk headroom approaching the existing 22 GiB supervisor guard. Stop leaf OpenROAD below 22.35 GiB to allow LibreLane to flush routing logs; not a tool-reported routing violation.','threshold_free_gib':threshold,'signals':[]}
finished=False
while True:
 free=shutil.disk_usage(r).free
 qfile=r/'evidence/dp-signoff-thread-cap-continuation.json'
 if qfile.exists():
  q=json.loads(qfile.read_text())
  if 'continuation_returncode' in q or q.get('decision','').startswith('No successful'):finished=True;break
 if free<threshold*1024**3:break
 time.sleep(1)
record.update(action_unix=time.time(),free_bytes=free,already_finished=finished)
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
(r/'evidence/dp-disk-limit-log-preservation.json').write_text(json.dumps(record,indent=2)+'\n')
print('W2-STATUS: V2 disk log-preservation controller ended; stopped',len(record['signals']),'tools; free GiB',round(free/1024**3,3),flush=True)
