"""Explicit repeated-read phases and source-window metrics, independent of layout."""
import numpy as np

def protocol(period_ns):
    # Preserve the original14ns/18ns pre2std4 phases at60ns. Shorter periods
    # reduce precharge duration linearly but retain its4ns nonoverlap guard.
    pc_off=period_ns*14/60
    wl_start=pc_off+4
    assert wl_start<period_ns-2
    return {'period_ns':period_ns,'pc_off_ns':pc_off,'wl_start_ns':wl_start,
            'wl_fall_start_ns':period_ns-2.2,'wl_fall_end_ns':period_ns-2,
            'pc_on_start_ns':period_ns-.2,'sample_ns':[period_ns-6,period_ns-.5],
            'edge_ns':.2,'phase_family':'pre2std4;14/60fraction precharge plus fixed4ns guard'}

def pwl(points):return 'PWL('+' '.join(f'{t:.9g}n {v:.9g}' for t,v in points)+')'

def wl_stimulus(addresses,row,vdd,p):
    points=[(0,0)]
    for cycle,address in enumerate(addresses):
        if address==row:
            t=cycle*p['period_ns'];points.extend([(t+p['wl_start_ns'],0),(t+p['wl_start_ns']+.2,vdd),(t+p['wl_fall_start_ns'],vdd),(t+p['wl_fall_end_ns'],0)])
    points.append((len(addresses)*p['period_ns'],0));return pwl(points)

def aggressor(addresses,n,image,vdd,p):
    points=[(0,vdd)]
    for cycle,row in enumerate(addresses):
        if row is not None and (int(image[row,n//4])>>(n%4))&1:
            t=cycle*p['period_ns'];points.extend([(t+p['wl_start_ns']+.3,vdd),(t+p['wl_start_ns']+.5,0),(t+p['pc_on_start_ns'],0),(t+p['period_ns'],vdd)])
    points.append((len(addresses)*p['period_ns']+.1,vdd));return pwl(points)

def analyze(trace,names,meta,image,vdd):
    # Names are written explicitly; no dependence on brittle hardcoded columns.
    col={n:i+1 for i,n in enumerate(names)};time=trace[:,0];p=meta['protocol'];period=p['period_ns'];selected=meta['selected'];rows=meta['addresses'];base_count=meta['base_sequence_length']
    point=lambda t:np.array([np.interp(t*1e-9,time,trace[:,i]) for i in range(trace.shape[1])])
    samples=[];precharges=[];phase=[];latencies=[];apertures=[]
    for cycle,row in enumerate(rows):
        start=cycle*period;pre=point(start+p['pc_off_ns']-.5)
        for n in selected:
            near=pre[col[f'bl{n}s0']];far=pre[col[f'bl{n}s{meta["segments"]}']]
            precharges.append({'cycle':cycle,'row':row,'bit':n,'near_v':float(near),'far_v':float(far),'pass':min(near,far)>=.95*vdd})
        for when in p['sample_ns']:
            q=point(start+when)
            for n in selected:
                expected=0 if row is None else (int(image[row,n//4])>>(n%4))&1
                out=q[col[f'out{n}']];sense=q[col[f'bl{n}s0']]
                samples.append({'cycle':cycle,'row':row,'sample_ns':when,'bit':n,'expected':expected,'out_v':float(out),'sense_v':float(sense),'output_pass':out>=.9*vdd if expected else out<=.1*vdd,'raw_pass':sense<=.3*vdd if expected else sense>=.7*vdd})
        before=point(start+p['wl_start_ns']);after=point(start+p['pc_on_start_ns'])
        pc=min(before[col[n]] for n in meta.get('phase_precharge_nodes',['pc']));wl=max(after[col[n]] for n in meta.get('phase_wordline_nodes',[f'wl{r}' for r in meta['active_rows']]))
        phase.append({'cycle':cycle,'pc_v_at_wl_command':float(pc),'max_wl_v_at_pc_command':float(wl),'pc_off_pass':pc>=.9*vdd,'wl_off_pass':wl<=.1*vdd})
        # Last violation before capture gives settled time, not merely first crossing.
        capture=start+p['sample_ns'][0];window=trace[(time>=(start+p['wl_start_ns'])*1e-9)&(time<=capture*1e-9)]
        for n in selected:
            expected=0 if row is None else (int(image[row,n//4])>>(n%4))&1
            ok=(window[:,col[f'out{n}']]>=.9*vdd)&(window[:,col[f'bl{n}s0']]<=.3*vdd) if expected else (window[:,col[f'out{n}']]<=.1*vdd)&(window[:,col[f'bl{n}s0']]>=.7*vdd)
            bad=np.flatnonzero(~ok);settled=None if not len(window) or not ok[-1] else float((window[bad[-1]+1,0]*1e9 if len(bad) else start+p['wl_start_ns'])-start-p['wl_start_ns'])
            latencies.append({'cycle':cycle,'row':row,'bit':n,'settled_ns_after_wl_command':settled})
        # A20ns command-to-capture aperture is separate from initiation interval.
        when=start+p['wl_start_ns']+20
        if when<=start+p['wl_fall_start_ns']:
            q=point(when);fail=0
            for n in selected:
                e=0 if row is None else (int(image[row,n//4])>>(n%4))&1;o=q[col[f'out{n}']];s=q[col[f'bl{n}s0']];fail+=not((o>=.9*vdd and s<=.3*vdd) if e else (o<=.1*vdd and s>=.7*vdd))
            apertures.append({'cycle':cycle,'ns_after_wl_command':20,'data_failures':int(fail),'excludes_decoder_setup_latch_and_mux':True})
    begin=base_count*period;end=len(rows)*period;ti=np.concatenate(([begin*1e-9],time[(time>begin*1e-9)&(time<end*1e-9)],[end*1e-9]));energy={}
    for name in ['pr','pw','pp','pa']:
        energy[name]=float(np.trapezoid(np.interp(ti,time,trace[:,col[name]]),ti)*1e12/(len(rows)-base_count))
    a=point(begin);b=point(end);state=[col[n] for n in names if n not in ['pr','pw','pp','pa'] and not n.startswith('pcolumn')]
    failures={'output':sum(not s['output_pass'] for s in samples),'raw':sum(not s['raw_pass'] for s in samples),'precharge':sum(not s['pass'] for s in precharges),'phase':sum(not(s['pc_off_pass'] and s['wl_off_pass']) for s in phase)}
    return {'protocol_pass':not any(failures.values()),'failures':failures,'samples':samples,'precharges':precharges,'phase_checks':phase,'latencies':latencies,'maximum_sampled_settled_ns':max((v['settled_ns_after_wl_command'] for v in latencies if v['settled_ns_after_wl_command'] is not None),default=None),'command_to_capture_20ns_probe':apertures,'energy_pj_per_sampled_read':energy,'energy_window_ns':[begin,end],'energy_scope':'Finite-window net source energy over repeated sequence; only observed endpoint states compared, not all internal stored charge. Partial16active-column group plus128receivers/selectedWL/PC buffers; not complete bank energy.','maximum_observed_endpoint_voltage_difference_v':float(np.max(np.abs(a[state]-b[state]))),'samples_checked':len(samples)}
