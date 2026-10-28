from pathlib import Path
import sys,json,time,gzip,hashlib
import numpy as np
sys.dont_write_bytecode=True
R=Path.cwd();W=Path(__file__).resolve().parent;D=W/'ss-120ns';S=R/'overnight-20261014/taalas-pitch/timing';O=S/'r1280-g02';sys.path.insert(0,str(S));import simulate
meta=json.loads((D/'build.json').read_text()); names=json.loads((D/'names.json').read_text());trace=np.loadtxt(D/'trace.dat',skiprows=1);image=np.load(O/'image.npy');assert trace[-1,0]>=1200e-9*.999
out=simulate.analyze(trace,names,meta,image,2.97);watch=json.loads((D/'watchdog-extension.json').read_text())
out.update({'corner':'ss','voltage_v':2.97,'temperature_c':125,'protocol':meta['protocol'],'scope':meta['scope'],'wall_seconds':watch['supervisor_completed_epoch']-watch['guard_start_epoch'],'wall_seconds_scope':'native launch log birth through supervisor completion; includes up to2s supervisor poll delay','full_bank_timing_proven':False,'full_row_energy_pj':None,'reset_abort_qualified':False,'source_inputs':{str(q):simulate.sha(q) for q in [S/'simulate.py',S/'protocols.py',O/'joined-canonical.spice',O/'array-canonical.spice',O/'image.npy']},'deck_sha256':simulate.sha(D/'test.cir'),'trace_sha256':simulate.sha(D/'trace.dat')})
try:json.dumps(out,indent=2)
except TypeError as exc:
 (D/'postprocess-original-failure.json').write_text(json.dumps({'error':str(exc),'scope':'Reproduced original analyzer JSON serialization failure on retained completed trace; nativeSPICE complete; no native rerun','fix':'Convert numpy scalar via.item only at JSON serialization boundary; circuit, trace, analysis unchanged'},indent=2))
(D/'result.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item())+'\n')
with gzip.open(D/'trace.dat.gz','wb') as f:f.write((D/'trace.dat').read_bytes())
print(json.dumps({k:out[k] for k in ['protocol_pass','failures','maximum_sampled_settled_ns','energy_pj_per_sampled_read','wall_seconds']},default=lambda x:x.item()))
