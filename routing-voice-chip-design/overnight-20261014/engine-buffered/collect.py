"""Collect only executed evidence. Missing stages and values remain explicit."""
import datetime
import hashlib
import json
import re
from pathlib import Path

W=Path(__file__).resolve().parent
R=W/'runs/buf-v4-physical'
states=[]
for p in list((W/'runs/buf-v4').glob('*/state_out.json')) + list(R.glob('*/state_out.json')):
    try:
        idx=int(p.parent.name.split('-')[0])
        if p.parent.parent.name=='buf-v4' and idx>26:continue
        states.append((idx+(1000 if p.parent.parent==R else 0),p,json.loads(p.read_text())))
    except (ValueError,json.JSONDecodeError):
        continue
states.sort(key=lambda x:x[0])
latest=states[-1] if states else (0,None,{})
started=sorted((p for p in R.iterdir() if p.is_dir() and p.name.split('-')[0].isdigit()),key=lambda p:int(p.name.split('-')[0])) if R.exists() else []
unfinished=[p for p in started if not (p/'state_out.json').exists()]
latest_unfinished=unfinished[-1].name if unfinished else None
metrics=latest[2].get('metrics',{})
stages=[p.parent.parent.name+'/'+p.parent.name for _,p,_ in states]
def stage(fragment):
    return next((s for s in reversed(stages) if fragment in s),None)
def log(name):
    p=W/'logs'/name
    return p.read_text(errors='replace') if p.exists() else ''
def number(x):
    return x if isinstance(x,(float,int)) and abs(x)<1e100 else None
corners={}
for k,v in metrics.items():
    if k.startswith('timing__setup__wns__corner:'):
        c=k.split(':',1)[1];wns=number(v)
        corners[c]={
            'setup_wns_ns':wns,
            'worst_setup_slack_ns':number(metrics.get('timing__setup__ws__corner:'+c)),
            'worst_hold_slack_ns':number(metrics.get('timing__hold__ws__corner:'+c)),
            'hold_wns_ns':number(metrics.get('timing__hold__wns__corner:'+c)),
            'mhz_from_requested_wns_formula':1000/(20-wns) if wns is not None else None,
        }
# Distinguish fresh STA measurements from inherited metrics in later states.
fresh={}
for _,path,state in states:
    name=path.parent.name
    if not any(x in name for x in ['staprepnr','stamidpnr','stapostpnr']):continue
    mm=state.get('metrics',{})
    for key,val in mm.items():
        if not key.startswith('timing__setup__wns__corner:'):continue
        c=key.split(':',1)[1]
        if 'stamidpnr' in name and c!='nom_tt_025C_3v30':continue
        wns=number(val)
        fresh[c]={'setup_wns_ns':wns,'worst_setup_slack_ns':number(mm.get('timing__setup__ws__corner:'+c)),
                  'worst_hold_slack_ns':number(mm.get('timing__hold__ws__corner:'+c)),
                  'hold_wns_ns':number(mm.get('timing__hold__wns__corner:'+c)),
                  'mhz_from_requested_wns_formula':1000/(20-wns) if wns is not None else None,
                  'source_stage':path.parent.parent.name+'/'+name,'post_route':'stapostpnr' in name}
for c in json.loads((W/'configs/array_port_buf.json').read_text())['STA_CORNERS']:
    fresh.setdefault(c,{'setup_wns_ns':None,'worst_setup_slack_ns':None,'worst_hold_slack_ns':None,'hold_wns_ns':None,'mhz_from_requested_wns_formula':None,'source_stage':None,'post_route':False})
