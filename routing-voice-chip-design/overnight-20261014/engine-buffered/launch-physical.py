import subprocess,os,signal,json,hashlib
from pathlib import Path
W=Path('/workspace/rv/overnight-20261014/engine-buffered')
assert not (W/'runs/buf-v4-physical').exists()
state=W/'runs/buf-v4/25-checker-powergridviolations/state_out.json';d=json.loads(state.read_text())
r={'source_state':str(state),'state_sha256':hashlib.file_digest(state.open('rb'),'sha256').hexdigest(),'odb':d['odb'],'odb_sha256':hashlib.file_digest(Path(d['odb']).open('rb'),'sha256').hexdigest(),'config_unchanged':True,'original_mid_sta':'runs/buf-v4/26-openroad-stamidpnr','continuation_from':'OpenROAD.RepairDesignPostGPL'}
(W/'evidence/physical-continuation.json').write_text(json.dumps(r,indent=2)+'\n')
pid=int((W/'evidence/finish-v4.pid').read_text());assert b'finish.py' in Path(f'/proc/{pid}/cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
for name,args in [('flow-v4-physical',['bash','run-flow-v4-physical.sh']),('stop-original-after-sta',['python3','stop-original-after-sta.py']),('finish-v4-physical',['bash','run-finish.sh'])]:
 with (W/'logs'/f'{name}-launcher.log').open('w') as f:p=subprocess.Popen(args,cwd=W,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 (W/'evidence'/f'{name}.pid').write_text(str(p.pid)+'\n');print(name,p.pid)
