#!/usr/bin/env python3
import datetime,json,shutil,subprocess,sys,time
from pathlib import Path
r=Path(__file__).resolve().parent;run=r/'runs'/sys.argv[1];tail_bytes=160 if '--brief' in sys.argv else 1400
steps=sorted(p for p in run.iterdir() if p.is_dir() and p.name[:2].isdigit())
states=sorted(run.glob('*/state_out.json'))
print(datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'free GiB',round(shutil.disk_usage(r).free/1024**3,2))
if steps:
 p=steps[-1];stamp=getattr(p.stat(),'st_birthtime',p.stat().st_mtime)
 print('Latest step:',p.name,'created minutes ago:',round((time.time()-stamp)/60,1))
 log=p/(p.name[3:]+'.log')
 if log.exists():
  print('Step log bytes:',log.stat().st_size)
  with log.open('rb') as f:f.seek(max(0,log.stat().st_size-tail_bytes));print(f.read().decode(errors='replace'))
print('Last completed:',states[-1].parent.name if states else None)

receipt=r/'evidence'/f'{run.name}.supervisor.json'
if receipt.exists():
 d=json.loads(receipt.read_text());print('SUPERVISOR ENDED:',d.get('exit_code'),d.get('stop_reason'),'elapsed seconds',d.get('elapsed_seconds'))

processes=[]
for line in subprocess.check_output(['ps','-axo','pid,etime,%cpu,rss,command'],text=True).splitlines()[1:]:
 fields=line.strip().split(maxsplit=4)
 if len(fields)==5 and str(run.resolve())+'/' in fields[4] and '/openroad ' in fields[4]:
  processes.append(dict(pid=int(fields[0]),elapsed=fields[1],cpu_percent=float(fields[2]),rss_kib=int(fields[3])))
print('OpenROAD processes:',processes)
observation={'time':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'run':run.name,'free_bytes':shutil.disk_usage(r).free,'processes':processes}
with (r/'evidence/resource-observations.jsonl').open('a') as f:f.write(json.dumps(observation)+'\n')