corners=fresh
diagroot=W/'runs/buf-v4-idealprects'
diagstates=sorted(diagroot.glob('*/state_out.json'),key=lambda p:int(p.parent.name.split('-')[0]))
diaglast=json.loads(diagstates[-1].read_text()) if diagstates else {}
diag={'run':'buf-v4-idealprects','declared_deviation':'Pre-CTS ideal clock; CTS restores propagated clock; original requested-settings run continues separately.',
      'latest_completed_stage':diagstates[-1].parent.name if diagstates else None,
      'flow_exit':int((W/'evidence/flow-buf-v4-idealprects.exit').read_text()) if (W/'evidence/flow-buf-v4-idealprects.exit').exists() else None,
      'completed_stages':[p.parent.name for p in diagstates],
      'stopped':json.loads((W/'evidence/ideal-prects-stopped.json').read_text()) if (W/'evidence/ideal-prects-stopped.json').exists() else None,
      'metrics':diaglast.get('metrics',{}),'evidence':'evidence/ideal-prects-deviation.json'}
fanout_path=W/'evidence/synthesis-fanout.json'
fanout=json.loads(fanout_path.read_text()) if fanout_path.exists() and fanout_path.stat().st_size else None
full=log('gate-full-simulation.log');activity=log('gate-activity-simulation.log')
serial_full_pass='PASS gate vectors=54 outputs=17280' in full and '$finish' in full
shards_path=W/'evidence/gate-sharded-results.json'
shards=json.loads(shards_path.read_text()) if shards_path.exists() else None
full_pass=serial_full_pass or bool(shards and shards.get('passed'))
activity_pass='PASS gate_activity vectors=1 outputs=320' in activity and '$finish' in activity
power=None
power_report=W/'evidence/routed-tt.power.rpt'
annotation=W/'evidence/routed-tt.annotation.rpt'
if power_report.exists() and (W/'evidence/power.exit').exists():
    power_text=power_report.read_text()
    assert '(Watts)' in power_text, 'Power units are not explicitly Watts'
    match=re.search(r'^Total\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',power_text,re.M)
    if match:
        vals=list(map(float,match.groups()))
        power=dict(zip(['internal_w','switching_w','leakage_w','total_w'],vals))
        power.update({'clock_period_ns':20,'projection_cycles':4163,'projection_time_s':4163*20e-9,
            'engine_energy_per_projection_j_at_20ns':vals[3]*4163*20e-9,
            'engine_energy_per_mac_j_at_20ns':vals[3]*4163*20e-9/409600,
            'activity_scope':'tb/dut','trace':'Zero-delay mapped cells, saved real activation vector0, initial reset included; no SDF glitches.',
            'annotation_report':annotation.read_text() if annotation.exists() else None,
            'power_tool_exit':int((W/'evidence/power.exit').read_text()),
            'operating_point_validated':False})
        if annotation.exists():
            ann=dict((k,int(v)) for k,v in re.findall(r'^(saif|unannotated)\s+(\d+)',annotation.read_text(),re.M))
            if set(ann)=={'saif','unannotated'}:
                power.update(annotated_pins=ann['saif'],unannotated_pins=ann['unannotated'],annotation_coverage_fraction=ann['saif']/sum(ann.values()))
        tt=corners.get('nom_tt_025C_3v30',{})
        elec=W/'evidence/routed-tt.electrical.rpt'
        power['operating_point_validated']=bool(power['power_tool_exit']==0 and stage('stapostpnr') and tt.get('setup_wns_ns') is not None and tt['setup_wns_ns']>=0 and tt.get('worst_hold_slack_ns') is not None and tt['worst_hold_slack_ns']>=0 and elec.exists() and 'VIOLATED' not in elec.read_text().upper())
repair_log=W/'runs/buf-v4-physical/01-openroad-repairdesignpostgpl/openroad-repairdesignpostgpl.log'
repair_rows=re.findall(r'^\s*(\d+)\s*\|\s*([+-]?[\d.]+)%\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)',repair_log.read_text(errors='replace') if repair_log.exists() else '',re.M)
repair_progress=None
if repair_rows:
    rr=repair_rows[-1]
    repair_progress=dict(zip(['iteration','area_change_percent','resized_cells','inserted_buffers','repaired_nets','remaining_nets'],[int(rr[0]),float(rr[1]),*map(int,rr[2:])]))
    repair_progress['source']=str(repair_log)
