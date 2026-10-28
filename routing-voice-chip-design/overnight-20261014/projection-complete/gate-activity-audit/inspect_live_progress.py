#!/usr/bin/env python3
"""Streaming snapshot of selected VCD controls; not stable-trace evidence."""
import collections,json,os,re,sys,time
from pathlib import Path
if hasattr(os,'sched_getaffinity'):os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
p=Path(sys.argv[1]);out=Path(sys.argv[2]);limit=p.stat().st_size
selected={};stack=[];last={};changes=collections.Counter();first={};history={};timestamp=0
names={'_00007_','_01588_','_01587_','_01644_','_01586_','r','c','elapsed','v','reads','stalls','clk','reset','start','step_enable','in_valid','in_ready','out_ready','out_valid','out_data','out_column','busy','phase','read_row','array_row','pc','pc_logic','evaluate','engine_step','engine_in_ready','engine_in_valid','array_read_enable','frozen_index_bits','array_out','wordline'}
with p.open('rb') as f:
 while True:
  line=f.readline()
  if not line:raise RuntimeError('Incomplete header')
  t=line.split()
  if not t:continue
  if t[0]==b'$scope':stack.append(t[2].decode())
  elif t[0]==b'$upscope':stack.pop()
  elif t[0]==b'$var':
   name=t[4].decode().lstrip('\\');depth=len(stack)
   wanted=(depth<=3 and (name.split('[')[0] in names or re.fullmatch(r'engine\.(state|row|input_row|in_ready|busy|phase|start|reset|step_enable|in_valid|out_valid)(\[[0-9]+\])?',name)))
   wanted = wanted or any(scope in {'_10470_','_03969_','_03968_','_03967_','_05000_','_05001_'} for scope in stack)
   if wanted:
    code=t[3];selected.setdefault(code,[]).append({'scope':'/'.join(stack),'name':name,'width':int(t[2])});history.setdefault(code,collections.deque(maxlen=8))
  elif t[0]==b'$enddefinitions':break
 for line in f:
  if f.tell()>limit:break
  line=line.strip()
  if not line:continue
  if line[:1]==b'#':timestamp=int(line[1:]);continue
  if line[:1] in (b'b',b'B',b'r'):
   pieces=line.split()
   if len(pieces)!=2:continue
   value=pieces[0][1:];code=pieces[1]
  else:value=line[:1];code=line[1:]
  if code not in selected:continue
  if last.get(code)!=value:
   changes[code]+=1;first.setdefault(code,{'time_ps':timestamp,'value':value.decode()})
   history[code].append({'time_ps':timestamp,'value':value.decode()})
  last[code]=value

def value_summary(value):
 s=value.decode()
 if len(s)<=64:return {'bits':s,'integer':int(s,2) if set(s)<={'0','1'} else None}
 return {'bits_count':len(s),'one_bits':s.count('1'),'unknown_bits':sum(s.count(v) for v in 'xz'),'first32':s[:32],'last32':s[-32:]}
rows=[]
for code,aliases in selected.items():
 rows.append({'value_identifier':code.decode(),'aliases':aliases,'last_value':value_summary(last[code]) if code in last else None,'distinct_value_events':changes[code], 'first_value':{'time_ps':first[code]['time_ps'],**value_summary(first[code]['value'].encode())} if code in first else None,'recent_changes':[{'time_ps':v['time_ps'],**value_summary(v['value'].encode())} for v in history[code]]})
r={'status':'live streaming diagnostic snapshot, not a finalized VCD audit','source':str(p),'read_limit_bytes':limit,'latest_timestamp_ps_in_snapshot':timestamp,'source_size_after':p.stat().st_size,'UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'signals':rows}
out.write_text(json.dumps(r,indent=2)+'\n')
for row in rows:print(json.dumps({'names':[x['scope']+'/'+x['name'] for x in row['aliases']],'last':row['last_value'],'changes':row['distinct_value_events'],'last_change_ps':row['recent_changes'][-1]['time_ps'] if row['recent_changes'] else None}))
print(json.dumps({'latest_timestamp_ps':timestamp,'selected_identifiers':len(selected)}))
