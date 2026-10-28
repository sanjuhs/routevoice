from pathlib import Path
import json,re,hashlib,sys
import numpy as np
W=Path(__file__).resolve().parent;v=sys.argv[1]
g=json.loads((W/'evidence'/f'{v}-activity-guard.json').read_text());assert g.get('returncode')==0
log=W/'logs'/f'{v}-activity-simulation.log';text=log.read_text()
assert re.search(r'PASS gate_activity vectors=1 outputs=320 cycles=\s*4163 stalls=\s*0 aborts=0 unstalled_cycles=4163',text) and 'Verilog $finish' in text
trace=W/'evidence'/f'{v}-mapped-speech.saif'
with trace.open('r') as f:header=f.read(1024)
duration=int(re.search(r'\(DURATION\s+(\d+)\)',header).group(1));assert '(TIMESCALE 1ps)' in header
acts=np.array([int(x,16) for x in (W/'vectors/inputs.hex').read_text().split()[:1280]],np.int64);acts[acts>=256]-=512
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
files=[trace,log,W/'tb'/f'activity_{v}.sv',W/'runs'/f'{v}-v2/06-yosys-synthesis/rv_k64_{v}.nl.v',W/'vectors/inputs.hex',W/'vectors/activation-scales.hex']
r={'variant':v,'status':'one_vector_functional_pass_and_trace_complete','vectors':1,'fp32_outputs':320,'cycles_excluding_start':4163,'stalls':0,'reset_mid_vector_tests':0,'initial_reset_included':True,'clock_period_ns':20,'trace_duration_ps':duration,'trace_duration_us':duration/1e6,'trace_duration_over_projection_ns':duration/1000-4163*20,'activity':'Mapped standard-cell zero-delay simulation, saved real activation vector0; no SDF delays or glitch timing, not a long stream/idle/peak characterization.','activation_statistics':{'samples':1280,'min':int(acts.min()),'max':int(acts.max()),'zero_count':int(np.count_nonzero(acts==0)),'mean_absolute':float(np.abs(acts).mean())},'guard':g,'artifacts':{str(p.relative_to(W)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files},'annotation_coverage_pending':True,'power_computed':False}
annotation=W/'evidence'/f'{v}-placed-saif-annotation.rpt'
probe=W/'logs/saif-projection-probe-success.log'
if v=='array_port' and annotation.exists() and probe.exists():
 a=annotation.read_text();p=probe.read_text()
 assert 'Error:' not in p and 'Annotated 1253320 pin activities.' in p
 annotated=int(re.search(r'^saif\s+(\d+)',a,re.M).group(1))
 unannotated=int(re.search(r'^unannotated\s+(\d+)',a,re.M).group(1))
 r['annotation_coverage_pending']=False
 r['annotation']={'stage':'28-openroad-globalplacement; not final routed netlist','annotated_pins':annotated,'unannotated_pins':unannotated,'coverage_fraction':annotated/(annotated+unannotated),'netlist':'runs/array_port-v2/28-openroad-globalplacement/rv_k64_array_port.nl.v','report':str(annotation.relative_to(W)),'log':str(probe.relative_to(W)),'units':{'time':'ns','capacitance':'pF','power':'uW'}}
 r['artifacts'][str(annotation.relative_to(W))]={'bytes':annotation.stat().st_size,'sha256':sha(annotation)}
 r['artifacts'][str(probe.relative_to(W))]={'bytes':probe.stat().st_size,'sha256':sha(probe)}
(W/'evidence'/f'{v}-mapped-activity.json').write_text(json.dumps(r,indent=2)+'\n');print('W2b-STATUS: Complete mapped SAIF validated:',v,'duration_us',duration/1e6,'bytes',trace.stat().st_size)
if v=='sc_rom':
 annotation=W/'evidence/sc_rom-synth-saif-annotation.rpt'
 probe=W/'logs/sc-saif-probe.log'
 if annotation.exists() and probe.exists():
  a=annotation.read_text();p=probe.read_text();assert 'Error:' not in p
  annotated=int(re.search(r'^saif\s+(\d+)',a,re.M).group(1))
  unannotated=int(re.search(r'^unannotated\s+(\d+)',a,re.M).group(1))
  assert f'Annotated {annotated} pin activities.' in p
  r['annotation_coverage_pending']=False
  r['annotation']={'stage':'06-yosys-synthesis; not final routed netlist','annotated_pins':annotated,'unannotated_pins':unannotated,'coverage_fraction':annotated/(annotated+unannotated),'netlist':'runs/sc_rom-v2/06-yosys-synthesis/rv_k64_sc_rom.nl.v','report':str(annotation.relative_to(W)),'log':str(probe.relative_to(W)),'units':{'time':'ns','capacitance':'pF','power':'uW'}}
  for f in [annotation,probe]:r['artifacts'][str(f.relative_to(W))]={'bytes':f.stat().st_size,'sha256':sha(f)}
  (W/'evidence'/f'{v}-mapped-activity.json').write_text(json.dumps(r,indent=2)+'\n')
