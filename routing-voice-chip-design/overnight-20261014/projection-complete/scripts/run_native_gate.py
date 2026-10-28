#!/usr/bin/env python3
"""Bounded native gate retry; retains PDK cells, mapped netlist and original harness."""
import argparse, gzip, hashlib, json, os, shutil, signal, subprocess, time
from pathlib import Path
w = Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--tag',default='gate-native');a=p.parse_args()
assert a.tag.replace('-','').isalnum()
out = w/a.tag
out.mkdir(exist_ok=False)
assert shutil.disk_usage(w).free >= 23*2**30, 'Need at least23GiB before bounded native build'
nl = out/'complete-mapped.nl.v'
with gzip.open(w/'evidence/complete-mapped.nl.v.gz', 'rb') as src, nl.open('wb') as dst:
    shutil.copyfileobj(src, dst)
cell = w.parent/'fabric-k64/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog'
cmd = ['verilator','--binary','--timing','--trace','--trace-underscore','--trace-depth','3',
       '--autoflush','--top-module','tb','-DFUNCTIONAL',
       '-DGF180MCU_FD_SC_MCU7T5V0__HOLD_V','-DGF180MCU_FD_SC_MCU7T5V0__HOLD_FUNC_V',
       '-Wno-fatal','-j','2','--Mdir',str(out/'build'),'-o','sim',
       str(cell/'primitives.v'),str(cell/'gf180mcu_fd_sc_mcu7t5v0.v'),str(nl),
       str(w/'tb/bank_model.sv'),str(w/'tb/gate_trace.sv')]
env=dict(os.environ, TMPDIR=str(w/'tmp'), OMP_NUM_THREADS='2')
receipt={'scope':'Native Verilator retry using unchanged mapped design/PDK models; trace depth3 retains mapped leaf ports',
         'command':cmd,'netlist_sha256':hashlib.sha256(nl.read_bytes()).hexdigest(),
         'version':subprocess.check_output(['verilator','--version'],text=True).strip(),'runs':[]}
def run(command, name, limit):
    start=time.monotonic();why=None
    with (out/(name+'.log')).open('w') as log:
        p=subprocess.Popen(command,cwd=w,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while p.poll() is None:
            if time.monotonic()-start>limit:why='wall-time bound'
            if shutil.disk_usage(w).free<22.5*2**30:why='22.5GiB free-space guard'
            if why:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=3)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
                break
            time.sleep(.25)
    result={'name':name,'exit_code':p.returncode,'seconds':time.monotonic()-start,'stopped_reason':why}
    receipt['runs'].append(result);(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    return p.returncode==0 and not why
if run(cmd,'compile',900):
    run([str(out/'build/sim'),'+vcd='+str(out/'speech.vcd')],'speech',300)
