#!/usr/bin/env python3
"""Bounded process-group supervisor; preserve every failed log and partial run."""
import json, os, signal, shutil, subprocess, sys, time
from pathlib import Path
r=Path(__file__).resolve().parent
variant=sys.argv[1];tag=sys.argv[2] if len(sys.argv)>2 else 'v1'
limit=int(os.environ.get('W2_LIMIT_SECONDS','7200'))
thread_limit=int(os.environ.get('W2_NUM_THREADS','8'));assert 1<=thread_limit<=8
min_free_gib=float(os.environ.get('W2_MIN_FREE_GIB','22'));assert min_free_gib>=22
log=r/'logs'/f'{variant}-{tag}.flow.log'; receipt=r/'evidence'/f'{variant}-{tag}.supervisor.json'
start=time.time(); command=['bash',str(r/'run_flow.sh'),variant,tag]
if shutil.disk_usage(r).free<min_free_gib*1024**3:
    result={'command':command,'status':'not_started','stop_reason':f'disk safety margin: free below {min_free_gib:g} GiB','minimum_free_bytes':shutil.disk_usage(r).free,'exit_code':None,'elapsed_seconds':0,'limit_seconds':limit,'thread_limit':thread_limit,'nice':10,'minimum_required_free_gib':min_free_gib,'start_unix':start,'flow_controls':{k:os.environ[k] for k in ['W2_FROM_STEP','W2_TO_STEP','W2_INITIAL_STATE','W2_NUM_THREADS','W2_CONFIG_PATH','W2_VCD','W2_MIN_FREE_GIB','W2_LIMIT_SECONDS'] if k in os.environ}}
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    log.write_text(f'W2-STATUS: NOT STARTED: disk safety margin requires {min_free_gib:g} GiB free; no EDA subprocess launched.\n'+json.dumps(result,indent=2)+'\n')
    print(log.read_text(),flush=True)
    raise SystemExit(2)
with log.open('w') as out:
    proc=subprocess.Popen(command,cwd=r,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    reason=None; minimum=shutil.disk_usage(r).free
    try:
        while proc.poll() is None:
            free=shutil.disk_usage(r).free;minimum=min(minimum,free)
            if free<min_free_gib*1024**3: reason=f'disk safety margin: free below {min_free_gib:g} GiB';break
            if time.time()-start>limit: reason=f'time limit {limit} seconds';break
            time.sleep(5)
    except BaseException as e:
        reason=f'supervisor interrupted: {e}'
    if reason:
        os.killpg(proc.pid,signal.SIGTERM)
        try: proc.wait(timeout=20)
        except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL);proc.wait()
    result={'command':command,'log':str(log),'exit_code':proc.returncode,'stop_reason':reason,'elapsed_seconds':time.time()-start,'minimum_free_bytes':minimum,'limit_seconds':limit,'thread_limit':thread_limit,'nice':10,'minimum_required_free_gib':min_free_gib,'start_unix':start,'flow_controls':{k:os.environ[k] for k in ['W2_FROM_STEP','W2_TO_STEP','W2_INITIAL_STATE','W2_NUM_THREADS','W2_CONFIG_PATH','W2_VCD','W2_MIN_FREE_GIB','W2_LIMIT_SECONDS'] if k in os.environ}}
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print('W2-STATUS: physical attempt ended '+json.dumps(result),flush=True)
    sys.exit(0 if proc.returncode==0 and not reason else 1)
