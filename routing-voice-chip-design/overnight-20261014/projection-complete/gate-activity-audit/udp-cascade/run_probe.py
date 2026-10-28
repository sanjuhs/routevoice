#!/usr/bin/env python3
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--mode',choices=['verilator','iverilog'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
os.environ['OMP_NUM_THREADS']='1'
a.output.mkdir(parents=True,exist_ok=False);out=a.output.resolve()
base=a.root/'overnight-20261014/fabric-k64/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog'
sources=[base/'primitives.v',base/'gf180mcu_fd_sc_mcu7t5v0.v',Path(__file__).resolve().with_name('tb.sv')]
sources=[x.resolve() for x in sources]
defines=['-DFUNCTIONAL','-DGF180MCU_FD_SC_MCU7T5V0__HOLD_V','-DGF180MCU_FD_SC_MCU7T5V0__HOLD_FUNC_V']
exe=shutil.which(a.mode)
version=subprocess.run([exe,'--version' if a.mode=='verilator' else '-V'],capture_output=True,text=True,timeout=10)
(out/'version.log').write_text(version.stdout+version.stderr)
if a.mode=='verilator':
 command=[exe,*defines,'--binary','--timing','--trace','--trace-underscore','--top-module','tb','-Wno-fatal','-j','1','--Mdir',str(out/'obj'),'-o','sim',*map(str,sources)]
 sim=[str(out/'obj/sim')]
else:
 command=[exe,*defines,'-g2012','-s','tb','-o',str(out/'sim'),*map(str,sources)]
 sim=[shutil.which('vvp'),str(out/'sim')]
receipt={'mode':a.mode,'command':command,'simulation_command':sim,'sources_sha256':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources},'scope':'Tiny exact-cell cascade diagnostic; not projection correctness evidence'}
with (out/'compile.log').open('w') as f:
 r=subprocess.run(command,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
receipt['compile_exit']=r.returncode
if r.returncode==0:
 with (out/'simulation.log').open('w') as f:
  r=subprocess.run(sim,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=30)
 receipt['simulation_exit']=r.returncode
 log=(out/'simulation.log').read_text();receipt['pass']='PASS exact GF180 two-FF cascade' in log and r.returncode==0
 print(log)
(out/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k in ['mode','compile_exit','simulation_exit','pass']}))
