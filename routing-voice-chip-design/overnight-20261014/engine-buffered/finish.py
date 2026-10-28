"""Run final characterization only after actual required artifacts exist."""
import json
import subprocess
import time
from pathlib import Path

W=Path(__file__).resolve().parent
shell='/workspace/rv/tools/librelane/shell.nix'
def collect():
    subprocess.run(['python3',str(W/'collect.py')],check=True)
while not (W/'evidence/flow-buf-v4-physical.exit').exists():
    collect()
    time.sleep(30)
collect()
d=json.loads((W/'results.json').read_text())
if d['steps']['extraction']:
    while not (W/'evidence/gate-activity.status').exists():
        # The parent controls the morning stop; do not fabricate partial activity.
        collect()
        time.sleep(30)
    subprocess.run(['nix-shell',shell,'--run',f'python3 {W}/run-power.py'],check=False)
collect()
states=sorted((W/'runs/buf-v4-physical').glob('*/state_out.json'),key=lambda p:int(p.parent.name.split('-')[0]))
gds=None
for p in states:
    s=json.loads(p.read_text())
    gds=s.get('gds') or s.get('mag_gds') or s.get('klayout_gds') or gds
if isinstance(gds,str) and Path(gds).exists():
    with (W/'logs/supplemental-klayout-drc.log').open('w') as out:
        cp=subprocess.run(['nix-shell',shell,'--run',f'bash {W}/run-klayout-drc.sh {gds}'],stdout=out,stderr=subprocess.STDOUT)
    (W/'evidence/supplemental-klayout-drc.exit').write_text(str(cp.returncode)+'\n')
collect()
