"""Build the W6 status ledger from retained evidence; never infer pending passes."""
from pathlib import Path
import argparse
import datetime
import json

W = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--final', action='store_true', help='Mark the scoped handoff finished, retaining incomplete measurements.')
args = parser.parse_args()

def read(relative):
    path = W / relative
    return json.loads(path.read_text()) if path.exists() else None

layouts = {}
for height in (64, 1280):
    lvs_run = f'r{height}-v2'
    layouts[str(height)] = {
        'geometry': read(f'r{height}-v2/geometry.json'),
        'selected_drc': read(f'r{height}-v2/drc-result.json'),
        'readback': read(f'r{height}-v2/readback.json'),
        'lvs_receipt': f'verification/{lvs_run}/full-bank-netgen-result.json',
        'lvs': read(f'verification/{lvs_run}/full-bank-netgen-result.json'),
        'negative': read(f'verification/{lvs_run}/negative-width-netgen-result.json'),
    }
g = layouts['1280']['geometry']
density = g['um2_per_selection']
whole = 31_457_280 * density / 1e6
timing = read('timing/results.json')
missing = [
    'Measured energy for a complete simultaneous 1,280-bit row read',
    'Placed decoder, WL/PC drivers and phase controller',
    'Output latches and output escape routing',
    'Global PDN integrity and full simultaneously active row power',
    'Downstream codebooks, shared products, accumulation and full recognizer',
]
for height, evidence in layouts.items():
    if not (evidence['lvs'] or {}).get('pass'):
        missing.append(f'Full {height}-row Netgen LVS pass')
    if not (evidence['negative'] or {}).get('negative_control_rejected'):
        missing.append(f'Full {height}-row negative-control rejection')
passing_corners = {
    case.get('corner') for case in (timing or {}).get('cases', [])
    if case.get('protocol_pass') is True
}
for corner in ('typical', 'ss'):
    if corner not in passing_corners:
        missing.append(f'Completed passing extracted {corner} timing case')
cap_receipts = (timing or {}).get('full_bank_capacitance_receipts') or {}
if cap_receipts.get('status') != 'complete':
    missing.append('Global full-bank capacitance ranking')
candidate_checks = (timing or {}).get('full_bank_proxy_candidate_characterization') or {}
if candidate_checks.get('sampled_TT_SS_protocol_complete') is not True:
    missing.append('Passing TT and SS characterization of the globally ranked load-proxy candidate')

report = {
    'status': 'partial' if args.final else 'in_progress',
    'handoff_finished': args.final,
    'artifact_manifest': 'artifact-manifest.json',
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'architecture': 'P2 stored-address mask-programmed index branch: four access NMOS per four-bit selection, one pre2/keeper/restoring inverter per bit; downstream shared products excluded',
    'chosen_option': 'A: eight staggered rows; no column multiplexing or additional subphases',
    'image_shape': [1280, 320],
    'selections': 409600,
    'bitcells': 1638400,
    'layouts': layouts,
    'area': {
        'bank_area_um2': g['area_um2'],
        'bank_area_mm2': g['area_um2'] / 1e6,
        'um2_per_selection_including_analog_readout': density,
        'W5_um2_per_selection': {
            '64row20tile_assembly': 54.4950341796875,
            '320row4bank_assembly': 30.371291,
            '1280row_bank': 25.640028,
        },
        'reduction_vs_W5_1280_fraction': 1 - density / 25.640028,
        'whole_model_uniform_density_extrapolation': {
            'selections': 31457280,
            'formula': '31457280 * measured_bank_area_um2 / 409600 / 1000000',
            'area_mm2': whole,
            'qualification': 'Uniform 1,280-row rectangular density projection, not layout of 98 model tensors. No padding, shape, port or replication allocation performed.',
        },
        'october_component_budget_mm2': {
            'base_arrays': 153.833,
            'receiver_strips': 11.004,
            'decoder_cells': 25.002,
            'wordline_driver_cells': 30.369,
            'precharge_driver_cells': 0.269,
            'bank_selector_cells': 0.944,
            'total': 221.421,
        },
        'mixed_estimate_only_mm2': {
            'formula': 'W6 uniform array/readout extrapolation + October decoder/WL-driver/PC-driver/selector component terms',
            'additional_old_nonreceiver_components': 56.584,
            'sum': whole + 56.584,
            'qualification': 'Engineering estimate only: neither placed nor complete macro, different allocation/utilization scopes. Does not add the 11.004 mm2 receiver term again.',
        },
    },
    'timing': timing,
    'independent_verification': read('verification/results.json'),
    'independent_geometry_audit': read('audit/geometry-audit.json'),
    'independent_final_audit': read('audit/final-audit.json'),
    'required_measurements': {
        'selected_drc_64_and_1280': {
            'pass': all((item['selected_drc'] or {}).get('drc_markers') == 0 for item in layouts.values()),
            'scope': 'Selected GF180 FEOL, BEOL, connectivity and off-grid; density and antenna excluded',
        },
        'independent_full_lvs_and_negative_64_and_1280': {
            'pass': all((item['lvs'] or {}).get('pass') is True and (item['negative'] or {}).get('negative_control_rejected') is True for item in layouts.values()),
            'reference': 'Independent original packed-tensor reference; exact raw graph/model/W/L plus monolithic Netgen',
        },
        'layout_bits_readback': {
            'pass': all((item['readback'] or {}).get('mismatches') == 0 for item in layouts.values()),
            'full_bank_bits': 1638400,
            'independent_original_source_audit': 'verification/results.json',
        },
        'extracted_timing_and_row_energy': {
            'status': 'partial',
            'global_load_proxy_candidate_TT_SS_pass': candidate_checks.get('sampled_TT_SS_protocol_complete') is True,
            'global_transient_worst_case_proven': False,
            'complete_1280_bit_row_energy_pj': None,
            'scope': 'Sampled extracted candidate columns and separately labeled control-loading sensitivities. Partial slice and receiver MOS energy are measured; complete simultaneous-row energy remains unmeasured.',
        },
        'measured_area_and_model_extrapolation': {
            'pass': True,
            'measured_scope': 'GDS array, analog readout and local/common wiring; output escape and placed control drivers excluded',
            'whole_model_result_kind': 'Uniform-density engineering extrapolation, not a whole-model layout',
        },
    },
    'complete_row_energy_pj': None,
    'twenty_ns_capture_supported': False,
    'twenty_ns_capture_status': 'Sampled SS cases fail the 20 ns aperture after WL command. See timing.failed_20ns_aperture_checks for each retained case. Decoder, lookup and setup are excluded.',
    'complete_macro': False,
    'complete_projection': False,
    'whole_model_die_fit_proven': False,
    'subwatt_proven': False,
    'missing': missing,
    'failures': [{
        'artifact': 'r64-v1',
        'DRC_markers': 160,
        'categories': {'M3.2a': 80, 'V4.3b': 80},
        'fix': 'Receiver horizontal origin shifted 0.09 um; lower ground via row moved 0.4 um higher. Original GDS, log and build-v1.py retained.',
    }],
    'resource_contract': {
        'workspace_only': 'overnight-20261014/taalas-pitch',
        'min_free_disk_GiB': 22,
        'max_threads': 4,
        'no_git': True,
        'no_cloud': True,
    },
}
(W / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
print(f"W6-STATUS: ledger refreshed; bank {g['area_um2'] / 1e6:.8f} mm2; uniform extrapolation {whole:.6f} mm2", flush=True)
