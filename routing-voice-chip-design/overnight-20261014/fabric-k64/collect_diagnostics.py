"""Keep pre-route failures separate from extracted/signoff result fields."""
from pathlib import Path
import hashlib,json,re
W=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def metric_report(p):
 s=p.read_text()
 values=re.findall(r'^(?:nom|min|max)_\w+: ([+-]?[0-9.eE+-]+)$',s,re.M)
 assert len(values)==1,p
 return float(values[0])
out={'status':'diagnostic_only_not_operating_point','warning':'Unbuffered/high-fanout early netlists violate slew/capacitance limits. Delay and internal-power extrapolation are not an achieved MHz or supported energy estimate. No routed RC extraction or activity-annotated power is available.','variants':{}}
for v in ['array_port','sc_rom']:
 run=W/'runs'/f'{v}-v2';pre=run/'12-openroad-staprepnr'
 timing=[]
 for d in sorted(pre.glob('nom_*')):
  p=d/'wns.max.rpt'
  if not p.exists():continue
  timing.append({'stage':'pre-PNR, no placed or routed parasitics','corner':d.name,'setup_wns_ns':metric_report(p),'setup_report':str(p.relative_to(W)),'hold_wns_ns':metric_report(d/'wns.min.rpt') if (d/'wns.min.rpt').exists() else None})
 data={'early_timing':timing}
 placed=run/'31-openroad-stamidpnr';p=placed/'or_metrics_out.json'
 if p.exists():
  m=load(p)
  data['placement_diagnostics']={'stage':'31-openroad-stamidpnr','corner':'nom_tt_025C_3v30','setup_wns_ns':metric_report(placed/'wns.max.rpt'),'hold_wns_ns':metric_report(placed/'wns.min.rpt'),'max_slew_violations':m['design__max_slew_violation__count__corner:nom_tt_025C_3v30'],'max_cap_violations':m['design__max_cap_violation__count__corner:nom_tt_025C_3v30'],'max_fanout_violations':m['design__max_fanout_violation__count__corner:nom_tt_025C_3v30'],'default_power':{'source':'Flow defaults, before CTS/route; no VCD/SAIF annotation','valid_operating_point':False,'reported_unit':'W, explicitly printed in report','internal_mw':m['power__internal__total']*1000,'switching_mw':m['power__switching__total']*1000,'leakage_mw':m['power__leakage__total']*1000,'total_mw':m['power__total']*1000,'energy_per_projection':None,'report':str((placed/'power.rpt').relative_to(W))}}
 out['variants'][v]=data
(W/'evidence/pre-route-diagnostics.json').write_text(json.dumps(out,indent=2)+'\n')
print('W2b-STATUS: Pre-route timing/power diagnostics preserved separately; no signoff credit.')
