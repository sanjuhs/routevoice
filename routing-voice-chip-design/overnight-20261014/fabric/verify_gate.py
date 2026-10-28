#!/usr/bin/env python3
"""Bounded zero-delay GF180 mapped-netlist verification with original-byte oracle."""
import hashlib,json,os,re,shutil,signal,subprocess,sys,time
from pathlib import Path
r=Path(__file__).resolve().parent;variant=sys.argv[1];netlist=Path(sys.argv[2]).resolve();assert netlist.is_file()
rows=64 if '64x320' in variant else 320
activity='--activity' in sys.argv
compile_only='--compile-only' in sys.argv
cell_pins='--cell-pins' in sys.argv
min_free_gib=float(os.environ.get('W2_GATE_MIN_FREE_GIB','23' if cell_pins else '22'));assert min_free_gib>=22
period=int(sys.argv[sys.argv.index('--period')+1]) if '--period' in sys.argv else 20
assert period>0 and period%2==0
tag='gate-activity' if activity else 'gate'
bench=r/'tb'/f'tb_{tag}_{variant}.sv'
text=(r/'tb/tb.sv').read_text().replace('`include "dump_memories.vh"\n','')
text=text.replace('always #10 clk=~clk;',f'always #{period//2} clk=~clk;')
text=text.replace('#2000000;',f'#{max(2000000,period*32*(rows+400))};')
if activity:
 text=text.replace('for(v=0;v<32;v=v+1)','for(v=4;v<9;v=v+1)')
 text=text.replace('$dumpfile(tracefile);$dumpvars(0,tb);','$dumpfile(tracefile);').replace('   $dumpoff;','')
 text=text.replace('if(trace_on && v==4) $dumpon;','if(trace_on && v==4) $dumpvars(0,tb);').replace('if(trace_on && v==9) $dumpoff;','')
 text=text.replace('VERIFICATION PASS vectors=32 random=20','GATE_ACTIVITY PASS vectors=5 random=5')
bench.write_text(text)
lib=r/'pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog';obj=r/'tb'/f'{tag.replace("-","_")}_obj_{variant}'
command=['verilator','--binary','--timing','--top-module','tb','--build-jobs','3' if cell_pins else '4','--threads','1','--output-split','15000','--output-split-cfuncs','5000','-Wno-fatal','-DFUNCTIONAL',f'-DDUT={variant}',f'-DROWS={rows}','--Mdir',str(obj),str(lib/'primitives.v'),str(lib/'gf180mcu_fd_sc_mcu7t5v0.v'),str(netlist),str(bench)]
if variant.endswith('_dp'):command.append('-DEXTERNAL')
wave=r/'vectors'/f'{variant}.gate-power-{period}ns.vcd'
if activity:command.extend(['--trace','--trace-depth','3','--trace-max-width','65536'])
if cell_pins:command.append('--trace-underscore')
simulate=[str(obj/'Vtb')]+([f'+vcd={wave}'] if activity else [])
start=time.time();receipt={'variant':variant,'level':'Zero-delay mapped netlist, GF180 FUNCTIONAL models, Verilator (two-state); no SDF timing simulation','netlist':str(netlist),'netlist_sha256':hashlib.sha256(netlist.read_bytes()).hexdigest(),'clock_period_ns':period,'activity_vcd':str(wave) if activity else None,'thread_caps':{'build':3 if cell_pins else 4,'simulation':1},'limit_seconds':1200,'phases':[]};reason=None
for phase,args in ([('compile',command)] if compile_only else [('compile',command),('simulate',simulate)]):
 if shutil.disk_usage(r).free<min_free_gib*1024**3:reason=f'disk safety margin below {min_free_gib} GiB';break
 log=r/'logs'/f'{variant}.{tag}-{phase}.log';entry={'phase':phase,'command':['nice','-n','10']+args,'log':str(log.relative_to(r))};receipt['phases'].append(entry)
 with log.open('w') as out:
  env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',NUMEXPR_NUM_THREADS='1',TMPDIR=str(r/'tmp'),XDG_CACHE_HOME=str(r/'cache'))
  proc=subprocess.Popen(entry['command'],cwd=r,stdout=out,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  try:
   while proc.poll() is None:
    if shutil.disk_usage(r).free<min_free_gib*1024**3:reason=f'disk safety margin below {min_free_gib} GiB';break
    if time.time()-start>1200:reason='gate check time limit 1200 seconds';break
    time.sleep(3)
  except BaseException as e:reason=f'interrupted: {e}'
  if reason:
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  entry['exit_code']=proc.returncode
 if reason or proc.returncode:break
receipt.update(elapsed_seconds=time.time()-start,stop_reason=reason)
log=r/'logs'/f'{variant}.{tag}-simulate.log'
if receipt['phases'] and receipt['phases'][-1]['phase']=='simulate' and receipt['phases'][-1].get('exit_code')==0:
 m=re.search(r'(?:VERIFICATION|GATE_ACTIVITY) PASS vectors=(\d+) random=(\d+) checks=(\d+) failures=(\d+)',log.read_text())
 if m:receipt['verification']=dict(zip(['vectors_passed','random_vectors','exact_comparisons','failures'],map(int,m.groups())))
(r/'evidence'/f'{variant}.{tag}-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('W2-STATUS: Gate check ended',json.dumps(receipt),flush=True)
raise SystemExit(0 if receipt.get('verification',{}).get('failures')==0 or (compile_only and not reason and receipt['phases'][-1].get('exit_code')==0) else 1)
