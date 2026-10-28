from pathlib import Path
import subprocess,time,os,signal,json
O=Path(__file__).resolve().parent/'v1';pid=42367
while True:
 p=subprocess.run(['ps','-p',str(pid),'-o','etime=,command='],capture_output=True,text=True)
 if p.returncode or not p.stdout.strip():break
 elapsed,cmd=p.stdout.strip().split(None,1)
 assert 'canonical.spice W5_DECODED_TILE_FLAT' in cmd,cmd
 parts=list(map(int,elapsed.split(':')));seconds=sum(v*60**i for i,v in enumerate(parts[::-1]))
 if seconds>=600:
  (O/'monolithic-bound.json').write_text(json.dumps({'pid':pid,'action':'SIGTERM after600s wallclock cap','elapsed_seconds':seconds,'reason':'CPU-active large flat graph did not complete within bounded local allocation; logs preserved; compositional proof run separately'},indent=2));os.kill(pid,signal.SIGTERM);print('W5-STATUS: monolithic Netgen stopped at',seconds,'seconds; outputs preserved',flush=True);break
 time.sleep(min(5,600-seconds))
