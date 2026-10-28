#!/usr/bin/env python3
import json,re,datetime
from pathlib import Path
W=Path(__file__).resolve().parents[1]
runs=[]
for run in sorted((W/'runs').glob('complete-*')):
 stages=[]
 for step in sorted(run.glob('[0-9][0-9]-*')):
  state=step/'state_out.json'
  if state.exists():
   d=json.loads(state.read_text());m=d.get('metrics',{})
   selected={k:v for k,v in m.items() if re.search(r'area|setup|hold|drc|antenna|lvs|power|slew|cap|unmapped|check_error|disconnected|instance__count|wirelength',k,re.I)}
   native=step/'or_metrics_out.json'
   native_metrics=json.loads(native.read_text()) if native.exists() else None
   stages.append(dict(step=step.name,metrics=selected,metrics_note='state_out metrics are cumulative and may originate in earlier stages; consult native step metrics/reports before attributing timing to this stage',native_step_metrics=native_metrics,views={k:v for k,v in d.items() if k!='metrics'}))
 log=W/'logs'/('physical-'+run.name.split('-')[-1]+'.log')
 exitfile=log.with_suffix('.exit')
 runs.append(dict(run=run.name,exit_code=exitfile.read_text().strip() if exitfile.exists() else None,completed_stages=stages,latest_completed=stages[-1]['step'] if stages else None))
(W/'evidence/physical-snapshot.json').write_text(json.dumps(dict(updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),runs=runs),indent=2)+'\n')
for r in runs:print(r['run'],r['exit_code'],r['latest_completed'])
