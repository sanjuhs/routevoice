import subprocess,shutil,time,os,signal,json,sys,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent;name=sys.argv[1];assert '/' not in name
receipt=json.loads((W/(name+'.receipt.json')).read_text());free=shutil.disk_usage(W).free
assert free-receipt['bytes']>=22.25*2**30,(free,receipt['bytes'])
cmd=[str(W.parent/'runpod/pod-rsync'),'pod:/workspace/rv/overnight-20261014/engine-buffered/'+name,str(W)+'/']
p=subprocess.Popen(cmd,start_new_session=True)
while p.poll() is None:
 if shutil.disk_usage(W).free<22.25*2**30:
  os.killpg(p.pid,signal.SIGTERM);p.wait();raise SystemExit('Stopped download at disk guard')
 time.sleep(2)
assert p.returncode==0,p.returncode
with (W/name).open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
assert h==receipt['sha256'];print('W9-STATUS: downloaded and verified',name,'free GiB',shutil.disk_usage(W).free/2**30)
