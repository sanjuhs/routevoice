from pathlib import Path
import os,sys,time,subprocess,signal,shutil,json,hashlib
W=Path.cwd()/'overnight-20261014/projection-complete';D=W/'sim-gate-harness-rtl';S=W.parent/'fabric-k64'; deadline=time.monotonic()+120
assert shutil.disk_usage('/').free>=22*2**30
paths=(W/'configs/sim-files.f').read_text().splitlines();assert paths[-1]==str(W/'tb/complete.sv');paths[-1]=str(W/'tb/gate_trace.sv');(D/'sim-files.f').write_text('\n'.join(paths)+'\n');(D/'source-hashes.json').write_text(json.dumps({p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},indent=2))
commands=[['verilator','--binary','--timing','--autoflush','--top-module','tb','-Wno-fatal','-j','2','--Mdir',str(D/'obj'),'-o','sim','-I'+str(S/'hf'),'-I'+str(S/'hf/ARM-VFPv2'),'-f',str(D/'sim-files.f')],[str(D/'obj/sim')]]
receipts=[]
for stage,cmd in zip(['compile','run'],commands):
 if time.monotonic()>=deadline:break
 start=time.monotonic();log=D/'logs'/f'{stage}.log';(D/f'{stage}-command.json').write_text(json.dumps(cmd,indent=2))
 with log.open('w') as f:
  p=subprocess.Popen(cmd,cwd=W,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  reason=None
  while p.poll() is None:
   if time.monotonic()>=deadline:reason='120second total compile/run deadline'
   elif shutil.disk_usage('/').free<22*2**30:reason='22GiB free storage guard'
   if reason:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=3)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    break
   time.sleep(.2)
  receipt={'stage':stage,'exit_code':p.returncode,'wall_seconds':time.monotonic()-start,'stop_reason':reason,'log':str(log),'free_disk_bytes':shutil.disk_usage('/').free};receipts.append(receipt);(D/'result.json').write_text(json.dumps(receipts,indent=2));print(json.dumps(receipt),flush=True)
 if p.returncode!=0:break
