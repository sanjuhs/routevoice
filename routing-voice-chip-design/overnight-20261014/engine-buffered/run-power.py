import fnmatch
import hashlib
import json
import os
import subprocess
from pathlib import Path

W=Path(__file__).resolve().parent
states=sorted((p for p in (W/'runs/buf-v4-physical').glob('*/state_out.json')),key=lambda p:int(p.parent.name.split('-')[0]))
eligible=[]
for p in states:
    d=json.loads(p.read_text())
    if d.get('spef') and d.get('odb') and d.get('sdc'):
        eligible.append((p,d))
if not eligible:
    raise SystemExit('No extracted state: no power run')
state,d=eligible[-1]
try:(W/'evidence/power-run.lock').mkdir()
except FileExistsError:raise SystemExit('Power characterization already started; not duplicating')
spefs=[v for k,v in d['spef'].items() if fnmatch.fnmatch('nom_tt_025C_3v30',k)]
if len(spefs)!=1:
    raise SystemExit(f'Expected one nominal SPEF, found {spefs}')
paths={
    'W9_LIB':'/workspace/rv/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib',
    'W9_ODB':d['odb'],'W9_SDC':d['sdc'],'W9_SPEF':spefs[0],
    'W9_SAIF':str(W/'evidence/array_port-mapped-speech-w9-frozen.saif'),
}
receipt={'state':str(state),'inputs':{}}
for key,path in paths.items():
    p=Path(path); h=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
    receipt['inputs'][key]={'path':path,'bytes':p.stat().st_size,'sha256':h}
(W/'evidence/power-inputs.json').write_text(json.dumps(receipt,indent=2)+'\n')
env=dict(os.environ,**paths,W9_PREFIX=str(W/'evidence/routed-tt'),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1')
with (W/'logs/power-routed-tt.log').open('w') as out:
    cp=subprocess.run(['openroad','-exit','-no_splash',str(W/'power.tcl')],stdout=out,stderr=subprocess.STDOUT,env=env)
(W/'evidence/power.exit').write_text(str(cp.returncode)+'\n')
print(f'W9-STATUS: extracted TT activity power exited {cp.returncode}')
raise SystemExit(cp.returncode)