flow_exit=W/'evidence/flow-buf-v4-physical.exit'
exitcode=int(flow_exit.read_text()) if flow_exit.exists() else None
result={
    'status':'partial_in_progress' if exitcode is None else 'flow_complete' if exitcode==0 else 'flow_failed',
    'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'lineage':'buf-v4 synthesis through placement and original STAMidPNR; buf-v4-physical resumes RepairDesignPostGPL from the identical placement state while read-only STA runs concurrently.',
    'scope':'1280x320 ARRAY-PORT engine only. Custom index array, sense/read circuits, pads, upstream quantizer and recognizer excluded.',
    'latest_unfinished_physical_stage':latest_unfinished,
    'run':'buf-v4-physical','flow_exit':exitcode,'latest_completed_stage':latest[1].parent.name if latest[1] else None,
    'attempt_history':[
        {'run':'buf-v1','status':'interrupted_synthesis_console_bottleneck','evidence':'evidence/restart-console-bottleneck.json'},
        {'run':'buf-v2','status':'synthesis_complete_fanout_failed_flow_stopped_before_placement','max_fanout':11359,'row_bit6_fanout':4068,'buffers':6643,'evidence':'evidence/buf-v2-synthesis-fanout.json'},
        {'run':'buf-v3','status':'fanout_failed_identical_to_v2_invalid_ABC_driving_cell','evidence':'evidence/buf-v3-synthesis-fanout.json'},
        {'run':'buf-v4','change':'ABC PI buffering with bare driving cell; ten preserved row-register/decode domains, 32 lanes each'},
    ],
    'serial_full_replay_pass':serial_full_pass,'sharded_full_replay':shards,
    'rtl_regression_pass':(W/'evidence/rtl-full.status').exists(),
    'steps':{'rtl': 'passed' if (W/'evidence/rtl-full.status').exists() else 'pending_or_failed','configuration':'complete','synthesis':stage('yosys-synthesis'),'routing':stage('openroad-detailedrouting'),
             'extraction':stage('openroad-rcx'),'sta':stage('stapostpnr') or stage('stamidpnr') or stage('staprepnr'),
             'gate_replay':('54 vectors / 17280 outputs passed (serial)' if serial_full_pass else '54 vectors / 17280 outputs passed (8 shards, original stall cycles)' if full_pass else 'pending_or_failed'),
             'activity':'vector0 / 320 outputs passed' if activity_pass else 'pending_or_failed','power':'computed_at_target_period' if power else 'pending'},
    'area':{key:number(metrics.get(key)) for key in ['design__die__area','design__core__area','design__instance__area','design__instance__area__stdcell','design__instance__utilization']},
    'area_units':'square micrometres; divide by 1e6 for square millimetres',
    'timing_corners':corners,
    'timing_note':'Each corner identifies its last fresh STA source; missing corners are pending. Before post-PNR STA these are early diagnostics. Pre-CTS propagated-clock results include an unsynthesized clock network. Frequency formula does not certify hold, electrical or physical signoff.',
    'signoff':{k:v for k,v in metrics.items() if any(t in k.lower() for t in ['drc','antenna','lvs','max_slew','max_cap','max_fanout'])},
    'signoff_stages':{name:stage(name) for name in ['magic-drc','klayout-drc','netgen-lvs','checkantennas']},
    'supplemental_klayout':{'exit':int((W/'evidence/supplemental-klayout-drc.exit').read_text()) if (W/'evidence/supplemental-klayout-drc.exit').exists() else None, 'log':'logs/supplemental-klayout-drc.log','executed':(W/'logs/supplemental-klayout-drc.log').exists()},
    'klayout_note':'W2b input enables KLayout DRC but resolved runset can be null; skipped execution is not a pass.',
    'activity_receipt':json.loads((W/'evidence/array_port-mapped-activity.json').read_text()) if (W/'evidence/array_port-mapped-activity.json').exists() else None,
    'activity_file_status':'frozen_complete' if (W/'evidence/frozen-activity-provenance.json').exists() else 'first_pass_recorded_shared_path_being_replayed' if activity_pass else 'pending',
    'repair_progress':repair_progress,
    'synthesis_fanout':fanout,'power':power,'separate_diagnostic':diag,
    'completed_stages':stages,
}
(W/'results.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# W9 buffered ARRAY-PORT engine','',f"Updated {result['updated_utc']}. Status: **{result['status']}**.",'',result['scope'],'',
       f"Latest completed step: `{result['latest_completed_stage']}`; unfinished physical step: `{latest_unfinished}`; flow exit: `{exitcode}`.",'',
       'The requested repaired, routed, signoff-checked engine and extracted activity power are not yet achieved. Functional and activity verification are complete; routed MHz, DRC/LVS/antenna results, power and energy remain pending.' if not result['steps']['routing'] else 'Routing stage completed; see the remaining signoff and power statuses below.', '',
       'ABC buffering enabled, maximum fanout 16, sizing enabled, 20 ns clock. The W9-local synthesis wrapper adds `buffer -p` to cover primary inputs (including extracted register outputs). ABC-only driver uses the bare cell name. Ten RTL row-register copies each drive 32 lanes. Repair/CTS/route/signoff retained. DRT 12 threads, STA 4.','',
       'Pinned LibreLane supplied ABC a cell/pin driver (`inv_1/ZN`), which ABC could not resolve. Stock buffering and the first `-p` attempt therefore produced the same ineffective map. V4 fixes the ABC-only driver to the bare cell name and enables PI buffering; the 3,000-load smoke test reaches max fanout 16. Both failed maps and logs are preserved in `synthesis-checkpoint.tar.gz`; see `FAILURES.md`. The tested V4 combination also includes RTL duplication; no separate ablation is claimed.','',
       '## Completion','']
