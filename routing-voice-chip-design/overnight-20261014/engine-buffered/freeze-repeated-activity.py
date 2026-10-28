import json,shutil,time,hashlib,re,os
from pathlib import Path
W=Path(__file__).resolve().parent
for src,dst in [('evidence/array_port-mapped-activity.json','evidence/array_port-mapped-activity-first-pass.json'),('evidence/activity-compression.json','evidence/activity-compression-empty.json'),('logs/placed-annotation.log','logs/placed-annotation-empty.log')]:
 p=W/src;q=W/dst
 if p.exists() and not q.exists():shutil.copyfile(p,q)
p=W/'evidence/array_port-mapped-speech.saif.gz'
if p.exists() and p.stat().st_size==20:p.rename(p.with_name('empty-activity-copy.saif.gz'))
while Path('/proc/49777').exists():time.sleep(5)
log=W/'logs/lead-gate-activity.log';text=log.read_text();assert 'PASS gate_activity vectors=1 outputs=320' in text and '$finish' in text and 'exit=0' in text,text[-500:]
src=W/'evidence/array_port-mapped-speech.saif';dst=W/'evidence/array_port-mapped-speech-w9-frozen.saif';assert src.stat().st_size>1000000 and not dst.exists()
shutil.copyfile(src,dst)
with dst.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
r={'source':str(src),'frozen':str(dst),'bytes':dst.stat().st_size,'sha256':h,'source_replay_log':str(log),'source_process':49777,'reason':'Separate lead-labelled replay reopened the original shared path after W9 first pass. Completed repeat frozen under unique path.','first_pass_receipt':'evidence/array_port-mapped-activity-first-pass.json'}
(W/'evidence/frozen-activity-provenance.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
