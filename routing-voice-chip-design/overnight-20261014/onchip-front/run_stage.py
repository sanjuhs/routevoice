"""Run one recorded W1c stage, niced, with unique logs and a disk-space floor."""
from pathlib import Path
import datetime
import json
import os
import shutil
import signal
import subprocess
import sys
import time

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
RUN = Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-front'
stage = sys.argv[1]
command = json.loads((WORK/'commands.json').read_text())[stage]
stamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
logdir = WORK/'logs'
logdir.mkdir(exist_ok=True)
log = logdir/f'{stamp}-{stage}.log'
record = log.with_suffix('.json')
if stage in ('lint-full','generate-full','compile','positive') or stage.endswith('-build'):
    subprocess.run(['df','-h','/'],check=True)
    if shutil.disk_usage('/').free < 22*1024**3:
        raise SystemExit('W1c disk reserve: fewer than 22 GiB available; refusing stage to protect 20 GiB floor')
if stage == 'positive':
    # Lead clarified concurrency: one positive per worker; W1/W1b may run concurrently.
    import fcntl
    lock = (WORK/'f64.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    processes = subprocess.check_output(['ps','-axo','pid=,command='],text=True)
    for line in processes.splitlines():
        if any(Path(word).name == 'Vrv_allonchip_top_w1c' for word in line.split()[1:2]) and line.rstrip().endswith(' positive'):
            raise SystemExit('Another positive simulation is running: '+line)
    actual = RUN/'actual'
    if actual.exists() and any(actual.iterdir()):
        raise SystemExit('Refusing to append to previous actual outputs; archive explicitly first')
    actual.mkdir(exist_ok=True)
env = os.environ.copy()
env['TMPDIR'] = str(RUN/'tmp')
Path(env['TMPDIR']).mkdir(exist_ok=True)
started = time.monotonic()
info = dict(stage=stage,command=['/usr/bin/nice','-n','10',*command],cwd=str(ROOT),
            log=str(log),started=stamp,exit_code=None)
record.write_text(json.dumps(info,indent=2)+'\n')
print('W1c stage',stage,'log',log,flush=True)
with log.open('w') as output:
    process = subprocess.Popen(info['command'],cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
    info['pid'] = process.pid
    record.write_text(json.dumps(info,indent=2)+'\n')
    while process.poll() is None:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if shutil.disk_usage('/').free < 22*1024**3:
                info['stop_reason'] = 'Disk reserve fell below 22 GiB; stopping own process group to protect required 20 GiB floor'
                print(info['stop_reason'],flush=True)
                os.killpg(process.pid,signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL)
                    process.wait()
info.update(exit_code=process.returncode,elapsed_seconds=time.monotonic()-started)
record.write_text(json.dumps(info,indent=2)+'\n')
print(f'W1c-STATUS: {stage} exit={process.returncode} elapsed={info["elapsed_seconds"]:.1f}s log={log}',flush=True)
if process.returncode:
    print('\n'.join(log.read_text(errors='replace').splitlines()[-50:]))
raise SystemExit(process.returncode)
