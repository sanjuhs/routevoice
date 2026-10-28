# W8 postroute power recipe

`run_power.py` runs `postroute_power.tcl` in one fresh OpenSTA process per selected PVT/RC corner and writes immutable raw reports, input hashes and `results.json`. **The complete W8 projection power run is not yet executed.** Parent supplies the actual mapped/routed gate VCD and checks its numerical outputs. No additional cloud job was launched by this worker.

The runner reads standard-cell Liberty file(s), the explicitly provisional macro Liberty, actual postroute netlist, SDC and extracted SPEF, then applies `read_vcd -scope tb/dut`. It reports default power before annotation, annotated power afterward, raw parasitic coverage and the actual VCD pin-annotation fraction. Zero macro internal/leakage tables remain missing data, never measured zero power.

Required environment:

| Variable | Meaning |
| --- | --- |
| `W8_LIB_LIST` | Newline-separated absolute standard-cell Liberty paths for one selected corner. |
| `W8_MACRO_LIB` | Corrected `macro/PITCH_BANK_R1280.lib`; an engineering proxy, not full-bank corner characterization. |
| `W8_NETLIST` | Actual postroute netlist to analyze. |
| `W8_TOP` | `rv_k64_projection_complete`. |
| `W8_SDC` | Constraints matching that netlist and the activity clock period. |
| `W8_SPEF` | Actual extracted RC file for the selected corner. |
| `W8_VCD` | Gate-level VCD for one captured-speech activation vector, starting at timestamp zero. |
| `W8_OUT_DIR` | A NEW directory for this corner/run; existing directories are rejected to preserve evidence. |
| `W8_CORNER` | Explicit name identifying PVT and RC assumptions. |

Optional environment:

| Variable | Default and meaning |
| --- | --- |
| `W8_STA` | `sta`; can be the absolute executable. |
| `W8_SCOPE` | `tb/dut`; slash-delimited DUT scope actually present in VCD. |
| `W8_ACTIVITY_NETLIST` | Gate-simulation netlist; hash equality with STA netlist is recorded when provided. |
| `W8_ACTIVITY_NOTE` | Text identifying the correctness receipt and source-vector provenance. |
| `W8_WORKLOAD_KIND` | `active`; use `idle` for a no-projection trace. |
| `W8_COMPLETED_PROJECTIONS` | `1` for active; set exactly `0` for idle. |
| `W8_IDLE_RESULT` | Optional compatible idle `results.json` used to mix active and idle means when a rate is supplied. |
| `W8_RATE_HZ` | Unset, so real-time-rate power remains unknown. Supply an explicitly qualified projections/second rate. The protocol review supports a conditional50Hz single-pass/no-replay example; the general streaming rate remains unknown. |
| `W8_HIGHEST_INSTANCES` | Unset, so instance ranking is skipped. Optional count must not exceed instance count; a local one-cell request for20 trapped the tool. |

After exporting those variables in the existing pod's Nix shell:

```sh
python3 /workspace/rv/overnight-20261014/projection-complete/power/run_power.py
```

Repeat in fresh directories for each PVT/RC combination. Keep concurrency within the parent's existing CPU cap. The runner does not create pods, modify the design, pick a clock period or launch routing.

## Activity and output interpretation

W2b's retained RTL trace annotated only1,388 of1,253,320 reported pins (0.1107459%). Header-only flattening did not improve that coverage. Gate simulation should expose actual mapped leaf instances and their input/output pins, including underscore-prefixed cells; Verilator's `--trace-underscore` is relevant. Trace depth must retain leaf-pin scopes under `tb/dut`. Do not claim successful annotation from a VCD's size or merely from an “Annotated” log line. The exported fraction comes from `report_activity_annotation`: direct `vcd` count divided by all reported source categories, including `unannotated`. This is pin coverage, not capacitance-weighted or switching-weighted coverage.

The parser requires the native report's explicit `(Watts)` heading and reads the Internal, Switching, Leakage and Total columns. Dynamic power is Internal + Switching. Although `report_units` lists the library power unit as1µW, installed OpenSTA's `sta::report_power_design` emits these report columns in SI Watts; its inspected Tcl body is preserved in `report_power_design_source.log`. The code does not accidentally multiply those Watts by a library-unit factor.

For an entire trace lasting T seconds with N complete vectors:

