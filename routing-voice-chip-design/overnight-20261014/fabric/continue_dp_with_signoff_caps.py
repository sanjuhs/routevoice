#!/usr/bin/env python3
"""Preserve successful GRT and resume with explicit KLayout limits, no new budget."""
import json,os,signal,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
prefix='rv_fixed_proj320_dp-route200';receipt=r/'evidence'/f'{prefix}.supervisor.json'
state=r/'runs'/prefix/'03-openroad-globalrouting/state_out.json'
record={'purpose':'Resume after successful global routing with explicit KLayout thread caps, retaining original run deadline.'}
while not state.exists() and not receipt.exists():time.sleep(5)
if state.exists() and not receipt.exists():
 lines=subprocess.check_output(['ps','-axo','pid,command'],text=True).splitlines()
 matches=[int(line.split(None,1)[0]) for line in lines if line.rstrip().endswith('supervise.py rv_fixed_proj320_dp route200')]
 assert len(matches)==1,matches
 record['interrupted_supervisor_pid']=matches[0];record['interrupt_unix']=time.time()
 os.kill(matches[0],signal.SIGINT)
 while not receipt.exists():time.sleep(2)
q=json.loads(receipt.read_text());remain=int(q['start_unix']+q['limit_seconds']-time.time())
record.update(original_outcome=q,remaining_seconds=remain)
if state.exists() and remain>30:
 record['decision']='Continue from OpenROAD.CheckAntennas with same total deadline.'
 (r/'evidence/dp-signoff-thread-cap-continuation.json').write_text(json.dumps(record,indent=2)+'\n')
 env=dict(os.environ,W2_FROM_STEP='OpenROAD.CheckAntennas',W2_INITIAL_STATE=str(state),W2_CONFIG_PATH=str(r/'configs/rv_fixed_proj320_dp-util20-200ns.json'),W2_NUM_THREADS='4',W2_LIMIT_SECONDS=str(remain))
 env.pop('W2_TO_STEP',None)
 rc=subprocess.run([str(r.parents[1]/'.venv/bin/python'),str(r/'supervise.py'),'rv_fixed_proj320_dp','postgrt-capped'],env=env).returncode
 record['continuation_returncode']=rc
else:record['decision']='No successful GRT checkpoint or no remaining budget; no continuation.'
(r/'evidence/dp-signoff-thread-cap-continuation.json').write_text(json.dumps(record,indent=2)+'\n')
print('W2-STATUS: V2 signoff-cap controller ended:',record['decision'],flush=True)
