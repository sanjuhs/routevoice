#!/usr/bin/env python3
"""Reuse the compiled gate testbench, streaming its VCD to gzip to bound disk use."""
import gzip,hashlib,json,os,shutil,signal,subprocess,threading,time,sys,re
from pathlib import Path
tag='gate-cell-pins' if '--cell-pins' in sys.argv else 'gate'
r=Path(__file__).resolve().parent;v='rv_fixed_proj64x320_rom';fifo=r/'tmp/gate-activity.fifo';out=r/'vectors'/f'{v}.{tag}-power-200ns.vcd.gz';log=r/'logs'/f'{v}.{tag}-activity-stream.log'
assert not fifo.exists() and not out.exists()
build=json.loads((r/'evidence'/f'{v}.gate-activity-verification.json').read_text());assert build['clock_period_ns']==200 and build['phases'][-1]['exit_code']==0
if tag!='gate':assert '--trace-underscore' in build['phases'][0]['command']
os.mkfifo(fifo);errors=[]
def compress():
 try:
  with fifo.open('rb') as src,gzip.open(out,'wb',compresslevel=1) as dst:shutil.copyfileobj(src,dst,1024*1024)
 except BaseException as e:errors.append(str(e))
th=threading.Thread(target=compress,daemon=True);th.start();cmd=['nice','-n','10',str(r/'tb'/f'gate_activity_obj_{v}'/'Vtb'),f'+vcd={fifo}'];start=time.time();reason=None
with log.open('w') as f:
 p=subprocess.Popen(cmd,cwd=r,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 while p.poll() is None:
  if shutil.disk_usage(r).free<(23 if tag!='gate' else 22)*1024**3:reason='auxiliary free-disk margin reached';break
  if time.time()-start>1200:reason='1200 second timeout';break
  time.sleep(3)
 if reason:
  os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=20)
 th.join(timeout=30)
fifo.unlink();d=dict(command=cmd,exit_code=p.returncode,stop_reason=reason,elapsed_seconds=time.time()-start,compression_errors=errors,trace=str(out),simulation_log=str(log),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),level='Mapped synthesis netlist zero-delay GF180 FUNCTIONAL models; five random vectors at 200 ns with clocked output reads')
m=re.search(r'GATE_ACTIVITY PASS vectors=(\d+) random=(\d+) checks=(\d+) failures=(\d+)',log.read_text())
if m:d['verification']=dict(zip(['vectors_passed','random_vectors','exact_comparisons','failures'],map(int,m.groups())))
(r/'evidence'/f'{tag}-activity-stream.json').write_text(json.dumps(d,indent=2)+'\n');print('W2-STATUS:',json.dumps(d));print(log.read_text());raise SystemExit(0 if p.returncode==0 and not reason and not errors and m else 1)
