#!/usr/bin/env python3
"""Continue the completed full-ROM prefix within its original total budget."""
import json,os,subprocess,time,sys
from pathlib import Path
r=Path(__file__).resolve().parent
b=json.loads((r/'evidence/full-rom-physical-budget.json').read_text())
deadline=b['start_unix']+b['remaining_physical_seconds']
suffix=sys.argv[1] if len(sys.argv)>1 else 'util20-density35-200ns'
prefix='rv_fixed_proj320_rom-'+suffix
continuation_tag='route-'+suffix
decision_file=r/'evidence'/f'full-rom-continuation-{suffix}.json'
receipt=r/'evidence'/f'{prefix}.supervisor.json'
while not receipt.exists() and time.time()<deadline+30:time.sleep(5)
status={'prefix':prefix,'deadline_unix':deadline,'decision_unix':time.time()}
if not receipt.exists():status['decision']='No completion receipt before deadline; no continuation.'
else:
 q=json.loads(receipt.read_text());states=list((r/'runs'/prefix).glob('*-openroad-stamidpnr-1/state_out.json'))
 remain=int(deadline-time.time())
 if q['exit_code']!=0 or q['stop_reason'] or not states or remain<=30:
  status.update(decision='Prefix not successful or total budget exhausted; no continuation.',prefix_outcome=q,remaining_seconds=remain)
 else:
  status.update(decision='Continue full flow from post-CTS timing repair.',initial_state=str(states[0]),remaining_seconds=remain)
  decision_file.write_text(json.dumps(status,indent=2)+'\n')
  env=dict(os.environ,W2_FROM_STEP='OpenROAD.ResizerTimingPostCTS',W2_INITIAL_STATE=str(states[0]),W2_CONFIG_PATH=str(r/'configs'/f'{prefix}.json'),W2_NUM_THREADS='4',W2_LIMIT_SECONDS=str(remain))
  env.pop('W2_TO_STEP',None)
  rc=subprocess.run([str(r.parents[1]/'.venv/bin/python'),str(r/'supervise.py'),'rv_fixed_proj320_rom',continuation_tag],env=env).returncode
  status['continuation_returncode']=rc
decision_file.write_text(json.dumps(status,indent=2)+'\n')
print('W2-STATUS: Full-ROM bounded continuation controller ended:',status['decision'],flush=True)