- modeled dynamic energy per trace-normalized projection = dynamic_W × T / N;
- modeled total energy per trace-normalized projection = total_W × T / N;
- observed simulation-window rate = N / T, not physically proven throughput;
- if rate R and an actual compatible idle report are supplied, conditional always-clocked power = P_active × (R × T/N) + P_idle × (1 − R × T/N).

The mixture uses the measured trace means, including running-clock idle switching and each report’s leakage. It makes no clock-gating assumption. Active and idle reports must use matching netlist, standard-cell and macro libraries, SDC, SPEF and corner. Their trace-reset/drain overhead remains included; inter-window transitions are not separately modeled. A duty fraction over1 produces no power mixture. Actual physical support requires timing evidence from the parent. If no idle report is available, supplied-rate power remains null.

All timestamps are scanned without loading the VCD into memory. The duration includes reset, loading, drain and idle if they were dumped. This is not an active-only energy measurement unless the VCD itself is appropriately bounded. The installed `read_vcd` has no documented start/end-window option; unsupported time-window flags are not used. Traces must start at#0 to avoid an unqualified normalization assumption. Timing comes from extracted STA, while the supplied gate activity remains zero-delay without SDF: delay-induced glitches and timing failures are not modeled.

The macro's measured complete-row energy is unknown. W6's partial extracted column/receiver energies are not scaled into a “measured full array” result. Complete-projection power and energy fields remain `null`, even when standard-cell/net-charging estimates are available. Any future independently qualified array-energy addition must establish a disjoint accounting boundary to avoid counting existing standard-cell driver and net-charging energy twice.

## Verification performed

- Read W2b `power.tcl`, `activity_probe.tcl`, API-help log, retained coverage receipt and actual annotation/power report formats.
- Probed the installed OpenSTA2.7 API and inspected relevant Tcl procedure bodies locally.
- `report_units > file` fails in this tool although other report commands accept redirection; the recipe uses tested `sta::redirect_file_begin/end` around `report_units`.
- End-to-end API fixture `api-fixture-output-v5/` passes: synthetic one-inverter netlist, actual GF180 cell library, synthetic SPEF/VCD, four direct pin annotations out of four, parsed Watts and energy. This is explicitly not projection power, speech activity or extracted physical evidence. Its arbitrary25Hz exercised the earlier idle-quiet formula only; that retained historical recipe is superseded by actual-idle mixing below and is not a W8 rate assumption.
- The parser matches W2b's retained1,388/1,253,320 annotation counts and its known native power row.
- Failed API attempts remain in `api-fixture-output*` and `api_probe-first-failure.log`. They exposed missing macro Liberty thresholds (fixed with parent authorization), an unsupported `//` comment in a fixture-only Liberty derivative, unsupported direct redirection for `report_units`, and the excessive highest-instance request trap.
- Corrected macro Liberty parser acceptance is independently recorded in `liberty_parser_check.log`.

No complete W8 projection power, array power, achieved real-time power or gate-level activity coverage is claimed by these scripts or fixtures.

## Escaped flattened names: actual gate-trace probe

The W2b header-only transformation removed child scopes and joined RTL hierarchy with dots, preserving timestamped event bytes. Its2,353 renamed declarations still annotated only1,388/1,253,320 pins; its dotted DUT scope `tb.dut` annotated zero. Those failures do not justify applying that transformer to a gate trace.

A new bounded local test used an actual escaped Verilog cell instance `\engine._cell_ `, the GF180 inverter model, and Verilator5.050 with `--trace --trace-underscore`. The generated VCD has `tb` → `dut` → literal `engine._cell_` scopes with `I` and `ZN` leaf pins. Its first timestamp is#0 despite the testbench `$dumpvars(0,dut)` call. Unmodified VCD and `read_vcd -scope tb/dut` annotate all four reported pins in OpenSTA. See `escaped-api/actual-verilator.vcd` and `escaped-api-output/results.json`. This proves that escaped dotted leaf names can work directly in the installed tools; it does not establish the complete W8 trace's coverage.