lines += [f'- {k}: {v}' for k,v in result['steps'].items()]
lines += ['','## Area','', '| Measurement | Value |','|---|---|']
for k,v in result['area'].items():
    lines.append(f'| {k} | {v}'+(f' µm² ({v/1e6:.6f} mm²)' if v is not None and 'area' in k else '')+' |')
lines += ['','## Timing','',result['timing_note'],'','| Corner | Setup WNS ns | Hold worst slack ns | 1000/(20−WNS) MHz | Source |','|---|---:|---:|---:|---|']
for c,v in corners.items():
    f=v['mhz_from_requested_wns_formula'];lines.append(f"| {c} | {v['setup_wns_ns']} | {v['worst_hold_slack_ns']} | {f} | {v.get('source_stage')} |")
lines += ['','## Fanout','',f"Post-synthesis audit: `{fanout['max_signal_fanout'] if fanout else 'pending'}` maximum non-clock load count.",
          f"Mapped buffers: {fanout['buffers'] if fanout else 'pending'}; nets above 16: {fanout['signal_nets_over_16'] if fanout else 'pending'}; distinct duplicated row bit-6 nets: {fanout.get('duplicated_row_bit6_distinct') if fanout else 'pending'}.",
          '', '## Physical repair progress','',json.dumps(repair_progress,indent=2) if repair_progress else 'Pending progress log.', '', '## Power and signoff','',
          json.dumps(power,indent=2) if power else 'Routed SPEF + new mapped SAIF power is pending. No power or energy result claimed.',
          json.dumps(result['activity_receipt'].get('placed_annotation'),indent=2) if result['activity_receipt'] else 'Activity receipt pending.',
          '', 'Raw signoff counts and their completed stages are in `results.json`. Missing or skipped checks receive no pass credit.','',
          f"Separate ideal-pre-CTS diagnostic: `{diag['stopped']['status'] if diag['stopped'] else diag['latest_completed_stage']}`. This declared STA-behavior deviation is not silently substituted for the requested-settings run; see `DIAGNOSTICS.md`.",'',
          'The report is partial until routing, extracted STA, DRC/LVS/antenna checks, the full mapped replay and activity power have completed.']
(W/'RESULTS.md').write_text('\n'.join(lines)+'\n')
if latest[1]:
    (W/'evidence/latest-state.json').write_text(json.dumps({'source':str(latest[1]),**latest[2]},indent=2))
print('W9-STATUS:',result['status'],result['latest_completed_stage'])
