"""One bounded observation of this worker's detached positive run."""
import argparse,json,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--wait',type=float,default=0);a=p.parse_args();assert 0<=a.wait<=50
W=Path(__file__).resolve().parent
time.sleep(a.wait)
r=sorted((W/'logs').glob('*positive.json'))[-1];d=json.loads(r.read_text())
lines=Path(d['log']).read_text(errors='replace').splitlines()
status={'record':str(r),'exit_code':d['exit_code'],'free_GiB':round(shutil.disk_usage('/').free/1024**3,2),'tail':lines[-4:]}
if d['exit_code'] is None:
 ps=subprocess.run(['ps','-p',str(d['pid']),'-o','pid=,etime=,%cpu=,rss=,nice=,stat='],capture_output=True,text=True)
 status['process']=ps.stdout.strip();status['process_present']=ps.returncode==0
(W/'positive-status.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2))