For the real mapped gate trace, preserve actual leaf scopes and enable `--trace-underscore` so underscore-prefixed mapped cells/signals are not silently dropped. Do not replace literal dots with hierarchy separators and do not flatten the header without a concrete name-mismatch diagnosis. If coverage is low, retain the raw report and inspect a bounded selection of leaf declarations against the mapped cell names and terminal names; `report_activity_annotation -report_unannotated` can identify missing pins. Correct the actual DUT scope or omitted trace declarations, then rerun the same numerical gate test and annotation. Gate-level SAIF is an alternative supported by the installed tools and W2b's separate single-cell API probe, but its complete-projection mapping would also need measured coverage. Low coverage must remain explicitly reported if neither path is qualified.


## Active and idle traces

The parent gate-trace binary supports `+idle` to run10,000 clock cycles with reset/release and no projection start, and `+vcd=PATH` to select the trace file. Analyze that trace with:

```sh
export W8_WORKLOAD_KIND=idle
export W8_COMPLETED_PROJECTIONS=0
export W8_VCD=/absolute/path/to/idle.vcd
export W8_OUT_DIR=/absolute/path/to/new-idle-corner-directory
python3 /workspace/rv/overnight-20261014/projection-complete/power/run_power.py
```

Its result includes mean power and coverage, while projection energies and rates remain null. Retain the simulation correctness/run receipt separately. The VCD includes reset overhead if the simulator emits from#0, so the resulting idle mean is that entire trace's mean, not an asserted steady-state idle measurement.

For the active trace, set `W8_WORKLOAD_KIND=active`, `W8_COMPLETED_PROJECTIONS=1`, and point `W8_IDLE_RESULT` to the compatible idle report. Supply `W8_RATE_HZ=50` only for the source-backed conditional single-pass/no-replay case in `../protocol/rate-and-energy-review.json`; do not label it a measured general streaming invocation rate. Omit the rate to leave rate-based power unknown. The same mixture can be produced after both runs:

```sh
python3 power/mix_active_idle.py active/results.json idle/results.json --rate-hz 50 --output conditional-50Hz.json
```

The output path must not already exist. The helper verifies identical analysis inputs and uses complete trace-normalized active duration. Array internal/leakage power remains unknown and complete-projection power remains null.

## Original and explicit multicycle timing scenarios

`run_timing.py` drives `postroute_timing.tcl` using the same `W8_LIB_LIST`, `W8_MACRO_LIB`, `W8_NETLIST`, `W8_TOP`, `W8_SDC`, `W8_SPEF`, `W8_CORNER`, optional `W8_STA`, and a fresh `W8_OUT_DIR`. A VCD is unnecessary:

```sh
python3 /workspace/rv/overnight-20261014/projection-complete/power/run_timing.py
```

It first reports the original supplied SDC setup/hold paths, worst slack and TNS. Verify the supplied SDC is the intended single-cycle baseline; the script does not silently discard existing constraints. It then adds ONLY:

```tcl
set_multicycle_path -setup -through [get_pins bank/OUT*] 3
set_multicycle_path -hold  -through [get_pins bank/OUT*] 2
```

and writes separate `macro-multicycle-3-2-*` reports. The pattern defaults to `bank/OUT*`; an empty match is a fatal error. `W8_MACRO_OUTPUT_PATTERN` exists for bounded API tests or an explicitly verified alternate actual instance path. The scope/count and complete input hashes are recorded. The expected integration rationale is PC rising at20ns and capture at80ns under a20ns clock. The macro's44ns PC-to-output proxy and absent independent WL arcs mean neither timing scenario qualifies the full bank. Setup/hold units are preserved in `units.rpt` rather than silently assumed.

Local bounded API verification passes in `idle-timing-api-v2-*`: idle0-projection handling, compatible active/idle mixing, parser extraction, and both timing scenarios. The synthetic one-inverter timing substitute uses `_cell_/ZN` solely to exercise exception APIs; its setup slack moves19.721891→59.721893ns while hold remains0.173211ns. These values are not W8 projection timing. The test script is `test_idle_timing_api.py`. The complete-projection idle, mixed power and timing scenarios remain unexecuted by this worker.

Optional `W8_SKIP_DEFAULT_POWER=1` omits only the pre-VCD `default-power.rpt` calculation. The default remains `0`, which preserves previous behavior. When omitted, JSON `default_power` is null with an explicit `default_power_omission_note`; activity power and annotation reports remain mandatory. The option is recorded in provenance. Original scripts and hashes are preserved in `pre-skip-default-power/`.
