#!/usr/bin/env python3
"""Run one postroute corner, preserving raw reports and honest power scope."""
import gzip, hashlib, json, os, re, shutil, subprocess, sys
from idle_accounting import mix_active_idle
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def inspect_vcd(path):
    # Streaming: never retain a potentially multi-GB gate-level trace in RAM.
    opener = gzip.open if str(path).endswith('.gz') else open
    header = []
    first = last = None
    declarations = scopes = 0
    in_header = True
    with opener(path, 'rt', errors='strict') as stream:
        for line in stream:
            line = line.strip()
            if in_header:
                header.append(line)
                declarations += int(line.startswith('$var '))
                scopes += int(line.startswith('$scope '))
                if line.startswith('$enddefinitions'):
                    in_header = False
            elif line.startswith('#'):
                value = int(line[1:])
                if first is None:
                    first = value
                if last is not None and value < last:
                    raise ValueError('Non-monotonic VCD timestamps')
                last = value
    match = re.search(r'\$timescale\s+(\d+)\s*(s|ms|us|ns|ps|fs)\s+\$end', ' '.join(header))
    if not match or first is None or last is None or last <= first:
        raise ValueError('Missing timescale or positive timestamp span')
    if first != 0:
        raise ValueError('Require #0 start: OpenSTA normalization of nonzero-start traces is not qualified here')
    unit = int(match[1]) * {'s': 1, 'ms': 1e-3, 'us': 1e-6, 'ns': 1e-9, 'ps': 1e-12, 'fs': 1e-15}[match[2]]
    return {'timescale_seconds': unit, 'first_timestamp': first, 'last_timestamp': last,
            'duration_seconds': (last - first) * unit, 'declarations': declarations,
            'scope_declarations': scopes, 'duration_scope': 'Entire emitted VCD; includes reset and drain if dumped'}


def parse_annotation(path):
    categories = {}
    for line in Path(path).read_text().splitlines():
        match = re.fullmatch(r'\s*([A-Za-z_][A-Za-z_ -]*)\s+(\d+)\s*', line)
        if match:
            categories[match[1].strip()] = int(match[2])
    if 'unannotated' not in categories or 'vcd' not in categories:
        raise ValueError('Unexpected report_activity_annotation format; retain raw report and extend parser explicitly')
    total = sum(categories.values())
    if total == 0:
        raise ValueError('No reported pin activities')
    return {'categories': categories, 'total_reported_pins': total,
            'direct_vcd_pins': categories['vcd'],
            'direct_vcd_pin_fraction': categories['vcd'] / total,
            'unannotated_pins': categories['unannotated'],
            'scope': 'OpenSTA pin activity-source counts, not nets, capacitance-weighted coverage or switching coverage'}


def parse_power(path):
    data = Path(path).read_text()
    if not re.search(r'Power\s*\(Watts\)', data):
        raise ValueError('Expected explicit report_power Watts heading')
    number = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
    pattern = re.compile(r'^\s*([A-Za-z]+)\s+(' + number + r')\s+(' + number + r')\s+(' + number + r')\s+(' + number + r')', re.M)
    groups = {}
    for match in pattern.finditer(data):
        groups[match[1]] = dict(zip(['internal_W', 'switching_W', 'leakage_W', 'total_W'], map(float, match.groups()[1:])))
    if 'Total' not in groups:
        raise ValueError('Missing report_power Total row')
    total = groups['Total']
    total['dynamic_W'] = total['internal_W'] + total['switching_W']
    # Report formatting rounds the independent sum; retain both original total and components.
    if abs(total['total_W'] - total['dynamic_W'] - total['leakage_W']) > max(1e-10, abs(total['total_W']) * 1e-5):
        raise ValueError('Power component sum differs materially from Total row')
    return {'groups': groups, 'total': total}


def summarize(output_dir, vcd, projections, rate, workload_kind="active"):
    coverage = parse_annotation(output_dir / 'activity-annotation.rpt')
    power = parse_power(output_dir / 'activity-power.rpt')
    default = parse_power(output_dir / 'default-power.rpt')
    duration = vcd['duration_seconds']
    energy_dynamic = power['total']['dynamic_W'] * duration / projections if projections else None
    energy_total = power['total']['total_W'] * duration / projections if projections else None
    actual_rate = projections / duration if projections else None
    real_time = None
    if rate is not None and workload_kind == 'active':
        real_time = {'requested_projections_per_second': rate,
                     'modeled_power_W': None,
                     'reason': 'Requires an actual compatible idle report; no clock-gating assumption is made.'}
    return {'corner': os.environ.get('W8_CORNER', 'unspecified'),
            'workload_kind': workload_kind,
            'scope': 'Postroute STA model estimate: standard cells and modeled net charging; excludes uncharacterized array internal dynamic and leakage',
            'activity_coverage': coverage, 'activity_power': power, 'default_power': default,
            'parasitic_annotation_report': (output_dir / 'parasitic-annotation.rpt').read_text(),
            'vcd': vcd, 'completed_projections_in_trace': projections,
            'observed_simulation_window_projection_rate_per_second': actual_rate,
            'supported_physical_rate_proven': False,
            'modeled_dynamic_J_per_projection_in_trace': energy_dynamic,
            'modeled_total_J_per_projection_in_trace': energy_total,
            'requested_rate_projection': real_time,
            'array_measured_energy_J_per_read': None, 'array_measured_reads_energy_J_per_projection': None,
            'complete_projection_energy_J': None, 'complete_projection_power_W': None,
            'limitations': [
                'Gate simulation without SDF is zero-delay activity: no extracted-delay glitches or timing correctness evidence.',
                'Entire VCD window is normalized; reset, load, drain and idle cycles are included if dumped.',
                'Direct pin coverage alone does not prove representative activity or correct mapped-cell waveforms.',
                'Unannotated activity may be propagated or defaulted by OpenSTA; retain measured coverage.',
                'Macro proxy has no internal power or leakage tables; a zero Macro report is not measured zero power.',
                'Macro pin load and slew assumptions affect modeled driver and net charging.',
                'W6 partial extracted energy cannot be multiplied into a measured full-row result.',
                'Any later array-energy addition must avoid double-counting drivers and net charging already in this report.',
                'An observed simulation rate does not establish timing closure or achievable silicon throughput.'
            ]}


