#!/usr/bin/env python3
"""Keep pre-route evidence separate from routed/signoff metrics."""
import json,re
from pathlib import Path
r=Path(__file__).resolve().parent;records=[]
for run in sorted((r/'runs').iterdir()):
 if not (run/'resolved.json').is_file():continue
 cfg=json.loads((run/'resolved.json').read_text());period=float(cfg['CLOCK_PERIOD'])
 for step in sorted(run.glob('*-openroad-stamidpnr*')):
  if not (step/'state_out.json').exists():continue
  entry={'run':str(run.relative_to(r)),'step':str(step.relative_to(r)),'scope':'pre-route placement-estimated parasitics; not extracted/signoff','period_ns':period,'target_mhz':1000/period}
  metrics=step/'or_metrics_out.json'
  if metrics.exists():
   m=json.loads(metrics.read_text());entry['fresh_step_metrics']=m
   entry['sta_corners']={}
   for key,value in m.items():
    for kind in ['setup','hold']:
     prefix=f'timing__{kind}__ws__corner:'
     if key.startswith(prefix):entry['sta_corners'].setdefault(key[len(prefix):],{})[kind+'_slack_ns']=value
   entry['typical_setup_slack_ns']=m.get('timing__setup__ws__corner:nom_tt_025C_5v00');entry['typical_hold_slack_ns']=m.get('timing__hold__ws__corner:nom_tt_025C_5v00')
   setup=entry['typical_setup_slack_ns']
   entry['typical_setup_inferred_mhz']=1000/(period-setup) if isinstance(setup,(int,float)) and setup<period else None
  log=step/'openroad-stamidpnr.log'
  if log.exists():
   txt=log.read_text(errors='replace');power={}
   for label in ['DEFAULT','VCD']:
    p=re.search(r'W2_'+label+r'_ACTIVITY_POWER_BEGIN (\S+)\n(.*?)W2_'+label+r'_ACTIVITY_POWER_END',txt,re.S)
    if p:
     total=re.search(r'^Total\s+([\deE+.-]+)\s+([\deE+.-]+)\s+([\deE+.-]+)\s+([\deE+.-]+)',p[2],re.M)
     if total:power[label.lower()]={'corner':p[1],'components_mw':dict(zip(['internal','switching','leakage','total'],[float(x)*1000 for x in total.groups()]))}
   if power:
    entry['power']=power;n=re.findall(r'Annotated (\d+) pin activities',txt);entry['vcd_annotated_pins']=int(n[0]) if n else None
    n=re.findall(r'^unannotated\s+(\d+)',txt,re.M);entry['unannotated_pins']=int(n[0]) if n else None
    entry['vcd_valid_nonzero_annotation']=bool(entry['vcd_annotated_pins'])
    entry['annotation_limitation']='Zero-delay synthesis-netlist cell-pin activity. Inserted/changed physical cells rely on propagated/default activity; no routed glitches.' if 'gate-cell' in run.name else f"RTL top-level port activity: {entry['vcd_annotated_pins']} directly annotated pins; internal activity propagated/default. No gate-level glitch modelling. Zero matched pins is a failed annotation attempt."
    if entry['vcd_annotated_pins'] is not None and entry['unannotated_pins'] is not None:entry['annotated_pin_fraction']=entry['vcd_annotated_pins']/(entry['vcd_annotated_pins']+entry['unannotated_pins'])
    entry['power_source_log']=str(log.relative_to(r))
  records.append(entry)
(r/'evidence/checkpoint-metrics.json').write_text(json.dumps(records,indent=2)+'\n');print('W2-STATUS: Collected',len(records),'explicitly pre-route timing/power checkpoints')
