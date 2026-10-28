#!/usr/bin/env python3
"""W10 fresh mapped replay and SAIF. No RTL/SAIF evidence is reused as a pass."""
import argparse, concurrent.futures, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
from scale_saif import scale
HERE=Path(__file__).resolve().parent
W10=HERE.parent
REPO=HERE.parents[3]
COUNTS={'inputs.hex':69120,'expected.hex':17280,'activation-scales.hex':54,'integer-all.hex':17280}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def write(p,obj): p.write_text(json.dumps(obj,indent=2)+'\n')

def checked_fixture(p,expected):
    if not p.is_file(): raise ValueError(f'Missing fixture: {p}')
    actual=sha(p)
    if actual!=expected: raise ValueError(f'Fixture hash mismatch: {p}: {actual}')
    words=p.read_text().split()
    if len(words)!=COUNTS[p.name] or any(not re.fullmatch('[0-9a-fA-F]+',w) for w in words):
        raise ValueError(f'Unexpected fixture format/length: {p}')
    return dict(path=str(p),sha256=actual,words=len(words))

def run(cmd,log,cwd,env,timeout):
    with log.open('w') as f:
        f.write('ARGV '+json.dumps(cmd)+'\n');f.flush()
        return subprocess.run(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout).returncode

def compile_bench(kind,a,nl,cells,out,env):
    obj=out/f'obj-{kind}'
    bench=out/('gate_sharded.sv' if kind=='full' else 'activity_array_port.sv')
    cmd=['verilator','--binary','--timing','--autoflush','--output-groups','0','--top-module','tb',
         '-DFUNCTIONAL','-DGF180MCU_FD_SC_MCU7T5V0__HOLD_V','-DGF180MCU_FD_SC_MCU7T5V0__HOLD_FUNC_V',
         '-Wno-fatal','-j',str(a.jobs),'--Mdir',str(obj),'-o','sim']
    if kind=='activity':cmd+=['--trace-saif','--trace-underscore','--trace-depth','2']
    cmd += [str(cells/'primitives.v'),str(cells/'gf180mcu_fd_sc_mcu7t5v0.v'),str(nl),str(bench),str(out/'index_fabric.sv')]
    rc=run(cmd,out/f'{kind}-compile.log',out,env,a.timeout)
    if rc: raise RuntimeError(f'{kind} compile exit {rc}; see {out}/{kind}-compile.log')
    return obj/'sim'

def full(a,nl,cells,out,env):
    sim=compile_bench('full',a,nl,cells,out,env)
    plan=json.loads((out/'shard-plan.json').read_text())
    def shard(bounds):
        first,last=bounds; log=out/f'shard-{first:02d}-{last:02d}.log'
        cmd=[str(sim),f'+w10_first={first}',f'+w10_last={last}',f'+w10_rng={plan["rng_seeds"][first]:08x}']
        rc=run(cmd,log,out,env,a.timeout); txt=log.read_text()
        rows=[tuple(map(int,x)) for x in re.findall(r'^vector=(\d+) cycles=(\d+) reads=(\d+)',txt,re.M)]
        ok=(rc==0 and '$finish' in txt and f'PASS shard first={first} last={last} vectors={last-first} outputs={(last-first)*320}' in txt
            and [v for v,_,_ in rows]==list(range(first,last))
            and all(c==plan['cycles'][v] and r==1280 for v,c,r in rows))
        return dict(first=first,last=last,exit=rc,passed=ok,log=str(log),vectors=rows)
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(a.jobs,8)) as pool:
        results=list(pool.map(shard,plan['ranges']))
    seen=[v for r in results for v,_,_ in r['vectors']]
    r=dict(passed=all(x['passed'] for x in results) and sorted(seen)==list(range(54)),
           vectors=len(seen),outputs=len(seen)*320,shards=results,aborts_per_shard=4,
           netlist_sha256=sha(nl),source_clock_period_ns=20,integer_internal_nodes_checked=False,
           expected_output_contract='All 17280 FP32 outputs and original stall schedule; integer-all loaded but no internal integer assertions in mapped W9 bench')
    write(out/'full-results.json',r)
    if not r['passed']:raise RuntimeError('54-vector mapped replay failed; see full-results.json')
    print('W10-STATUS: fresh mapped replay passed 54 vectors / 17280 outputs',flush=True)
    return r

