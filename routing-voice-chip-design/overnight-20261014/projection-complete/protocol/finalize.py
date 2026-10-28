from pathlib import Path
import json
W=Path(__file__).resolve().parent; D=W/'ss-120ns'; r=json.loads((D/'result.json').read_text());loads=json.loads((W/'input_loads.json').read_text());p=r['protocol']; e=r['energy_pj_per_sampled_read'];summary={k:r[k] for k in ['protocol_pass','failures','maximum_sampled_settled_ns','energy_pj_per_sampled_read','samples_checked','maximum_observed_endpoint_voltage_difference_v','full_bank_timing_proven','full_row_energy_pj','reset_abort_qualified','wall_seconds']};summary.update({'status':'sampled_SS_120ns_protocol_pass' if r['protocol_pass'] else 'sampled_SS_120ns_protocol_fail','protocol':p,'scope':r['scope'],'source_energy_sum_pj_per_sampled_read':sum(e.values()),'corners_measured':['ss_2.97V_125C'],'real_row_sequence':[0,1,1279,1274,546]*2,'output_load_fF':10,'minimum_actual_parent_row_cadence_ns':180,'parent_cadence_evidence':'Parent provided RTL schedule; not measured by this analog run','full_bank_MHz':None,'full_bank_energy_projection_pJ':None,'20ns_capture_probe_failures':sum(q['data_failures'] for q in r['command_to_capture_20ns_probe']),'result_file':'ss-120ns/result.json','input_loads_file':'input_loads.json'})
(W/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
text=f'''# W8 sampled synchronous protocol result

**{summary['status']}.** Real native SS SPICE completed in{r['wall_seconds']:.3f}s. Capture80ns passes all{r['samples_checked']}combined early/late output sample checks with raw, precharge and phase checks. Failures:{r['failures']}. Maximum sampled settling after WL command:{r['maximum_sampled_settled_ns']:.6f}ns. These are sampled partial-slice circuit estimates, not full-bank timing closure.

Exact20ns-edge construction: active-low PC rises20ns, WL rises40ns, first capture80ns, retention sample99.5ns, WL falls100ns, PC falls120ns. Each command's0.2ns source edge follows that time. Real row pattern[0,1,1279,1274,546]repeats twice;10fF output loads; SS2.97V125C. The parent180ns minimum row cadence is a separate RTL scheduling statement.

Finite-window source energy over the second repeated sequence:[600,1200]ns:

|Source|pJ per sampled read|
|---|---:|
|Receiver/pr|{e['pr']:.9f}|
|WL source/pw|{e['pw']:.9f}|
|PC source/pp|{e['pp']:.9f}|
|Ideal legal-state aggressor/pa|{e['pa']:.9f}|
|Net sum|{sum(e.values()):.9f}|

Scope is16active fullheight columns,112ideal legal-state bitline aggressors and128physical receivers, selected stockWL/PCdrivers, extracted MOS/C and geometry-derivedR. Maximum observed endpoint voltage difference:{r['maximum_observed_endpoint_voltage_difference_v']:.9g}V. Complete internal charge periodicity is not proven. Full1,280-bit row energy remainsnull. Do not multiply these components into a measured full-row energy.

No fastest safe full-bank period is established.120ns is the20ns-clock candidate actually sampled here. A100ns candidate would combine capture/WLoff on the same edge and requires its own hold/protocol proof; it remains unrun. Full-bank sharedWL/PCfanout, controls/decoder, outputlatch/setup/hold, PDN/return/current, simultaneous allcolumn evaluation and analog reset-abort behavior remain unqualified. The20ns command-to-capture probe still fails{summary['20ns_capture_probe_failures']}bit checks in this run.

Actual128-column-crop input loading is in[input_loads.json](input_loads.json): WLmetal24.69543–26.50314fF plus128NMOS0.36/0.28; PCmetal151.56014fF plus128PMOS2.88/0.28. Full-bank structural gate counts are1280each, but full-bank effective pin capacitance is uncharacterized. The clockless macro should not advertise fabricated clock-to-out/setup arcs. Preliminary WL-to-OUT timing and any electrical load estimates must remain labelledderived/conditional.

Evidence:[result.json](ss-120ns/result.json),[generated deck](ss-120ns/test.cir),[compressed trace](ss-120ns/trace.dat.gz),[watchdog extension](ss-120ns/watchdog-extension.json),[reading receipt](reading.json),[details](README.md). Original480s watchdog extended to720s by parent authorization without native restart. Only the waitingPython launcher was paused; native SPICE continued unchanged.
'''
(W/'RESULTS.md').write_text(text)
print(json.dumps(summary,indent=2))
