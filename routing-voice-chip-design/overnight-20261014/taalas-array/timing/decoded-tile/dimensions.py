from pathlib import Path
from collections import Counter
import json
W=Path(__file__).resolve().parent;O=W/'v1'
def units(s):return round(float(s[:-1])*1e-6 if s.endswith('u') else float(s),14)
def read(p):
 d=Counter();ports=Counter()
 for l in p.read_text().splitlines():
  if not l.startswith('X'):continue
  f=l.split();v=dict(t.lower().split('=') for t in f[6:]);d[(f[5],units(v['w']),units(v['l']))]+=1
  for pos,n in enumerate(f[1:5]):
   if n in ['VDD','VSS','EVAL','PC'] or n.startswith('ROW'):ports[(n,"DS" if pos in [0,2] else pos,f[5])]+=1
 return d,ports
a,ap=read(O/'canonical.spice');b,bp=read(O/'reference.spice');r={'full_transistor_type_width_length_population_match':a==b,'global_control_power_terminal_population_match':ap==bp,'scope':'Necessary checks on entire111460device flatnetlists, complementary to fullNetgen graph matching; not substitute LVS'};(O/'dimensions-check.json').write_text(json.dumps(r,indent=2));print(r);assert a==b;assert ap==bp