def activity(a,nl,cells,out,env):
    sim=compile_bench('activity',a,nl,cells,out,env)
    rc=run([str(sim)],out/'activity-simulation.log',out,env,a.timeout)
    txt=(out/'activity-simulation.log').read_text()
    if not (rc==0 and '$finish' in txt and re.search(r'PASS gate_activity vectors=1 outputs=320 cycles=\s*4165 stalls=\s*0 aborts=0',txt)):
        raise RuntimeError('Activity simulation failed or missing exact one-projection pass')
    saif=out/'activity-20ns.saif'
    if not saif.is_file() or saif.stat().st_size==0:raise RuntimeError('Missing fresh SAIF')
    # Confirm actual hierarchical labels exist; annotation coverage must still come from STA.
    labels=[]
    with saif.open() as f:
        for line in f:
            m=re.search(r'\(INSTANCE\s+([^\s()]+)',line)
            if m: labels.append(m[1])
            if len(labels)>=4:break
    if 'tb' not in labels or 'dut' not in labels:
        raise RuntimeError(f'Unexpected SAIF hierarchy {labels}; inspect before using -scope tb/dut')
    scaled=scale(saif,out/'activity-150ns.saif','20','150')
    r=dict(passed=True,netlist_sha256=sha(nl),scope='tb/dut',vectors=1,outputs=320,projection_cycles=4165,
           initial_reset_and_start_included=True,activity_kind='Zero-delay mapped cells; saved real-speech vector0, no SDF glitch timing',
           power_scope='rv_k64_array_port engine; external taalas_index_fabric is a bench source outside tb/dut and excluded from engine area/power',
           annotation_coverage='PENDING: must report using final ODB, SPEF and actual read_saif',scaling=scaled)
    write(out/'activity-results.json',r)
    print('W10-STATUS: fresh one-projection SAIF complete; 20ns -> 150ns, routed coverage pending',flush=True)
    return r

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--netlist',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path,help='New directory strictly within W10')
    p.add_argument('--mode',choices=['all','full','activity','prepare'],default='all')
    p.add_argument('--fixtures',type=Path,default=HERE/'fixtures')
    p.add_argument('--fabric',type=Path,default=REPO/'overnight-20261014/fabric-k64/rtl/index_fabric.sv')
    p.add_argument('--pdk-root',type=Path,default=Path('/workspace/rv/overnight-20261014/fabric-k64/pdks'))
    p.add_argument('--jobs',type=int,default=3,help='Must coordinate total W10 threads <=12 with routing')
    p.add_argument('--timeout',type=int,default=6*3600,help='Seconds per compile/simulation')
    a=p.parse_args()
    if not 1<=a.jobs<=12:p.error('--jobs must be 1..12; coordinate with concurrent W10 P&R')
    out=a.out.resolve();nl=a.netlist.resolve();cells=a.pdk_root.resolve()/'gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog'
    if not out.is_relative_to(W10) or out==W10:p.error('--out must be strictly within W10')
    if not nl.is_relative_to(W10):p.error('--netlist must be a NEW W10 mapped netlist')
    if out.exists():p.error('Refusing existing output directory; choose a fresh run name')
    out.mkdir(parents=True);status={'status':'preparing','started_unix':time.time(),'mode':a.mode,'jobs':a.jobs}
    write(out/'status.json',status)
    try:
        if not nl.is_file():raise ValueError(f'Missing new mapped netlist: {nl}')
        if not a.fabric.is_file():raise ValueError(f'Missing bench fabric: {a.fabric}')
        for f in [cells/'primitives.v',cells/'gf180mcu_fd_sc_mcu7t5v0.v']:
            if not f.is_file():raise ValueError(f'Missing PDK simulation model: {f}')
        with nl.open() as f:
            for line in f:
                if re.search(r'\bgf180mcu_fd_sc_mcu7t5v0__hold(?:_\w+)?\s',line):
                    raise ValueError('Instantiated hold cell cannot be excluded; qualify its simulation model first')
        fixtures=[checked_fixture(a.fixtures/name,digest) for name,digest in json.loads((HERE/'fixture-hashes.json').read_text()).items()]
        (out/'vectors').mkdir();(out/'tmp').mkdir()
        for r in fixtures: shutil.copyfile(r['path'],out/'vectors'/Path(r['path']).name)
        for name in ['gate_sharded.sv','activity_array_port.sv','shard-plan.json']:
            shutil.copyfile(HERE/name,out/name)
        shutil.copyfile(a.fabric,out/'index_fabric.sv')
        inputs=[nl,cells/'primitives.v',cells/'gf180mcu_fd_sc_mcu7t5v0.v',out/'index_fabric.sv',
                out/'gate_sharded.sv',out/'activity_array_port.sv',out/'shard-plan.json',HERE/'run_gate.py',HERE/'scale_saif.py']
        write(out/'inputs.json',dict(inputs={str(f):sha(f) for f in inputs},fixtures=fixtures,netlist=str(nl),
              bench_fabric_outside_power_scope=True,source_clock_period_ns=20,saif_target_clock_period_ns=150))
        env=os.environ.copy();env.update(TMPDIR=str(out/'tmp'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
        net_hash=sha(nl)
        if a.mode in ['all','full']:status['full']=full(a,nl,cells,out,env)
        if a.mode in ['all','activity']:status['activity']=activity(a,nl,cells,out,env)
        if sha(nl)!=net_hash:raise RuntimeError('Netlist changed while replaying; results invalid')
        status['status']='prepared_unverified' if a.mode=='prepare' else 'complete'
    except BaseException as e:
        status.update(status='failed',error=str(e));raise
    finally:
        status['ended_unix']=time.time();write(out/'status.json',status)
if __name__=='__main__':main()
