from pathlib import Path
import sys,json,shutil,time,subprocess,hashlib,gzip,os
import numpy as np
sys.dont_write_bytecode=True
R=Path.cwd(); W=R/'overnight-20261014/projection-complete/protocol'; S=R/'overnight-20261014/taalas-pitch/timing'; O=S/'r1280-g02'; D=W/'ss-120ns'; D.mkdir(exist_ok=False)
sys.path.insert(0,str(S)); import simulate
p={'period_ns':120.,'pc_off_ns':20.,'wl_start_ns':40.,'wl_fall_start_ns':100.,'wl_fall_end_ns':100.2,'pc_on_start_ns':120.,'sample_ns':[80.,99.5],'edge_ns':.2,'phase_family':'W8 synchronous20ns; capture80 WLoff100 PCon120'}
simulate.protocol=lambda period:p
assert shutil.disk_usage('/').free>=22*2**30
lines,names,meta,image=simulate.build(O,'ss',2.97,125,120,32)
# Source build assumes PC finishes falling at period. This candidate starts PC falling at120.
# Include its0.2ns edge and preserve exactly120ns repeating interval.
for i,line in enumerate(lines):
 if line.startswith('Vpcin '):
  points=[(0,0)]
  for c in range(len(meta['addresses'])):
   t=c*120.; points.extend([(t+20,0),(t+20.2,2.97),(t+120,2.97),(t+120.2,0)])
  lines[i]='Vpcin pcin 0 '+simulate.pwl(points)
 # Legal-state ideal aggressors recover with physical precharge command edge at120..120.2.
 elif line.startswith('Vagg'):
  n=int(line.split()[0][4:]);points=[(0,2.97)]
  for c,row in enumerate(meta['addresses']):
   if row is not None and (int(image[row,n//4])>>(n%4))&1:
    t=c*120.;points.extend([(t+40.3,2.97),(t+40.5,0),(t+120,0),(t+120.2,2.97)])
  points.append((len(meta['addresses'])*120+.3,2.97));lines[i]=f'Vagg{n} agg{n} 0 '+simulate.pwl(points)
(D/'test.cir').write_text('\n'.join(lines)+'\n');(D/'build.json').write_text(json.dumps(meta,indent=2));(D/'names.json').write_text(json.dumps(names));shutil.copyfile(S/'simulate.py',D/'source-simulate.py');shutil.copyfile(S/'protocols.py',D/'source-protocols.py');shutil.copyfile(__file__,D/'source-run.py')
start=time.monotonic()
with (D/'ngspice.log').open('w') as f:
 try: result=subprocess.run(['nice','-n','10','ngspice','-b','test.cir'],cwd=D,stdout=f,stderr=subprocess.STDOUT,timeout=480,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 except subprocess.TimeoutExpired:
  (D/'FAILURE.json').write_text(json.dumps({'failure':'480second timeout'}));raise
assert result.returncode==0,result.returncode
trace=np.loadtxt(D/'trace.dat',skiprows=1);assert trace[-1,0]>=1200e-9*.999
out=simulate.analyze(trace,names,meta,image,2.97)
out.update({'corner':'ss','voltage_v':2.97,'temperature_c':125,'protocol':p,'scope':meta['scope'],'wall_seconds':time.monotonic()-start,'full_bank_timing_proven':False,'full_row_energy_pj':None,'reset_abort_qualified':False,'source_inputs':{str(q):simulate.sha(q) for q in [S/'simulate.py',S/'protocols.py',O/'joined-canonical.spice',O/'array-canonical.spice',O/'image.npy']},'deck_sha256':simulate.sha(D/'test.cir'),'trace_sha256':simulate.sha(D/'trace.dat')})
(D/'result.json').write_text(json.dumps(out,indent=2));
with gzip.open(D/'trace.dat.gz','wb') as f:f.write((D/'trace.dat').read_bytes())
(D/'trace.dat').unlink(); print(json.dumps({k:out[k] for k in ['protocol_pass','failures','maximum_sampled_settled_ns','energy_pj_per_sampled_read','wall_seconds']}),flush=True)
