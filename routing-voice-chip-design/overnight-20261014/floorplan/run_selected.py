#!/usr/bin/env python3
"""Run one reviewed outline per partition, sequentially; enforce disk/time guards."""
from pathlib import Path
import subprocess,os,time,json,shutil,signal,sys
W=Path(__file__).resolve().parent;root=W.parent.parent
runs=sys.argv[1:] or ['custom7_sram_open_macro_off_baseline_whole_34mm','custom7_sram_open_macro_off_baseline_encoder_25mm','custom7_sram_open_macro_off_baseline_decoder_25mm']
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',VECLIB_MAXIMUM_THREADS='4')
active=None
def terminate(sig,frame):
 if active is not None and active.poll() is None:
  os.killpg(active.pid,signal.SIGTERM);active.wait()
 raise SystemExit(128+sig)
signal.signal(signal.SIGTERM,terminate)
signal.signal(signal.SIGINT,terminate)
for name in runs:
 out=W/'runs'/name;log=W/'logs'/f'{name}.log';cmd=['nice','-n','10','openroad','-exit',str(out/'floorplan.tcl')]
 if not (out/'floorplan.tcl').is_file():raise SystemExit('W3-STATUS: missing generated Tcl: '+str(out))
 start=time.time();minimum=shutil.disk_usage('/').free;stop=None
 if minimum<22*1024**3:raise SystemExit('W3-STATUS: stopped before launch: disk below22GiB')
 with log.open('w') as f:
  proc=subprocess.Popen(cmd,cwd=root,stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  active=proc
  while proc.poll() is None:
   minimum=min(minimum,shutil.disk_usage('/').free)
   if minimum<22*1024**3:stop='disk floor22GiB'
   if time.time()-start>600:stop='per-run600s bound'
   if stop:
    os.killpg(proc.pid,signal.SIGTERM);proc.wait();break
   time.sleep(2)
 receipt=dict(command=cmd,exit_code=proc.returncode,elapsed_s=time.time()-start,minimum_free_gib=minimum/1024**3,stop_reason=stop,threads=4,nice=10)
 (out/'execution.json').write_text(json.dumps(receipt,indent=2)+'\n');print('W3-STATUS:',name,receipt,flush=True)
 if proc.returncode==0:
  with (out/'geometry_check.log').open('w') as f:subprocess.run(['nice','-n','10','openroad','-python',str(W/'check_shorts.py'),str(out/'floorplan.odb')],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=120)
 if stop:break
