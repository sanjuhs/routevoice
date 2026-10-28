#!/usr/bin/env python3
"""Overnight RunPod helper: create / list / ssh-info / delete CPU pods, plus a hard spend guard.

Budget: $30 new spend for the 14 Oct overnight run. The guard terminates every pod whose name
starts with PREFIX once estimated cumulative spend reaches CAP_USD or the wall clock passes DEADLINE.
Spend is estimated conservatively from each pod's hourly rate x time since we first saw it, plus a
fixed per-pod allowance for storage, and persisted to spend.json so it survives restarts.
"""
import importlib.util, json, sys, time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('api', ROOT / 'scripts/taalas_runpod_readonly_v1.py')
api = importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

PREFIX = 'rv-overnight-'
CAP_USD = 58.0            # user raised the cap to $60 on 21 Oct 2026; $2 margin
DEADLINE = datetime.fromisoformat('2026-10-23T18:00:00+05:30').timestamp()
SPEND = HERE / 'spend.json'
LOG = HERE / 'guard.log'
API = 'https://api.runpod.io/v2/pods'


def log(msg):
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    with LOG.open('a') as f: f.write(line + '\n')


def pods():
    r = api.request(API)
    items = r if isinstance(r, list) else r.get('pods', r.get('data', []))
    return [p for p in items if str(p.get('name', '')).startswith(PREFIX)]


def load_spend():
    return json.loads(SPEND.read_text()) if SPEND.exists() else {'pods': {}, 'total_usd': 0.0}


def update_spend(live):
    s = load_spend(); now = time.time()
    for p in live:
        e = s['pods'].setdefault(p['id'], {'name': p['name'], 'first_seen': now, 'rate': float(p.get('cost') or p.get('costPerHr') or 0), 'usd': 0.0})
        e['rate'] = max(e['rate'], float(p.get('cost') or p.get('costPerHr') or 0))
        e['usd'] = round(e['rate'] * (now - e['first_seen']) / 3600 + 0.10, 4)   # +$0.10 storage/rounding allowance
        e['last_seen'] = now
    s['total_usd'] = round(sum(e['usd'] for e in s['pods'].values()), 4)
    s['updated'] = datetime.now().isoformat(timespec='seconds')
    SPEND.write_text(json.dumps(s, indent=2) + '\n')
    return s


def delete(pod_id):
    try:
        api.request(f'{API}/{pod_id}', None, 'DELETE')
    except json.JSONDecodeError:
        pass  # DELETE returns an empty body on success
    log(f'DELETE requested pod={pod_id}')


def create(name, vcpu=32, flavor='cpu3g', disk=80):
    s = update_spend(pods())
    assert s['total_usd'] < CAP_USD - 3, f"refusing: spend {s['total_usd']} too close to cap"
    body = dict(name=PREFIX + name, cpu=dict(id=flavor, vcpuCount=vcpu), image='runpod/base:1.0.2-ubuntu2404',
                disk=disk, ports=['22/tcp'], startSsh=True, startJupyter=False, cloud='SECURE')
    r = api.request(API, body, 'POST')
    log(f"CREATE {body['name']} {flavor}x{vcpu} -> id={r.get('id')} costPerHr={r.get('costPerHr')}")
    update_spend(pods())
    return r


def info(pod_id):
    r = api.request(f'{API}/{pod_id}')
    keep = {k: r.get(k) for k in ('id', 'name', 'status', 'cost', 'ssh', 'machine', 'lastStatusChange')}
    print(json.dumps(keep, indent=2))


def guard():
    log(f'GUARD start cap=${CAP_USD} deadline={datetime.fromtimestamp(DEADLINE).isoformat()}')
    while True:
        try:
            live = pods(); s = update_spend(live)
            over = s['total_usd'] >= CAP_USD; late = time.time() >= DEADLINE
            if (over or late) and live:
                log(f"GUARD trigger over={over} late={late} spend={s['total_usd']}")
                for p in live: delete(p['id'])
            if late and not live:
                log('GUARD deadline passed and no pods remain; exiting'); return
        except Exception as e:  # keep guarding through transient API errors
            log(f'GUARD error {e!r}')
        time.sleep(60)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'list': print(json.dumps([{k: p.get(k) for k in ('id', 'name', 'status', 'cost', 'ssh')} for p in pods()], indent=2)); print(json.dumps(update_spend(pods()), indent=2))
    elif cmd == 'create': create(*sys.argv[2:3], **({'vcpu': int(sys.argv[3])} if len(sys.argv) > 3 else {}))
    elif cmd == 'info': info(sys.argv[2])
    elif cmd == 'delete': delete(sys.argv[2])
    elif cmd == 'guard': guard()
    else: sys.exit('usage: rp.py list|create NAME [VCPU]|info ID|delete ID|guard')
