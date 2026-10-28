#!/usr/bin/env python3
"""Extract measured metrics only; missing physical stages stay null."""
import hashlib,json,re,math
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent
variants=['rv_fixed_proj320_rom','rv_fixed_proj320_dp','rv_fixed_proj64x320_rom']
expected_corners={f'{rc}_{pvt}' for rc in ['nom','min','max'] for pvt in ['tt_025C_5v00','ss_125C_4v50','ff_n40C_5v50']}
def numeric(v):
    try:
        f=float(v)
        return f if math.isfinite(f) else None
    except (TypeError,ValueError):return None
def area_from_bbox(v):
    if isinstance(v,str): v=v.split()
    if not isinstance(v,list) or len(v)!=4:return None
    a=list(map(float,v));return (a[2]-a[0])*(a[3]-a[1])
def choose(d,keys):
    for key in keys:
        if key in d:return numeric(d[key])
    return None
result={'scope':'Raw integer projection primitive, pre-silicon tool estimates. No whole-recognizer or custom-cell result.', 'metric_caveat':'LibreLane raw state metrics accumulate and may include stale metrics inherited from earlier stages/corners. Normalized sta_corners is populated only from extracted post-PnR STA.', 'generation':json.loads((r/'evidence/generation.json').read_text()),'initial_clock_period_ns':20,'variants':{},'attempt_receipts':{p.name:json.loads(p.read_text()) for p in (r/'evidence').glob('*supervisor.json')}}
for variant in variants:
    rows=64 if '64x320' in variant else 320;weights=rows*320
    v={'rows':rows,'outputs':320,'weight_positions':weights,'verification_level':'RTL simulation against original-byte NumPy INT64 oracle','verification':None,'physical_runs':[],
       'cycles_start_to_done_no_stalls':rows+1,'minimum_start_interval_without_readout_cycles':rows+2,'cycles_including_320_clocked_reads':rows+321,'accepted_activation_cycles':rows,'readout_cycles_if_clocked_one_output_per_cycle':320,
       'cycles_full_320_matvec':321 if rows==320 else None,'us_at_requested_50MHz':(rows+1)*.02,
       'synthesized_cell_count':None,'synthesized_cell_area_um2':None,'die_area_um2':None,'core_area_um2':None,'utilization':None,
       'sta_corners':{},'achieved_mhz':None,'sta_inferred_mhz':None,'drc':None,'lvs':None,'antenna':None,
       'power_mw':None,'power_corner':None,'power_activity_source':None,'mm2_per_weight':None,'um2_per_weight':None,
       'mw_per_weight_at_achieved_clock':None,'us_per_full_320_matvec_at_achieved_clock':None,'layout_png':None}
    v['expected_extracted_corners']=sorted(expected_corners)
    v['complete_extracted_corner_matrix']=False
    gate=r/'evidence'/f'{variant}.gate-verification.json'
    if gate.exists():v['gate_verification']=json.loads(gate.read_text())
    log=r/'logs'/f'{variant}.verify.log'
    if log.exists():
        m=re.search(r'VERIFICATION PASS vectors=(\d+) random=(\d+) checks=(\d+) failures=(\d+)',log.read_text())
        if m:v['verification']=dict(zip(['vectors_passed','random_vectors','exact_comparisons','failures'],map(int,m.groups())))
    runs=sorted((r/'runs').glob(variant+'-*'),key=lambda p:p.stat().st_mtime)
    best_metrics={};best_run=None;best_state_time=0
    for run in runs:
        states=sorted(run.glob('[0-9]*-*/state_out.json'))
        started_steps=sorted(p for p in run.glob('[0-9]*-*') if p.is_dir())
        supervisor=r/'evidence'/f'{run.name}.supervisor.json'
        attempt={'run_directory':str(run.relative_to(r)),'last_completed_step':states[-1].parent.name if states else None,'supervisor':json.loads(supervisor.read_text()) if supervisor.exists() else None}
        attempt['last_started_step']=started_steps[-1].name if started_steps else None
        attempt['flow_log']=str((r/'logs'/f'{run.name}.flow.log').relative_to(r))
        for termination in [r/'evidence/full-rom-time-limit-log-preservation.json',r/'evidence/dp-time-limit-log-preservation.json',r/'evidence/dp-disk-limit-log-preservation.json']:
            if termination.exists():
                term=json.loads(termination.read_text())
                if term.get('run')==run.name and term.get('signals'):
                    attempt['termination_reason']=term['reason']
                    attempt['termination_evidence']=str(termination.relative_to(r))
        v['physical_runs'].append(attempt)
        if states and not run.name.endswith(('-activity','-render')):
            stamp=states[-1].stat().st_mtime;metrics=json.loads(states[-1].read_text()).get('metrics',{})
            if stamp>=best_state_time:
                best_state_time=stamp;best_metrics=metrics;best_run=run
                v['latest_completed_step']=states[-1].parent.name
        syn=run/'06-yosys-synthesis/state_out.json'
        if syn.exists():
            sm=json.loads(syn.read_text()).get('metrics',{});v['synthesis_metrics']=sm
            v['synthesized_cell_count']=choose(sm,['design__instance__count','design__instance__count__stdcell'])
            v['synthesized_cell_area_um2']=choose(sm,['design__instance__area','design__instance__area__stdcell'])
    v['latest_measured_metrics']=best_metrics
    v['latest_physical_instance_count']=best_metrics.get('design__instance__count')
    v['latest_physical_instance_area_um2']=best_metrics.get('design__instance__area')
    if best_run:
        v['measurement_run']=str(best_run.relative_to(r))
        resolved=json.loads((best_run/'resolved.json').read_text())
        period=float(resolved['CLOCK_PERIOD']);v['measurement_clock_period_ns']=period
        v['target_mhz']=1000/period
        v['die_area_um2']=area_from_bbox(best_metrics.get('design__die__bbox'))
        v['core_area_um2']=area_from_bbox(best_metrics.get('design__core__bbox'))
        v['utilization']=choose(best_metrics,['design__instance__utilization__stdcell','design__instance__utilization'])
        v['utilization_percent']=100*v['utilization'] if v['utilization'] is not None else None
        v['pdn_connectivity_violations']=best_metrics.get('design__power_grid_violation__count')
        v['area_scope']='routed footprint' if list(best_run.glob('*-openroad-detailedrouting/state_out.json')) else 'allocated floorplan; routing not complete'
        post=list(best_run.glob('*-openroad-stapostpnr/state_out.json'))
        if post:
            pm=json.loads(post[-1].read_text())['metrics']
            for key,value in pm.items():
                for kind in ['setup','hold']:
                    prefix=f'timing__{kind}__ws__corner:'
                    if key.startswith(prefix):v['sta_corners'].setdefault(key[len(prefix):],{})[kind+'_slack_ns']=numeric(value)
            slacks=[c['setup_slack_ns'] for c in v['sta_corners'].values() if c.get('setup_slack_ns') is not None]
            holds=[c['hold_slack_ns'] for c in v['sta_corners'].values() if c.get('hold_slack_ns') is not None]
            v['expected_extracted_corners']=sorted(expected_corners)
            v['complete_extracted_corner_matrix']=expected_corners.issubset(v['sta_corners']) and all(v['sta_corners'][c].get(k) is not None for c in expected_corners for k in ['setup_slack_ns','hold_slack_ns'])
            if slacks:
                v['sta_inferred_mhz']=1000/(period-min(slacks)) if min(slacks)<period else None
                if v['complete_extracted_corner_matrix'] and min(slacks)>=0 and holds and min(holds)>=0:v['achieved_mhz']=1000/period
            power=post[-1].parent/'nom_tt_025C_5v00/power.rpt'
            if power.exists():
                match=re.search(r'^Total\s+([\deE+.-]+)\s+([\deE+.-]+)\s+([\deE+.-]+)\s+([\deE+.-]+)',power.read_text(),re.M)
                if match:
                    vals=list(map(float,match.groups()));v['power_mw']=vals[3]*1000
                    v['power_components_mw']=dict(zip(['internal','switching','leakage','total'],[x*1000 for x in vals]))
                    v['power_corner']='nom_tt_025C_5v00';v['power_activity_source']=f'OpenSTA default activity at {1000/period:g} MHz';v['power_report']=str(power.relative_to(r))
        v['physical_check_metrics']={k:value for k,value in best_metrics.items() if any(word in k.lower() for word in ['drc','lvs','antenna','power_grid_violation'])}
        v['physical_check_sources']={}
        drc_keys={'routing':('openroad-detailedrouting','route__drc_errors'),'magic':('magic-drc','magic__drc_error__count'),'klayout':('klayout-drc','klayout__drc_error__count')}
        drc={}
        for label,(stage,key) in drc_keys.items():
            checkpoints=sorted(best_run.glob(f'*-{stage}/state_out.json'))
            if checkpoints:
                drc[label]=json.loads(checkpoints[-1].read_text())['metrics'].get(key)
                v['physical_check_sources'][label+'_drc']=str(checkpoints[-1].relative_to(r))
        if drc:v['drc']={label:drc.get(label) for label in drc_keys}
        lvs_states=sorted(best_run.glob('*-netgen-lvs/state_out.json'))
        if lvs_states:
            v['lvs']=json.loads(lvs_states[-1].read_text())['metrics'].get('design__lvs_error__count')
            v['physical_check_sources']['lvs']=str(lvs_states[-1].relative_to(r))
        drt_states=list(best_run.glob('*-openroad-detailedrouting/state_out.json'))
        if drt_states:
            drt_index=int(drt_states[-1].parent.name.split('-')[0])
            antenna_states=sorted(p for p in best_run.glob('*-openroad-checkantennas*/state_out.json') if int(p.parent.name.split('-')[0])>drt_index)
            if antenna_states:
                v['antenna']=json.loads(antenna_states[-1].read_text())['metrics'].get('route__antenna_violation__count')
                v['physical_check_sources']['post_routing_antenna']=str(antenna_states[-1].relative_to(r))
        for path in best_run.glob('**/*.png'):
            if 'render' in str(path).lower():v['layout_png']=str(path.relative_to(r))
    if v['die_area_um2'] is not None:
        v['allocated_floorplan_um2_per_weight']=v['die_area_um2']/weights
        v['allocated_floorplan_mm2_per_weight']=v['allocated_floorplan_um2_per_weight']/1e6
        if v.get('area_scope')=='routed footprint':
            v['um2_per_weight']=v['allocated_floorplan_um2_per_weight'];v['mm2_per_weight']=v['allocated_floorplan_mm2_per_weight']
    if v['synthesized_cell_count'] is not None:v['synthesized_cell_count']=int(v['synthesized_cell_count'])
    if v['synthesized_cell_area_um2'] is not None:
        v['synthesized_cell_area_mm2']=v['synthesized_cell_area_um2']/1e6
        v['synthesized_cell_um2_per_weight']=v['synthesized_cell_area_um2']/weights
    if v['power_mw'] is not None:v['default_activity_mw_per_weight_at_target_clock']=v['power_mw']/weights
    if v['achieved_mhz'] is not None:
        v['us_per_projection_at_achieved_clock']=(rows+1)/v['achieved_mhz']
        if rows==320:v['us_per_full_320_matvec_at_achieved_clock']=321/v['achieved_mhz']
        if v['power_mw'] is not None:v['mw_per_weight_at_achieved_clock']=v['power_mw']/weights
    checkpoint_file=r/'evidence/checkpoint-metrics.json'
    if checkpoint_file.exists():
        v['pre_route_checkpoints']=[c for c in json.loads(checkpoint_file.read_text()) if c['run'].split('/')[-1].startswith(variant+'-')]
        baseline_timing=[c for c in v['pre_route_checkpoints'] if c['run']==v.get('measurement_run') and c.get('typical_setup_slack_ns') is not None]
        if baseline_timing:
            chosen_timing=baseline_timing[-1]
            v['pre_route_typical_timing']={k:chosen_timing[k] for k in ['scope','step','period_ns','target_mhz','typical_setup_slack_ns','typical_hold_slack_ns','typical_setup_inferred_mhz']}
        candidates=[c for c in v['pre_route_checkpoints'] if c.get('vcd_valid_nonzero_annotation')]
        if candidates:
            chosen=max(candidates,key=lambda c:c.get('vcd_annotated_pins',0))
            v['pre_route_selected_power']={k:chosen[k] for k in ['scope','step','period_ns','target_mhz','power','vcd_annotated_pins','unannotated_pins','annotated_pin_fraction','annotation_limitation'] if k in chosen}
            v['pre_route_selected_power']['mw_per_weight_at_unqualified_target']={k:x['components_mw']['total']/weights for k,x in chosen['power'].items()}
            v['pre_route_selected_power']['us_per_projection_at_unqualified_target']=(rows+1)/chosen['target_mhz']
    pre_image=r/f'{variant}-PRE-ROUTE-NOT-SIGNOFF.png'
    if pre_image.exists():v['pre_route_layout_png']=str(pre_image.relative_to(r))
    v['signoff_complete']=bool(v['complete_extracted_corner_matrix'] and v['achieved_mhz'] is not None and v['drc'] is not None and all(v['drc'].get(k)==0 for k in ['routing','magic','klayout']) and v['lvs']==0 and v['antenna']==0 and v.get('pdn_connectivity_violations')==0)
    v['signoff_status']='configured routed timing and physical checks passed' if v['signoff_complete'] else ('incomplete: extracted STA present, but required timing/physical checks are not all passed' if v['sta_corners'] else 'incomplete: no extracted final timing/signoff result')
    result['variants'][variant]=v
result['generated_at_utc']=datetime.now(timezone.utc).isoformat()
(r/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print('Results extracted; null means unavailable, never zero.')
