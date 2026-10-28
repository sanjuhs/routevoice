#!/usr/bin/env python3
"""One-shot monitor of an existing job, then its unchanged binary's idle trace."""
import os,time,json,re,hashlib,subprocess,signal,shutil
from pathlib import Path
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
W=Path('/workspace/rv/overnight-20261014/projection-complete');A=W/'gate-activity-audit';A.mkdir(exist_ok=True)
start=time.monotonic();events=A/'events.jsonl'
def event(kind,**kw):
 r={'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'kind':kind,**kw}
 with events.open('a') as f:f.write(json.dumps(r)+'\n')
 print(json.dumps(r),flush=True)
def save(name,r):(A/name).write_text(json.dumps(r,indent=2)+'\n')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for x in iter(lambda:f.read(8*1024*1024),b''):h.update(x)
 return h.hexdigest()
def pid_alive(pid):
 try:os.kill(pid,0);return True
 except ProcessLookupError:return False

def trace_receipt(path):
 before=path.stat();h=hashlib.sha256();stack=[];declarations=0;scopes=0;header_samples=[];pin_samples=[];units=[];first=last=None;header_end=False;var_width_bits=0
 with path.open('rb') as f:
  for line in f:
   h.update(line);tokens=line.split()
   if b'$timescale' in line:units.append(line.decode().strip())
   if tokens and tokens[0]==b'$scope':
    stack.append(tokens[2].decode());scopes+=1
    if len(stack)>=3 and len(header_samples)<12:header_samples.append('/'.join(stack))
   elif tokens and tokens[0]==b'$upscope':stack.pop()
   elif tokens and tokens[0]==b'$var':
    declarations+=1;var_width_bits+=int(tokens[2])
    if len(stack)>=3 and len(pin_samples)<40:pin_samples.append({'scope':'/'.join(stack),'reference':b' '.join(tokens[4:-1]).decode(),'width':int(tokens[2])})
   if tokens and tokens[0]==b'$enddefinitions':header_end=True;break
  if not header_end:raise ValueError('Incomplete VCD header: '+str(path))
  tail=b''
  for block in iter(lambda:f.read(8*1024*1024),b''):
   h.update(block);buf=tail+block;cut=buf.rfind(b'\n')
   if cut<0:tail=buf;continue
   complete=buf[:cut+1];tail=buf[cut+1:]
   for m in re.finditer(rb'(?m)^#(\d+)\r?$',complete):
    value=int(m[1]);first=value if first is None else first;last=value
  if tail.startswith(b'#'):value=int(tail[1:]);first=value if first is None else first;last=value
 after=path.stat()
 if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise RuntimeError('Trace changed while audited')
 text=' '.join(units);m=re.search(r'\$timescale\s*(\d+)\s*(s|ms|us|ns|ps|fs)',text)
 scale=int(m[1])*{'s':1,'ms':1e-3,'us':1e-6,'ns':1e-9,'ps':1e-12,'fs':1e-15}[m[2]] if m else None
 return {'path':str(path),'bytes':before.st_size,'sha256':h.hexdigest(),'mtime_ns':before.st_mtime_ns,'header_scope_count':scopes,'header_variable_declarations':declarations,'declared_bits_including_aliases':var_width_bits,'sample_actual_leaf_scopes':header_samples,'sample_actual_leaf_pins':pin_samples,'timescale_declaration':units,'timescale_seconds':scale,'first_timestamp':first,'last_timestamp':last,'duration_seconds':(last-first)*scale if first is not None and scale is not None else None,'scope_for_STA_to_test':'tb/dut','STA_annotation_coverage_measured':False,'zero_delay_gate_activity':True,'header_and_values_not_rewritten':True,'file_stable_during_read':True}

event('monitor_started',pid=13208,cpu_affinity=sorted(os.sched_getaffinity(0)),source_reading='Previously completed W8 reading; unchanged scope',remote_free_GiB=shutil.disk_usage(W).free/2**30)
status=W/'logs/gate-trace.exit';speechlog=W/'logs/gate-trace-simulation.log'
while not status.exists():
 if not pid_alive(13208):event('existing_job_exited_without_receipt');save('failure.json',{'reason':'Existing job13208 no longer present and exit receipt absent'});raise SystemExit(2)
 if time.monotonic()-start>7200:event('bounded_monitor_timeout');save('failure.json',{'reason':'2hour monitor bound expired; existing job untouched'});raise SystemExit(3)
 event('waiting_existing_job',elapsed_seconds=round(time.monotonic()-start),remote_free_GiB=round(shutil.disk_usage(W).free/2**30,3))
 time.sleep(30)
rc=int(status.read_text().strip());text=speechlog.read_text()
if rc!=0 or not re.search(r'PASS gate trace vectors=1 outputs=320',text):
 event('speech_gate_not_qualified',exit_code=rc,log_tail=text[-1500:]);save('failure.json',{'reason':'Speech run did not exit0 with all320outputmatches','exit_code':rc,'log_tail':text[-1500:]});raise SystemExit(4)
binary=W/'gate-trace/sim';binary_sha=sha(binary)
speech={'exit_code':rc,'output_matches':320,'vectors':1,'pass_line':[line for line in text.splitlines() if 'PASS' in line],'simulation_log_sha256':sha(speechlog),'binary_sha256':binary_sha,'gate_netlist_sha256':sha(W/'runs/complete-v3/02-yosys-synthesis/rv_k64_projection_complete.nl.v'),'gate_netlist_stage':'mapped synthesis complete-v3, not routed','source_vector':'vector0 from saved captured-speech activation image; no new speech capture','SDF_annotated':False}
save('speech-correctness.json',speech);event('speech_gate_pass',output_matches=320,binary_sha256=binary_sha)
idle_vcd=W/'evidence/gate-idle.vcd';idle_log=W/'logs/gate-idle-simulation.log';idle_exit=W/'logs/gate-idle.exit'
if idle_vcd.exists() or idle_log.exists() or idle_exit.exists():raise RuntimeError('Refusing to overwrite existing idle evidence')
if shutil.disk_usage(W).free<9*2**30:raise RuntimeError('Insufficient guarded space to start idle')
cmd=[str(binary),'+idle','+vcd='+str(idle_vcd)];reason=None;beg=time.monotonic()
with idle_log.open('w') as f:
 proc=subprocess.Popen(cmd,cwd=W,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 event('idle_started',pid=proc.pid,command=cmd,cpu_affinity=sorted(os.sched_getaffinity(proc.pid)),maximum_seconds=600,stop_free_GiB=9,hard_floor_GiB=8)
 while proc.poll() is None:
  free=shutil.disk_usage(W).free
  if time.monotonic()-beg>=600:reason='600second idle runtime bound'
  if free<9*2**30:reason='9GiB guard reached to preserve8GiB floor'
  if reason:
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   break
  time.sleep(1)
 rc=proc.wait()
idle_exit.write_text(str(rc)+'\n');idle_text=idle_log.read_text();receipt={'exit_code':rc,'stop_reason':reason,'wall_seconds':time.monotonic()-beg,'simulation_log_tail':idle_text[-2000:],'simulation_log_sha256':sha(idle_log),'binary_sha256_before':binary_sha,'binary_sha256_after':sha(binary),'completed_projections':0,'idle_pass_line_seen':'PASS gate idle cycles=10000 no projection started' in idle_text,'requested_idle_clocks':10000,'remote_free_GiB_after':shutil.disk_usage(W).free/2**30,'SDF_annotated':False,'cpu_affinity':sorted(os.sched_getaffinity(0))}
save('idle-execution.json',receipt);event('idle_finished',exit_code=rc,stop_reason=reason,wall_seconds=round(receipt['wall_seconds'],3))
# Sources are now stable; metadata/hashes use one CPU and retain large raw VCDs remotely.
for name,path in [('speech',W/'evidence/gate-speech.vcd'),('idle',idle_vcd)]:
 if path.exists():
  r=trace_receipt(path);r['workload_kind']='active' if name=='speech' else 'idle';r['execution_exit_code']=speech['exit_code'] if name=='speech' else rc;save(name+'-vcd.json',r);event('trace_metadata_saved',trace=name,bytes=r['bytes'],duration_seconds=r['duration_seconds'],sha256=r['sha256'])
summary={'speech_correctness':speech,'idle_execution':receipt,'STA_run':False,'raw_VCDs_kept_remote':True,'ready_for_power_annotation':rc==0 and reason is None and receipt['idle_pass_line_seen'],'full_array_internal_power_characterized':False}
save('results.json',summary);event('audit_finished',ready_for_power_annotation=summary['ready_for_power_annotation'])
