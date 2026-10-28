from pathlib import Path
import json,re,hashlib
W=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
results={}
for v in ['array_port','sc_rom']:
 guard=W/'evidence'/('gate-guard.json' if v=='array_port' else 'sc_rom-gate-guard.json')
 g=json.loads(guard.read_text()) if guard.exists() else {'status':'not_run'}
 p=W/'logs'/f'{v}-gate-simulation.log';text=p.read_text() if p.exists() else ''
 m=re.search(r'PASS gate vectors=(\d+) outputs=(\d+) cycles=\s*(\d+) stalls=\s*(\d+) aborts=(\d+) unstalled_cycles=(\d+)',text)
 passed=(g.get('returncode')==0 or (g.get('status')=='functional_completion_observed' and g.get('normal_finish_in_log'))) and m is not None and 'Verilog $finish' in text
 r={'status':'pass' if passed else g['status'],'stage':'mapped synthesis netlist, zero-delay functional cells; not routed or SDF timing verification','guard':g,'log':str(p.relative_to(W)),'integer_internal_checks':False}
 if passed:
  vectors,outputs,cycles,stalls,aborts,unstalled=map(int,m.groups())
  assert (vectors,outputs,cycles,stalls,aborts,unstalled)==(54,17280,300952,104112,4,4163)
  r.update(vectors=vectors,fp32_outputs=outputs,cycles=cycles,stall_events=stalls,reset_tests=aborts,unstalled_cycles=unstalled,log_sha256=sha(p),testbench_sha256=sha(W/'tb'/f'gate_{v}.sv'),netlist_sha256=sha(W/'runs'/f'{v}-v2/06-yosys-synthesis/rv_k64_{v}.nl.v'))
 results[v]=r
(W/'evidence/gate-correctness.json').write_text(json.dumps(results,indent=2)+'\n')
print('W2b-STATUS: mapped functional replay:',{v:r['status'] for v,r in results.items()})
