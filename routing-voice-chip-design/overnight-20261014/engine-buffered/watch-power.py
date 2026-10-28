from pathlib import Path
import json,time,subprocess
W=Path(__file__).resolve().parent
while True:
 ready=False
 for p in (W/'runs/buf-v4-physical').glob('*-openroad-rcx/state_out.json'):
  d=json.loads(p.read_text());ready=bool(d.get('spef') and d.get('odb') and d.get('sdc'))
 if ready and (W/'evidence/frozen-activity-provenance.json').exists():
  p=subprocess.run(['python3',str(W/'run-power.py')]);raise SystemExit(p.returncode)
 if (W/'evidence/flow-buf-v4-physical.exit').exists() and not ready:
  print('W9-STATUS: flow ended without extracted SPEF; no power claimed');break
 time.sleep(10)
