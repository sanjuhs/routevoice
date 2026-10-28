"""Summarize physical full-bank control net incident capacitance.

Incident sum is a capacitance inventory, not switching-energy or delay proof.
MOS intrinsic capacitance is supplied by transistor models, not this C sum.
"""
from pathlib import Path
import json,re,argparse,hashlib
from collections import defaultdict
P=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();assert re.fullmatch('[A-Za-z0-9_-]+',a.run);o=P/a.run;src=o/'extracted-cap.spice'
control_names={f'WL{r}' for r in range(320)}|{'PC'};bitline_names={f'IDX{c}_{b}' for c in range(320) for b in range(4)};controls=control_names|bitline_names;nets={n:dict(incident_capacitance_ff=0.0,explicit_cap_elements=0,gate_devices=0,gate_width_um=0.0,access_connected_drains=0,by_other_node_class_ff=defaultdict(float)) for n in controls};back={}
def name(n):
 short=n.rsplit('.',1)[-1]
 if short in controls:
  assert short not in back or back[short]==n,('nonbijective control names',n,back.get(short));back[short]=n
 return short
units={'f':1,'p':1000,'n':1e6,'u':1e9,'m':1e12,'':1e15}
def ff(s):
 m=re.fullmatch(r'([0-9.eE+-]+)([fpnum]?)',s);assert m,s;return float(m[1])*units[m[2]]
all_c=0
with src.open() as f:
 for l in f:
  t=l.split()
  if l.startswith('X'):
   gate=name(t[2])
   if gate.startswith('WL'):
    for node in (t[1],t[3]):
     node=name(node)
     if node in bitline_names:nets[node]['access_connected_drains']+=1
   if gate in controls:
    v=dict(x.split('=',1) for x in t[6:]);nets[gate]['gate_devices']+=1;nets[gate]['gate_width_um']+=float(v['w'].removesuffix('u'))
  elif l.startswith('C'):
   all_c+=1;n1,n2=name(t[1]),name(t[2]);c=ff(t[3]);assert n1!=n2
   for n,other in ((n1,n2),(n2,n1)):
    if n not in controls:continue
    z=nets[n];z['incident_capacitance_ff']+=c;z['explicit_cap_elements']+=1
    kind='other_wordline' if other.startswith('WL') else 'PC' if other=='PC' else 'VSS_or_ground' if other in ['VSS','0','GND','VSUBS'] else 'VDD' if other=='VDD' else 'bitline' if other.startswith('IDX') else 'output' if other.startswith('OUT') else 'other'
    z['by_other_node_class_ff'][kind]+=c
assert set(back)==controls
assert all(nets[n]['gate_devices']==1280 for n in control_names)
assert all(nets[n]['gate_devices']==2 for n in bitline_names)
report=dict(source='extracted-cap.spice',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),all_explicit_cap_elements=all_c,controls={n:nets[n] for n in control_names},bitlines={n:nets[n] for n in bitline_names},bitlines_ranked_by_explicit_incident_cap_ff=sorted(bitline_names,key=lambda n:nets[n]['incident_capacitance_ff'],reverse=True),wordline_min_incident_ff=min(nets[f'WL{r}']['incident_capacitance_ff'] for r in range(320)),wordline_max_incident_ff=max(nets[f'WL{r}']['incident_capacitance_ff'] for r in range(320)),precharge_incident_ff=nets['PC']['incident_capacitance_ff'],qualification='Full-bank geometry Magic explicit lumpedC incident inventory; includes real shared320WL/PC rails and joins. Not distributedRPEX. Coupling counted once per endpoint, so sums across controls double-count shared capacitors. Does not include voltage-dependent intrinsicMOS load, which requires the414720device circuit model.')
(o/'control-capacitance.json').write_text(json.dumps(report,indent=2)+'\n');print('W5-STATUS: full bank WL/PC cap inventory', {k:v for k,v in report.items() if k not in ('controls','bitlines','bitlines_ranked_by_explicit_incident_cap_ff')},flush=True)
