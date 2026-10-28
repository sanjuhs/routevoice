"""Mix actual active/idle STA reports without assuming clock gating."""
import hashlib,json
from pathlib import Path


def mix_active_idle(active, idle, rate):
    if active.get('workload_kind') != 'active' or idle.get('workload_kind') != 'idle':
        raise ValueError('Expected active report and explicit idle report')
    if idle['completed_projections_in_trace'] != 0 or active['completed_projections_in_trace'] < 1:
        raise ValueError('Invalid active/idle projection counts')
    if active['corner'] != idle['corner']:
        raise ValueError('Active and idle PVT/RC corner names differ')
    a = active['provenance'].get('design_signature_sha256')
    b = idle['provenance'].get('design_signature_sha256')
    if not a or a != b:
        raise ValueError('Active/idle libraries, macro model, netlist, SDC or SPEF differ')
    if rate <= 0:
        raise ValueError('Rate must be positive')
    seconds = active['vcd']['duration_seconds'] / active['completed_projections_in_trace']
    duty = rate * seconds
    pa = active['activity_power']['total']['total_W']
    pi = idle['activity_power']['total']['total_W']
    supports = duty <= 1
    return {'kind': 'conditional always-clocked active/idle mixture',
            'requested_projection_rate_Hz': rate,
            'actual_general_streaming_rate_measured': False,
            'active_trace_seconds_per_projection': seconds,
            'active_duty_fraction': duty,
            'fits_observed_trace_window_rate': supports,
            'active_mean_modeled_power_W': pa,
            'idle_mean_modeled_power_W': pi,
            'conditional_modeled_power_W': pa*duty + pi*(1-duty) if supports else None,
            'formula': 'P_active*(R*T_active_per_projection) + P_idle*(1-R*T_active_per_projection)',
            'idle_includes_running_clock': True,
            'complete_array_internal_power_W': None,
            'complete_projection_power_W': None,
            'physical_timing_supported': False,
            'assumptions': ['Both traces represent the same always-clocked implementation, period, PVT and extracted RC.',
                            'Trace means include their dumped reset and drain overhead; this is not steady-state idle unless the idle trace excludes or amortizes those cycles.',
                            'Active/idle transitions outside trace windows are not separately modeled.',
                            'No array internal dynamic or leakage power is characterized.',
                            '50 projections/s, if supplied, is only a conditional single-pass/no-replay example; general streaming invocation rate remains unknown.']}
