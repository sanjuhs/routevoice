import subprocess,os,signal
from pathlib import Path
W=Path('/workspace/rv/overnight-20261014/engine-buffered')
assert not (W/'evidence/synthesis-fanout.json').exists(),'Mapping completed; inspect before restart'
pid=int((W/'evidence/watch-gate-v4.pid').read_text());cmd=Path(f'/proc/{pid}/cmdline').read_bytes();assert b'watch-gate-v4.sh' in cmd
os.kill(pid,signal.SIGTERM)
with (W/'logs/watch-gate-v4-launcher.log').open('a') as f:p=subprocess.Popen(['bash','watch-gate-v4.sh'],cwd=W,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(W/'evidence/watch-gate-v4.pid').write_text(str(p.pid)+'\n');print('Restarted own synthesis watcher',p.pid)
