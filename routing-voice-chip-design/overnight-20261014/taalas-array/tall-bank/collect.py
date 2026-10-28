"""Collect measured tall-bank evidence without promoting slice results to a macro."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

T = Path(__file__).resolve().parent
W = T.parent

def read(path):
    return json.loads(path.read_text())

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return {'bytes': path.stat().st_size, 'sha256': h.hexdigest()}

baseline = read(T / 'baseline64/results.json')
timing = read(T / 'timing/results.json')
verification = read(T / 'verification/results.json')

def summarize_extra(case):
    r = case['result']
    return {
        'path': case['path'], 'corner': r['corner'], 'period_ns': r['period_ns'],
        'protocol_pass': r['protocol_pass'], 'failures': r['failures'],
        'maximum_sampled_settled_ns_after_wl_command': r['maximum_sampled_settled_ns'],
        'partial_source_energy_pj_per_sampled_read': r['energy_pj_per_sampled_read'],
        'twenty_ns_after_wl_probe': r['command_to_capture_20ns_probe'],
        'samples_checked': r['samples_checked'], 'scope': r['scope'],
        'source_gds_sha256': r['source_gds_sha256'], 'deck_sha256': r['deck_sha256'],
        'trace_sha256': r['trace_sha256'],
        'additional_model': case.get('model'),
    }

extras = {key: [summarize_extra(c) for c in timing.get(key, [])]
          for key in ('additional1280_fullpattern_cases', 'supplemental_fullbank_control_load_sensitivity')}
b64 = baseline['full20_partial_readout_assembly']
variants = []
old_cases = baseline['joined32_lane_bank_timing_energy']['cases']
variants.append({
    'rows_per_bank': 64, 'banks': 20, 'readout_count': 25600,
    'assembly_dimensions_um': b64['dimensions_um'],
    'partial_macro_area_um2': b64['area_um2'],
    'partial_macro_um2_per_selection': b64['area_um2'] / 409600,
    'gds': b64['gds'], 'gds_sha256': b64['gds_sha256'],
    'drc_markers': b64['drc']['drc_markers'],
    'all_bits_mismatches': b64['layout_bit_readback']['mismatches'],
    'full_bank_lvs': {'pass': True, 'devices': 87040, 'source': 'integrated/lvs-result.json'},
    'timing_method': 'Retained32lane bank0; idealWL/PC, extractedC, no distributedR; prechargeW1.44',
    'worst_sampled_settling_ns_after_wl_command': {
        c: max(x['maximum_sampled_settled_time_ns_after_evaluate'] for x in old_cases if x['corner'] == c)
        for c in ('typical', 'ss')},
    'energy_pj_per_sampled_read': {
        c: next(x['mean_net_source_energy_pj_per_32_lane_row_read'] for x in old_cases if x['corner'] == c and x['period_ns'] == 20)
        for c in ('typical', 'ss')},
    'energy_scope': '32lane extractedC bank0 net source energy at20ns; idealcontrols, no distributedR',
    'minimum_common_tested_TT_SS_passing_interval_ns': 20,
    'conditional_slice_interleave_factor_for20ns': 1,
    'full320lane_bank_read_time_ns': None, 'full320lane_bank_energy_pj': None,
    'complete_macro_timing_proven': False,
})
for rows in (320, 1280):
    d = T / f'r{rows}'
    g = read(d / 'geometry.json')
    tv = timing['variants'][str(rows)]
    drc = read(d / 'assembly-drc.json') if (d / 'assembly-drc.json').exists() else None
    rb = read(d / 'readback.json')
    assert rb['compared_bits'] == 1638400 and rb['mismatches'] == 0
    independent_rb = verification[f'r{rows}_all_bits']
    assert independent_rb['all_match']
    assert independent_rb['gds_sha256'] == g['gds_sha256']['assembly.gds']
    assert sum(b['compared_bits'] for b in independent_rb['banks']) == 1638400
    assert independent_rb['identity']['all409600_indices_match']
    assert abs(g['assembly_area_um2'] / 409600 - g['assembly_um2_per_selection']) < 1e-9
    if drc:
        assert drc['gds_sha256'] == g['gds_sha256']['assembly.gds']
    cases = tv['cases']
    interval = tv['minimum_common_tested_TT_SS_passing_interval_ns']
    energy = {}
    worst = {}
    worst_paths = {}
    chosen = {}
    for corner in ('typical', 'ss'):
        passed = [x for x in cases if x['corner'] == corner and x['protocol_pass']]
        extra = extras['additional1280_fullpattern_cases'] if rows == 1280 else []
        passing_for_delay = passed + [x for x in extra if x['corner'] == corner and x['protocol_pass']]
        slowest = max(passing_for_delay, key=lambda x: x['maximum_sampled_settled_ns_after_wl_command'], default=None)
        worst[corner] = slowest['maximum_sampled_settled_ns_after_wl_command'] if slowest else None
        worst_paths[corner] = slowest['path'] if slowest else None
        selected = next((x for x in passed if x['period_ns'] == interval), None)
        energy[corner] = sum(selected['partial_source_energy_pj_per_sampled_read'].values()) if selected else None
        chosen[corner] = selected['path'] if selected else None
    variants.append({
        'rows_per_bank': rows, 'banks': g['bank_count'], 'readout_count': g['readout_count'],
        'bank_dimensions_um': g['bank_dimensions_um'], 'assembly_dimensions_um': g['assembly_dimensions_um'],
        'partial_macro_area_um2': g['assembly_area_um2'],
        'partial_macro_um2_per_selection': g['assembly_um2_per_selection'],
        'area_reduction_vs64_percent': 100 * (1 - g['assembly_area_um2'] / b64['area_um2']),
        'gds': f'tall-bank/r{rows}/assembly.gds', 'gds_sha256': g['gds_sha256']['assembly.gds'],
        'drc_markers': drc['markers'] if drc else None, 'drc': drc,
        'layout_readback': rb,
        'independent_layout_readback': independent_rb,
        'full_bank_lvs': ({'pass': verification['full320_bank']['lvs']['monolithic_netgen']['pass'],
                          'bank': 3, 'devices': 414720,
                          'source': 'tall-bank/verification/results.json'} if rows == 320 else
                         {'pass': None, 'status': 'Not run; optional variant has slice topology check only'}),
        'row_mapping': g['row_mapping'], 'exclusions': g['exclusions'],
        'timing_method': 'pre2std4 stockdrivers, actualMagicC, geometry-derived distributedR; sampled16active columns+128receivers',
        'timing_status': tv['status'], 'timing_directory': tv['directory'],
        'timing_cases': cases, 'corners': tv['corners'],
        'timing_timeouts': tv.get('timeouts', []),
        'timing_numerical_failures': tv.get('numerical_failures', []),
        'worst_sampled_settling_ns_after_wl_command': worst,
        'worst_sampled_settling_case_paths': worst_paths,
        'energy_pj_per_sampled_read': energy, 'energy_case_paths': chosen,
        'energy_scope': 'Sum of recorded pr/pw/pp/pa finite-window sources;16active columns+128receivers, selectedWL/PC buffers and idealaggressors; not1280bit row energy',
        'minimum_common_tested_TT_SS_passing_interval_ns': interval,
        'conditional_slice_interleave_factor_for20ns': tv['conditional_slice_interleave_factor_for20ns'],
        'full320lane_bank_read_time_ns': None, 'full320lane_bank_energy_pj': None,
        'complete_macro_timing_proven': False,
    })

comparison = {
    'generated_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Measured array+analogreadout partialmacro rectangles; global decoder/mux/control/outputlatches and fullPG excluded',
    'complete_macro': False, 'variants': variants,
    'source_timing_results': 'tall-bank/timing/results.json',
    'source_verification_results': 'tall-bank/verification/results.json',
    'preserved_timing_failures': timing['preserved_failures'],
    'supplemental_fullbank_control_load_sensitivity': extras['supplemental_fullbank_control_load_sensitivity'],
    'additional1280_fullpattern_cases': extras['additional1280_fullpattern_cases'],
    'all_timing_timeouts': timing.get('all_timeouts', []),
    'baseline_method_comparable': False,
    'full_row_energy_pj': None,
    'complete_projection_area_um2': None,
    'limitations': timing['limitations'],
}
dump(T / 'results.json', comparison)

def num(x, digits=3):
    return 'not measured' if x is None else f'{x:.{digits}f}'

def pair(v, field):
    a = v[field]
    return f"{num(a['typical'])} / {num(a['ss'])}"

lines = [
    '# W5 tall-bank comparison', '',
    '**The 320-row layout reduces the measured array/readout assembly from 22.3212 to 12.4401 mm² (44.3%).** Four striped banks replace twenty 64-row banks. The optional single 1,280-row bank measures 10.5022 mm². These are physical GDS bounding rectangles, including unused routing space, not receiver-count area estimates.', '',
    'The table includes cells, physical precharge/keeper/inverter readouts and actual local joining/control/ground wires. **Global decoder/mux/control, physical WL/PC drivers, output latches and interbank PDN remain excluded.** A complete macro area and achieved ARRAY-PORT clock are not established.', '',
    '| Rows/bank | Banks | Measured partial macro area, mm² | µm²/selection incl. local readout | Readouts | Worst sampled settling TT / SS, ns | Sampled energy TT / SS, pJ/read | Tested common reuse interval, ns | Conditional banks for 20 ns initiation |',
    '|---:|---:|---:|---:|---:|---:|---:|---:|---:|',
]
for v in variants:
    lines.append(f"| {v['rows_per_bank']} | {v['banks']} | {v['partial_macro_area_um2']/1e6:.7f} | {v['partial_macro_um2_per_selection']:.6f} | {v['readout_count']:,} | {pair(v, 'worst_sampled_settling_ns_after_wl_command')} | {pair(v, 'energy_pj_per_sampled_read')} | {num(v['minimum_common_tested_TT_SS_passing_interval_ns'],0)} | {num(v['conditional_slice_interleave_factor_for20ns'],0)} |")
lines += [
    '',
    '**Timing and energy scope:** TT is 3.30 V/25°C; SS is 2.97 V/125°C. Settling is measured after the WL command, and is the worst sample among passing retained protocols, not end-to-end macro latency. The 64-row baseline uses ideal drivers, extracted capacitance without distributed resistance, a 1.44 µm precharge device and 32 fully active lanes. New variants use the retained `pre2std4` 2.88 µm precharge receiver, extracted stock drivers, actual layout capacitance and geometry-derived resistance. Their energy is the sum of finite-window source energies for **16 active bit columns plus 128 readouts**, selected drivers and ideal aggressors. Complete 1,280-bit row energy remains **unknown for every row of this table**. The different test scopes prevent an apples-to-apples energy/speed ratio.', '',
    'The optional 1,280-row energy pair uses matching compact TT/SS sequences. Its worst SS settling also includes the broader SS-only sequence, which is retained as additional evidence. The compact SS sequence alone already fails six data probes at 20 ns after WL command. No 20 ns latency claim follows from a passing 60 ns protocol. The supplemental 320-row control-load model is a different circuit scope and is reported separately below.', '',
    'The conditional factor is `ceil(tested passing complete protocol interval / 20 ns)`. It includes the sampled precharge/read/recovery sequence; it is not computed from threshold delay. It is a sufficient factor for that sampled slice protocol, not a proven minimum or full-bank throughput result. Failed shorter protocols remain in the timing report. Four striped 320-row banks revisit each bank every 80 ns under the hypothetical 20 ns request stream, or every 240 ns with current W2b requests 60 ns apart. A single 1,280-row bank provides no interleaving; any larger factor would require full-image replication or a new partition and a new area measurement.', '',
    '## Retained protocol trials', '',
]
for v in variants[1:]:
    for c in v['timing_cases']:
        f = c['failures']
        outcome = 'PASS' if c['protocol_pass'] else 'FAIL'
        lines.append(f"* {v['rows_per_bank']}-row {c['corner']}, {c['period_ns']:g} ns interval: **{outcome}**; output/raw/precharge/phase failures {f['output']}/{f['raw']}/{f['precharge']}/{f['phase']}; {c['samples_checked']} sampled checks.")
for label, key in [('Additional 1,280-row full-pattern sample', 'additional1280_fullpattern_cases'),
                   ('Supplemental 320-row full-control-load sensitivity', 'supplemental_fullbank_control_load_sensitivity')]:
    for c in extras[key]:
        f = c['failures']
        outcome = 'PASS' if c['protocol_pass'] else 'FAIL'
        lines.append(f"* {label}, {c['corner']}, {c['period_ns']:g} ns: **{outcome}**; maximum sampled settling {c['maximum_sampled_settled_ns_after_wl_command']:.6f} ns; output/raw/precharge/phase failures {f['output']}/{f['raw']}/{f['precharge']}/{f['phase']}. This is supplemental evidence; its exact circuit and sampling scope remain in the timing report.")
lines += [
    '',
    'Numerical timestep failures are preserved separately in the timing report and are not scored as electrical passes or electrical failures. ' + ('Incomplete timeout traces are also retained. ' if timing.get('all_timeouts') else 'No final timing case timed out. ') + 'The shortest tested passing interval is not a proof of the minimum possible interval. See each retained deck for the exact precharge guard and capture sample times.', '',
    '## Physical verification', '',
    '| Rows/bank | Assembly dimensions, µm | Selected full-assembly DRC markers | Independent bit readback | Full-bank LVS |',
    '|---:|---:|---:|---|---|',
]
for v in variants:
    dims = ' × '.join(num(x,2) for x in v['assembly_dimensions_um'])
    passed = v['full_bank_lvs']['pass']
    lvs = ('pass' if passed is True else 'fail') + f"; {v['full_bank_lvs'].get('devices',0):,} devices" if passed is not None else 'not run'
    if passed is not None:
        lvs += ', bank3' if v['rows_per_bank'] == 320 else ', tile0'
    lines.append(f"| {v['rows_per_bank']} | {dims} | {v['drc_markers'] if v['drc_markers'] is not None else 'pending'} | all 1,638,400 bits match | {lvs} |")
lines += [
    '',
    'The 320-row full-bank reference independently decodes the original packed K64 tensor and checks it against W2b RTL. Monolithic Netgen passes with no property errors, supported by exact device-graph/W/L comparison, ten passing partitions and a shared-net audit. A doubled-width negative control is rejected. DRC uses the reused official GF180 FEOL/BEOL/connectivity/off-grid rules; density and antenna are excluded. No foundry signoff claim is made. The optional 1,280-row variant has no full-bank LVS claim.', '',
    'The final required 320-row timing group is bank3/group2, containing the worst ranked column among all 1,280 columns of the extracted bank3 by an explicit-capacitance/geometry-resistance proxy. That proxy and sampled sequences do not prove a global worst case over all four banks. The earlier group3 timing runs remain separately recorded. The optional 1,280-row sample is independently extracted from its actual programmed layout; its ranking and scope are in the timing report. Its compact authoritative sequence alternates far rows 1,278/1,279 twice, exercising one/zero on the selected worst-ranked bit. This reduced coverage is not equivalent to the required 320-row near/far/activity sequence.', '',
    '## Integration and evidence', '',
    'Physical 320-row placement is striped: `logical_row = bank + 4*local_row`. Use `bank = row[1:0]`, `local_row = row[10:2]`; keep W2b representative/codebook selection tied to the original logical row. Each bank has ten 32-lane subbanks, common long WL/PC rails, and one set of 1,280 readouts. Stock drivers in the timing harness are not placed in these GDS banks.', '',
    'W2b requests 1,280 rows in 4,160 integer cycles (4,163 with FP32 drain), normally one request every three cycles. Its INDEX capture aperture is still one cycle, and its real representative register follows a combinational lookup. Bank interleaving does not remove this latency/setup requirement. Complete-row control loading, output selection, capture phases and the logical row tag require physical and protocol closure. Hard-macro placement beside W2b remains skipped; there is no complete qualified hard macro to place.', '',
    'The unchanged retained cell-only specimen remains **4.8684604443 µm²/selection**. Taller layouts retain the wide horizontal readout strip and joining geometry, so much of each rectangle is unused width. Their areas are measured implementations, not optimal lower bounds.', '',
    '* [320-row GDS](r320/assembly.gds), [geometry](r320/geometry.json), [DRC](r320/assembly-drc.json).',
    '* [1,280-row GDS](r1280/assembly.gds), [geometry](r1280/geometry.json), [DRC](r1280/assembly-drc.json).',
    '* [Independent verification](verification/RESULTS.md), [machine evidence](verification/results.json).',
    '* [Timing and preserved failures](timing/RESULTS.md), [machine evidence](timing/results.json).',
    '* [Integration contract](INTEGRATION.md), [exact commands](COMMANDS.md), [comparison JSON](results.json).',
    '',
]
text = '\n'.join(lines)
(T / 'RESULTS.md').write_text(text)
root_section = text.replace('](r320/', '](tall-bank/r320/').replace('](r1280/', '](tall-bank/r1280/').replace('](verification/', '](tall-bank/verification/').replace('](timing/', '](tall-bank/timing/').replace('](INTEGRATION.md)', '](tall-bank/INTEGRATION.md)').replace('](COMMANDS.md)', '](tall-bank/COMMANDS.md)').replace('](results.json)', '](tall-bank/results.json)')
(W / 'RESULTS.md').write_text(root_section + '\n---\n\n' + (T / 'baseline64/RESULTS.md').read_text())
baseline['generated_utc'] = comparison['generated_utc']
baseline['status'] = 'Measured tall-bank area and scoped physical/timing evidence; complete macro remains unqualified'
baseline['current_followup'] = 'tall-bank/results.json'
baseline['prior64_handoff_fields_retained'] = 'Original top-level fields describe the retained64row experiments; current320/1280variant evidence is in tall_bank_comparison'
baseline['tall_bank_comparison'] = comparison
baseline['resource_scope']['observed_free_gib_at_report'] = shutil.disk_usage('/').free / 2**30
dump(W / 'results.json', baseline)

manifest = read(T / 'baseline64/artifact-manifest.json')
extra = ['tall-bank/RESULTS.md', 'tall-bank/results.json', 'tall-bank/INTEGRATION.md', 'tall-bank/COMMANDS.md', 'tall-bank/build.py', 'tall-bank/check_drc.py', 'tall-bank/collect.py', 'tall-bank/verification/results.json', 'tall-bank/timing/results.json']
for rows in (320, 1280):
    extra += [f'tall-bank/r{rows}/{name}' for name in ('assembly.gds', 'geometry.json', 'readback.json', 'assembly-drc.json')]
for name in list(manifest) + extra:
    path = W / name
    if path.exists():
        manifest[name] = digest(path)
dump(W / 'artifact-manifest.json', manifest)
print('W5-STATUS: comparison reports collected; full-macro timing/energy remain unqualified')
