"""Record the observed end of the bounded ARRAY phase, never stop another job."""
from pathlib import Path
import json,subprocess,hashlib,datetime,shutil
W=Path(__file__).resolve().parent
g=json.loads((W/'evidence/array_port-guard.json').read_text())
assert g['status']!='running'
pg=g['pid'];remaining=[]
for line in subprocess.check_output(['ps','-axo','pid=,pgid=,state=,comm='],text=True).splitlines():
 fields=line.split(None,3)
 if len(fields)>=3 and int(fields[1])==pg:remaining.append({'pid':int(fields[0]),'pgid':int(fields[1]),'state':fields[2],'executable':fields[3] if len(fields)>3 else None})
assert not any(not p['state'].startswith('Z') for p in remaining),remaining
run=W/'runs/array_port-v2';states=sorted(run.glob('*/state_out.json'))
step=run/'32-openroad-repairdesignpostgpl';log=step/'openroad-repairdesignpostgpl.log'
counters=[line for line in log.read_text().splitlines() if '|' in line and line.strip()[:1].isdigit()]
free=shutil.disk_usage('/').free/2**30;assert free>=20
r={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'guard':g,'flow_process_group':pg,'remaining_group_processes':remaining,'no_live_flow_processes':True,'last_completed_step':states[-1].parent.name,'last_printed_repair_counter':counters[-1] if counters else None,'repair_step_has_state_out':(step/'state_out.json').exists(),'repair_log':str(log.relative_to(W)),'repair_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'root_free_gib':free,'physical_completion_credit':False,'note':'Interrupted/uncompleted repair counters are not a saved repaired database, extracted timing, routing, or signoff pass.'}
(W/'evidence/array_port-v2-bounded-stop.json').write_text(json.dumps(r,indent=2)+'\n')
print('W2b-STATUS: ARRAY stop receipt saved; no live flow processes; last completed',r['last_completed_step'])
