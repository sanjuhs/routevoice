from pathlib import Path
import json,datetime,hashlib,subprocess,time
W=Path(__file__).resolve().parent
def load(p):
 for attempt in range(5):
  try:return json.loads(p.read_text()) if p.exists() else None
  except json.JSONDecodeError:
   if attempt==4:raise
   time.sleep(0.01)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'physical_in_progress','scope':'Complete selected K64 1280x320 encoder FF output; not full recognizer','identity':load(W/'evidence/identity.json'),'correctness':load(W/'evidence/correctness.json'),'mapped_gate_correctness':load(W/'evidence/gate-correctness.json'),'numerical_width_bounds':load(W/'evidence/numerical-width-bounds.json'),'activity_annotation_probe':load(W/'evidence/activity-coverage.json'),'constraints':load(W/'evidence/resolved-constraints.json'),'variants':{},'physical_feasibility_proven':False,'tools':{'librelane':'3.0.11','librelane_repo_commit':'33ab64861c5570d65de69295da9a46f5bad32ee3','open_pdks_commit':'54435919abffb937387ec956209f9cf5fd2dfbee','simulation_verilator':'5.050 2026-07-01','native_yosys':'0.68+post c12172fbae8af5e20f6fb52e3d4e92d56ed587b6','opensta':'2.7.0; Nix store sc7lam0v6gsfzzcn993qcnkdzkzvnsk9-opensta','python_environment':load(W/'evidence/python-environment.json'),'pdk_view_hashes':'evidence/physical-view-hashes.json','pdk_source_revisions':load(W/'evidence/pdk-source-revisions.json'),'physical_yosys':'0.62 7326bb7d6641500ecb285c291a54a662cb1e76cf','openroad':'dcf36133a369abc8f3c5e5738cd4d82e4903c0e0 (2026-02-17)','physical_tools_source':'Each LibreLane step COMMANDS and logs; native PATH yosys is not physical flow yosys'},'commands':'COMMANDS.md','layout_png':'evidence/array_port-placed.png','layout_stage':'global placement, not routed'}
for v in ['array_port','sc_rom']:
 run=W/'runs'/f'{v}-v2';states=sorted(run.glob('*/state_out.json'))
 metrics=load(states[-1]).get('metrics',{}) if states else {}
 r['variants'][v]={'implementation':'standard-cell comparator' if v=='sc_rom' else 'datapath and fixed books/metadata; custom index array excluded','guard':load(W/'evidence'/f'{v}-guard.json'),'extended_overnight_window':load(W/'evidence/array_port-window-extension.json') if v=='array_port' else None,'cloud_request':'CLOUD-REQUEST.md' if v=='sc_rom' else None,'last_completed_step':states[-1].parent.name if states else None,'last_metrics':metrics,'routed_area_mm2':None,'area_partition_mm2':{'index_fabric':None,'books':None,'arithmetic':None,'state':None,'periphery':None,'routing_overhead':None},'timing_by_corner':None,'achieved_mhz':None,'cycles_excluding_start':4163,'target_only_duration_us_at_20ns':83.26,'achieved_duration_us':None,'power':{'dynamic_mw':None,'leakage_mw':None,'energy_uj_per_projection':None,'activity_source':f'evidence/{v}-speech.vcd','activity_annotated':False,'default_activity_power_mw':None},'physical_verification':{'magic_drc':None,'klayout_drc':None,'netgen_lvs':None,'antenna':None},'exclusions':[] if v=='sc_rom' else ['1,638,400-bit custom index array','macro sense/read/decode periphery','macro timing and electrical loading not characterized']}
for v in ['array_port','sc_rom']:
 run=W/'runs'/f'{v}-v2'
 synth=load(run/'06-yosys-synthesis/state_out.json')
 if synth:
  m=synth['metrics']
  r['variants'][v]['synthesis']={'cell_area_mm2':m['design__instance__area']/1e6,'cells':m['design__instance__count'],'unmapped_cells':m['design__instance_unmapped__count'],'check_errors':m['synthesis__check_error__count'],'inferred_latches':m['design__inferred_latch__count'],'routed':False}
 stat=load(run/'06-yosys-synthesis/reports/stat.json')
 if stat:
  sm=next(iter(stat['modules'].values()))
  r['variants'][v]['synthesis']['sequential_cell_area_mm2']=sm['sequential_area']/1e6
  r['variants'][v]['synthesis']['nonsequential_cell_area_mm2']=(sm['area']-sm['sequential_area'])/1e6
  r['variants'][v]['synthesis']['inferred_memory_count']=sm['num_memories']
 placed=load(run/'24-openroad-globalplacementskipio/state_out.json')
 if placed:
  m=placed['metrics'];r['variants'][v]['floorplan']={'die_area_mm2':m['design__die__area']/1e6,'core_area_mm2':m['design__core__area']/1e6,'placed_cell_area_mm2':m['design__instance__area']/1e6,'utilization':m['design__instance__utilization'],'routed':False,'initial_density_auto_adjustment':0.47 if v=='array_port' else None}
 grid=load(run/'30-checker-powergridviolations/state_out.json')
 if grid:r['variants'][v]['placed_power_grid']={'violation_count':grid['metrics'].get('design__power_grid_violation__count'),'routed_signoff':False}
 r['variants'][v]['rtl_constant_audit']=load(W/'evidence/rtl-constant-audit.json')
 activity=load(W/'evidence'/f'{v}-mapped-activity.json')
 r['variants'][v]['mapped_activity_attempt_guard']=load(W/'evidence'/f'{v}-activity-guard.json')
 if activity:
  r['variants'][v]['mapped_activity']=activity
  r['variants'][v]['power']['activity_source']=f'evidence/{v}-mapped-speech.saif'
  r['variants'][v]['power']['pre_route_activity_annotated']=not activity['annotation_coverage_pending']
  r['variants'][v]['power']['activity_annotated']=False # final routed netlist not checked
r['pre_route_diagnostics']=load(W/'evidence/pre-route-diagnostics.json')
r['tools']['native_simulation_compiler']=load(W/'evidence/native-simulation-compiler.json')
r['placement_bottleneck']=load(W/'evidence/array_port-placement-bottleneck.json')
r['tested_source_integrity']=load(W/'evidence/tested-source-integrity.json')
r['array_stop_receipt']=load(W/'evidence/array_port-v2-bounded-stop.json')
if not any(x['guard']['status']=='running' for x in r['variants'].values()):
 r['status']='bounded_physical_trial_incomplete'
 r['completion_note']='Functional implementation and tests delivered. Full physical projection has not been demonstrated; stopped/partial EDA receives no signoff credit.'
for v,x in r['variants'].items():
 x['extracted_timing_requested_corners']={c:{'status':'not_reached','setup_wns_ns':None,'hold_wns_ns':None,'achieved_mhz':None} for c in r['constraints']['STA_CORNERS']}
 x['signoff_complete']=False
 x['full_routed_projection_complete']=False
(W/'results.json').write_text(json.dumps(r,indent=2)+'\n')
print([(v,x['last_completed_step'],x['guard']['status']) for v,x in r['variants'].items()])
