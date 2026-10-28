#!/usr/bin/env python3
"""Stream the native simulator VCD through gzip to respect the local disk floor."""
import argparse, hashlib, json, os, signal, subprocess, time
from pathlib import Path
w=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--tag',default='gate-native');a=p.parse_args()
assert a.tag.replace('-','').isalnum()
out=w/a.tag
fifo=out/'speech.vcd';gz=out/'speech.vcd.gz'
assert not fifo.exists() and not gz.exists()
os.mkfifo(fifo)
env=dict(os.environ,W8_FIFO=str(fifo),W8_GZIP=str(gz))
p=subprocess.Popen(['sh','-c','exec gzip -1 < "$W8_FIFO" > "$W8_GZIP"'],env=env,start_new_session=True)
try:rc=p.wait(timeout=1250)
except subprocess.TimeoutExpired:
    os.killpg(p.pid,signal.SIGTERM);rc=p.wait()
r={'scope':'Lossless VCD stream compression through named pipe; no waveform transformation',
   'gzip_exit_code':rc,'trace_gzip':str(gz),'pipe':str(fifo)}
if gz.exists():
 r['bytes']=gz.stat().st_size;r['sha256']=hashlib.sha256(gz.read_bytes()).hexdigest()
 if rc==0:r['gzip_integrity_exit_code']=subprocess.run(['gzip','-t',str(gz)]).returncode
(out/'stream-compression.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