def main():
    required = ['W8_LIB_LIST', 'W8_MACRO_LIB', 'W8_NETLIST', 'W8_TOP', 'W8_SDC',
                'W8_SPEF', 'W8_VCD', 'W8_OUT_DIR', 'W8_CORNER']
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise ValueError('Missing environment variables: ' + ', '.join(missing))
    output_dir = Path(os.environ['W8_OUT_DIR']).resolve()
    # Immutable per-run directory preserves failures and prevents mixing corner reports.
    output_dir.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env['W8_OUT_DIR'] = str(output_dir)
    env.setdefault('W8_SCOPE', 'tb/dut')
    files = [Path(p.strip()).resolve() for p in env['W8_LIB_LIST'].splitlines() if p.strip()]
    files += [Path(env[k]).resolve() for k in ['W8_MACRO_LIB', 'W8_NETLIST', 'W8_SDC', 'W8_SPEF', 'W8_VCD']]
    for path in files:
        if not path.is_file():
            raise FileNotFoundError(path)
    projections = int(env.get('W8_COMPLETED_PROJECTIONS', '1'))
    workload_kind = env.get('W8_WORKLOAD_KIND', 'active')
    if workload_kind not in ('active', 'idle') or (workload_kind == 'active' and projections < 1) or (workload_kind == 'idle' and projections != 0):
        raise ValueError('Use active with positive projection count, or idle with exactly zero')
    rate = float(env['W8_RATE_HZ']) if env.get('W8_RATE_HZ') else None
    if rate is not None and rate <= 0:
        raise ValueError('W8_RATE_HZ must be positive if supplied')
    provenance = {'inputs_sha256': {str(p): sha256(p) for p in files}, 'scope': env['W8_SCOPE'],
                  'correctness_scope': env.get('W8_ACTIVITY_NOTE', 'Gate correctness receipt not supplied to this runner'),
                  'activity_netlist_sha256': None, 'activity_netlist_matches_STA_netlist': None,
                  'activity_is_zero_delay': True, 'script_sha256': sha256(HERE / 'postroute_power.tcl')}
    if env.get('W8_ACTIVITY_NETLIST'):
        sim_hash = sha256(env['W8_ACTIVITY_NETLIST'])
        provenance['activity_netlist_sha256'] = sim_hash
        provenance['activity_netlist_matches_STA_netlist'] = sim_hash == sha256(env['W8_NETLIST'])
    design_hashes = [sha256(path) for path in files[:-1]]
    provenance['design_signature_sha256'] = hashlib.sha256(json.dumps(design_hashes).encode()).hexdigest()
    vcd = inspect_vcd(env['W8_VCD'])
    (output_dir / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    (output_dir / 'vcd-window.json').write_text(json.dumps(vcd, indent=2) + '\n')
    executable = env.get('W8_STA', 'sta')
    with (output_dir / 'sta.log').open('w') as log:
        process = subprocess.run([executable, '-no_splash', '-exit', str(HERE / 'postroute_power.tcl')], env=env,
                                 stdout=log, stderr=subprocess.STDOUT, check=False)
    log_text = (output_dir / 'sta.log').read_text()
    if process.returncode or re.search(r'^Error:', log_text, re.M):
        (output_dir / 'failure.json').write_text(json.dumps({'sta_exit_code': process.returncode, 'report':'sta.log'}, indent=2)+'\n')
        raise RuntimeError('OpenSTA failed; raw log preserved at ' + str(output_dir / 'sta.log'))
    result = summarize(output_dir, vcd, projections, rate, workload_kind)
    result['provenance'] = provenance
    if workload_kind == 'active' and rate is not None and env.get('W8_IDLE_RESULT'):
        idle = json.loads(Path(env['W8_IDLE_RESULT']).read_text())
        result['requested_rate_projection'] = mix_active_idle(result, idle, rate)
    result['warnings'] = [line for line in log_text.splitlines() if 'Warning:' in line]
    (output_dir / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"W8-POWER: {env['W8_CORNER']}; direct VCD coverage {result['activity_coverage']['direct_vcd_pin_fraction']:.4%}; complete-array energy remains unknown")


if __name__ == '__main__':
    main()
