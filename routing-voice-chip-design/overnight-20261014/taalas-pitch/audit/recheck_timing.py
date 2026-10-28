"""Independent retained trace/header analysis; no SPICE or timing-module imports."""
from pathlib import Path
import gzip,json,sys,os
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
W=Path(__file__).resolve().parents[1]
receipts=[]
for argument in sys.argv[1:]:
    d=W/argument;m=json.loads((d/'build.json').read_text());r=json.loads((d/'result.json').read_text())
    image=np.load(d.parent/'image.npy')
    with gzip.open(d/'trace.dat.gz','rt') as f:
        header=f.readline().split();a=np.loadtxt(f)
    ci={n:i for i,n in enumerate(header)};t=a[:,0];p=m['protocol'];vdd=r['voltage_v'];period=p['period_ns']
    def voltage(name,ns):return float(np.interp(ns*1e-9,t,a[:,ci[f'v({name})']]))
    fails=dict(output=0,raw=0,precharge=0,phase=0);capture=0;aperture=0;latencies=[]
    for cycle,row in enumerate(m['addresses']):
        start=cycle*period
        for bit in m['selected']:
            e=(int(image[row,bit//4])>>(bit%4))&1
            for when in p['sample_ns']:
                o=voltage(f'out{bit}',start+when);s=voltage(f'bl{bit}s0',start+when)
                fails['output']+=not(o>=.9*vdd if e else o<=.1*vdd)
                fails['raw']+=not(s<=.3*vdd if e else s>=.7*vdd);capture+=1
            pre=start+p['pc_off_ns']-.5
            fails['precharge']+=min(voltage(f'bl{bit}s0',pre),voltage(f'bl{bit}s{m["segments"]}',pre))<.95*vdd
            when=start+p['wl_start_ns']+20
            if when<=start+p['wl_fall_start_ns']:
                o=voltage(f'out{bit}',when);s=voltage(f'bl{bit}s0',when)
                aperture+=not((o>=.9*vdd and s<=.3*vdd) if e else (o<=.1*vdd and s>=.7*vdd))
            ix=np.flatnonzero((t>=(start+p['wl_start_ns'])*1e-9)&(t<=(start+p['sample_ns'][0])*1e-9))
            o=a[ix,ci[f'v(out{bit})']];s=a[ix,ci[f'v(bl{bit}s0)']]
            valid=((o>=.9*vdd)&(s<=.3*vdd)) if e else ((o<=.1*vdd)&(s>=.7*vdd))
            if len(valid) and valid[-1]:
                bad=np.flatnonzero(~valid)
                delay=float(t[ix[bad[-1]+1]]*1e9-start-p['wl_start_ns']) if len(bad) else 0.
                latencies.append(delay)
        pc=min(voltage(n,start+p['wl_start_ns']) for n in m.get('phase_precharge_nodes',['pc']))
        wl=max(voltage(n,start+p['pc_on_start_ns']) for n in m.get('phase_wordline_nodes',[f'wl{x}' for x in m['active_rows']]))
        fails['phase']+=not(pc>=.9*vdd and wl<=.1*vdd)
    begin=m['base_sequence_length']*period*1e-9;end=len(m['addresses'])*period*1e-9
    ts=np.r_[begin,t[(t>begin)&(t<end)],end];denom=len(m['addresses'])-m['base_sequence_length']
    energy={n:float(np.trapezoid(np.interp(ts,t,a[:,ci[n]]),ts)*1e12/denom) for n in ['pr','pw','pp','pa']}
    assert fails==r['failures'],(d,fails,r['failures'])
    assert capture==r['samples_checked']
    assert aperture==sum(x['data_failures'] for x in r['command_to_capture_20ns_probe'])
    assert max(latencies,default=None)==r['maximum_sampled_settled_ns']
    assert all(abs(v-r['energy_pj_per_sampled_read'][n])<1e-7 for n,v in energy.items())
    receipts.append(dict(case=argument,independent_trace_recomputation_matches=True,failures=fails,
        capture_checks=capture,aperture20ns_failures=aperture,maximum_sampled_settle_ns=max(latencies,default=None),
        partial_source_energy_pj=energy,partial_total_pj=sum(energy.values()),max_step_ns=float(np.diff(t).max()*1e9)))
(W/'audit/final-timing-trace-audit.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('W6-STATUS: independent final timing trace audit',json.dumps(receipts))
