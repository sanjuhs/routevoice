#!/usr/bin/env python3
"""Select completed physical views, then run the retained timing/power recipe.

Run inside the existing pod's Nix shell. Refuses absent extracted parasitics.
No physical design is edited. Each output directory must be new.
"""
import argparse, fnmatch, json, os, subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('kind', choices=['timing','active','idle'])
p.add_argument('--run',default='complete-v3')
p.add_argument('--corner',default='nom_tt_025C_3v30')
p.add_argument('--output',required=True)
p.add_argument('--spef')
a=p.parse_args()
w=Path(__file__).resolve().parents[1]
r=w/'runs'/a.run
c=json.loads((r/'resolved.json').read_text())
states=sorted(r.glob('[0-9][0-9]-*/state_out.json'))
assert states, 'No completed stages'
state_path=states[-1]
s=json.loads(state_path.read_text())
spefs=s.get('spef')
assert spefs, 'No extracted SPEF in latest completed physical state'
if a.spef:
    spef=Path(a.spef)
elif isinstance(spefs,str):
    spef=Path(spefs)
else:
    matches=[v for k,v in spefs.items() if fnmatch.fnmatch(a.corner,k) or k==a.corner.split('_')[0]]
    assert len(matches)==1, f'Ambiguous SPEF keys {list(spefs)}; select --spef'
    spef=Path(matches[0])
assert spef.is_file(), spef
libs=[v for k,v in c['LIB'].items() if fnmatch.fnmatch(a.corner,k)]
assert len(libs)==1, 'Expected exactly one PVT library group'
sdcs=sorted(r.glob('[0-9][0-9]-*/rv_k64_projection_complete.sdc'))
sdcs=[q for q in sdcs if q.parent.name<=state_path.parent.name]
assert sdcs, 'No emitted self-contained physical SDC'
env=os.environ.copy()
env.update(W8_LIB_LIST='\n'.join(libs[0]),
           W8_MACRO_LIB=str(w/'macro/PITCH_BANK_R1280.lib'),
           W8_NETLIST=s['nl'],W8_TOP='rv_k64_projection_complete',
           W8_SDC=str(sdcs[-1]),W8_SPEF=str(spef),W8_CORNER=a.corner,
           W8_OUT_DIR=str(w/a.output),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
if a.kind!='timing':
    active=a.kind=='active'
    env.update(W8_VCD=str(w/'evidence'/('gate-speech.vcd' if active else 'gate-idle.vcd')),
               W8_SKIP_DEFAULT_POWER='1',
               W8_WORKLOAD_KIND=a.kind,W8_COMPLETED_PROJECTIONS='1' if active else '0',
               W8_ACTIVITY_NETLIST=str(r/'02-yosys-synthesis/rv_k64_projection_complete.nl.v'),
               W8_ACTIVITY_NOTE='Mapped complete top, zero-delay GF180 functional cells; actual speech vector0, or +idle. See gate simulation receipts. No SDF glitches modeled.')
script=w/'power'/('run_timing.py' if a.kind=='timing' else 'run_power.py')
print(json.dumps({'state':str(state_path),'kind':a.kind,'corner':a.corner,
                  'netlist':s['nl'],'sdc':str(sdcs[-1]),'spef':str(spef)},indent=2),flush=True)
subprocess.run(['python3',str(script)],env=env,check=True)
