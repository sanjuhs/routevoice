from pathlib import Path
import numpy as np,json,hashlib,re
W=Path(__file__).resolve().parent;R=W.parents[1]
z=np.load(W/'vectors/model.npz');a=np.array([int(x,16) for x in (W/'vectors/inputs.hex').read_text().split()],np.int64).reshape(54,1280);a[a>=256]-=512
out=np.zeros((54,320),np.int64)
for row in range(1280):
 partial=a[:,row,None]*np.arange(16,dtype=np.int64)
 w=z['books'][row//64,np.arange(320),z['indices'][row]]
 out+=partial[:,w&15]+(partial[:,w>>4]<<4)
out-=a.sum(axis=1)[:,None]*z['zero'][None,:]
np.testing.assert_array_equal(out,np.load(W/'vectors/numpy-integer-reference.npy'))
report=json.loads((R/'reports/taalas-projection-nibble-k64-affine.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['inputs.hex','expected.hex','activation-scales.hex','weight-scales.hex','bias.hex']:
 path='build/taalas-projection-nibble-k64-affine/'+name
 assert sha(W/'vectors'/name)==next(v['sha256'] for v in report['artifacts'] if v['path']==path)
variants={}
for v in ['array_port','sc_rom']:
 log=W/'logs'/f'{v}-full-simulation.log'
 if not log.exists():log=W/'evidence'/f'{v}-full-simulation.log'
 text=log.read_text()
 m=re.search(r'PASS vectors=(\d+) outputs=(\d+) cycles=\s*(\d+) stalls=\s*(\d+) aborts=(\d+) unstalled_cycles=(\d+)',text)
 assert m and 'Verilog $finish' in text, f'No completed regression: {log}'
 vectors,outputs,cycles,stalls,aborts,unstalled=map(int,m.groups())
 assert (vectors,outputs,cycles,stalls,aborts,unstalled)==(54,17280,300952,104112,4,4163)
 assert 'if(integer_checks!=17280)$fatal' in (W/'tb'/f'{v}.sv').read_text()
 variants[v]={'vectors':vectors,'integer_outputs':outputs,'fp32_outputs':outputs,'aborts':aborts,'stall_events':stalls,'total_cycles':cycles,'unstalled_cycles':unstalled,'full_log':str(log.relative_to(W)),'full_log_sha256':sha(log),'testbench_sha256':sha(W/'tb'/f'{v}.sv'),'speech_trace':f'evidence/{v}-speech.vcd','speech_trace_sha256':sha(W/'evidence'/f'{v}-speech.vcd'),'speech_trace_projection_vectors':1,'speech_trace_outputs':320}
checks={'scheduled_shared_partial_numpy_outputs':17280,'saved_affine_artifacts_hashes_match':True,'rtl_variants':variants,'activity_provenance':'Vector 0 from hash-checked saved affine inputs.hex; its saved report binds captured real-speech quantized input. Fresh real-speech capture was not performed.'}
(W/'evidence/correctness.json').write_text(json.dumps(checks,indent=2))
print('W2b-STATUS: independent scheduled numpy reference PASS 17280 outputs; one-vector speech VCDs retained for both variants')
