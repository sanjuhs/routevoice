#!/usr/bin/env python3
"""Run typical-corner STA with five-vector VCD; explicit --pre-route labels placement estimates."""
import gzip,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent
variant=sys.argv[1];state=Path(sys.argv[2]).resolve();base=Path(sys.argv[3]).resolve()
assert state.is_file() and base.is_file()
d=json.loads(state.read_text());pre_route='--pre-route' in sys.argv
if pre_route:assert d.get('odb'), 'Placed ODB required'
else:assert d.get('spef'), 'Extracted SPEF required; pass --pre-route explicitly for labelled placement estimates'
tag='pre-route-activity' if pre_route else 'activity'
stage='OpenROAD.STAMidPNR' if pre_route else 'OpenROAD.STAPostPNR'
if '--tag' in sys.argv:tag=sys.argv[sys.argv.index('--tag')+1]
assert re.fullmatch(r'[a-z0-9-]+',tag) and tag.endswith('activity')
assert not (r/'runs'/f'{variant}-{tag}').exists(), 'Use a fresh --tag ending in activity to preserve prior evidence'
run_state=state
if pre_route:
 # STAMidPNR declares only ODB as a required input. Keep the source SDC and metrics;
 # omit unrelated inherited views from this auxiliary run to avoid copying old SDFs.
 minimal={k:(value if k in ['odb','sdc','metrics'] else None) for k,value in d.items()}
 run_state=r/'evidence'/f'{variant}-{tag}-minimal-state.json';run_state.write_text(json.dumps(minimal,indent=2)+'\n')
c=json.loads(base.read_text());period=int(c['CLOCK_PERIOD']);assert period in (20,200)
source=r/'vectors'/f'{variant}.power{f"-{period}ns" if period!=20 else ""}.vcd.gz'
scope='tb/dut'
if '--scope' in sys.argv:scope=sys.argv[sys.argv.index('--scope')+1]
assert re.fullmatch(r'[A-Za-z0-9_/]+',scope)
custom='--vcd' in sys.argv
if custom:
 source=Path(sys.argv[sys.argv.index('--vcd')+1]).resolve();assert source.is_file();vcd=source
else:
 vcd=r/'tmp'/f'{variant}-{tag}.vcd'
 with gzip.open(source,'rb') as src,vcd.open('wb') as out:shutil.copyfileobj(src,out)
with vcd.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
hook=r/'evidence'/f'{variant}-{tag}-power-hook.tcl';hook.write_text((r/'power_activity.tcl').read_text().replace('read_vcd -scope tb/dut',f'read_vcd -scope {scope}'))
c.update(STA_CORNERS=['nom_tt_025C_5v00'],STA_THREADS=1,DRT_THREADS=1,STA_EXTRA_CORNER_TCL_FILE=str(hook))
config=r/'configs'/f'{variant}-{tag}.json';config.write_text(json.dumps(c,indent=2)+'\n')
(r/'evidence'/f'{variant}-{tag}-input.json').write_text(json.dumps({'parasitics':'placement-estimated, NOT extracted' if pre_route else 'extracted SPEF','hook':str(hook),'hook_sha256':hashlib.sha256(hook.read_bytes()).hexdigest(),'source_state':str(state),'auxiliary_run_state':str(run_state),'omitted_views_note':'Pre-route auxiliary uses required ODB plus SDC/metrics; original complete checkpoint unchanged' if pre_route else None,'config':str(config),'vcd':str(vcd),'compressed_source':str(source),'vcd_sha256':digest,'clock_period_ns':period,'corner':'nom_tt_025C_5v00','vcd_scope':scope,'activity':'Five random zero-delay gate vectors with cell pins plus clocked readout; no routed glitches' if custom else 'Five random RTL vectors plus clocked readout, no gate-level glitches'},indent=2)+'\n')
env=os.environ.copy();env.update(W2_FROM_STEP=stage,W2_TO_STEP=stage,W2_INITIAL_STATE=str(run_state),W2_CONFIG_PATH=str(config),W2_VCD=str(vcd),W2_NUM_THREADS='1')
status=subprocess.run([sys.executable,str(r/'supervise.py'),variant,tag],env=env).returncode
counts=[]
for log in (r/'runs'/f'{variant}-{tag}').rglob('*.log'):
 text=log.read_text(errors='replace')
 counts.extend(map(int,re.findall(r'Annotated (\d+) pin activities',text)))
validation={'step_exit_code':status,'annotated_pins':max(counts) if counts else None,'nonzero_annotation':bool(counts and max(counts)>0),'parasitics':'placement-estimated, NOT extracted' if pre_route else 'extracted SPEF'}
(r/'evidence'/f'{variant}-{tag}-annotation-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print('W2-STATUS: VCD annotation validation',json.dumps(validation))
raise SystemExit(status if status else (0 if validation['nonzero_annotation'] else 2))
