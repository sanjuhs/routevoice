# Exact local commands

Run from the repository root unless stated otherwise. The corrected launchers confine outputs to this workspace; the initial Nix temporary-path exception is recorded below. Use Python `PYTHONDONTWRITEBYTECODE=1`, thread cap and workspace TMPDIR in the launch scripts.

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python overnight-20261014/fabric-k64/prepare.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/pin_configs.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python overnight-20261014/fabric-k64/audit_rtl_constants.py
bash overnight-20261014/fabric-k64/verify.sh array_port full
bash overnight-20261014/fabric-k64/verify.sh sc_rom full
bash overnight-20261014/fabric-k64/verify.sh array_port trace
bash overnight-20261014/fabric-k64/verify.sh sc_rom trace
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python overnight-20261014/fabric-k64/finalize_checks.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/supervise.py array_port v2
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/supervise.py sc_rom v2
```

The original full simulation logs are `evidence/*-full-simulation.log`; the initial trace regeneration is recorded in `logs/trace-*.log`. The corrected reusable verifier labels future logs by full/trace mode. The first full checker attempted `$dumpoff`, but Verilator still emitted the full suite; oversized regenerable traces were removed with gzip hashes retained in `evidence/trace-replacement.json`. Dedicated one-vector traces are the actual power inputs.

`prepare.py` reads original repository model/manifest/saved evidence, hashes and validates them, and emits frozen RTL and vectors. The existing delivered RTL/vectors are sufficient for simulation and physical reproduction without the full model file. `relocate.py` rebases absolute config and checker paths after copying the workspace. Preserve the old source hashes before relocation; paths are the only intended differences.

`run_flow.sh` uses the same pinned `tools/librelane/shell.nix` as `scripts/run_physical.sh`, but explicitly sets workspace PDK, temporary/cache/run directories and manual-PDK mode to avoid writes outside this worker's scope. Both variants are nice 10, three threads each, maximum six concurrent. Synthesis/flow commands and executable paths are retained by LibreLane within each run directory.

The first EDA attempt (`*-v1`) was stopped after approximately ten minutes when Nix was observed resetting TMPDIR, placing an ABC temporary directory under `/tmp`. The corrected launcher sets TMPDIR inside Nix `--run`, preserves v1 logs, runs `*-v2`, and charges v1 elapsed time to the original limits. Console output is condensed; native tool step logs remain complete. No v1 pass credit.

SC-ROM v2 was stopped on the runtime forecast required by the brief; see `CLOUD-REQUEST.md`. ARRAY-PORT continues under its independent disk/runtime guard.

Mapped-netlist replay (one compile thread):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/make_gate_tb.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/gate_guard.py
```

`gate_guard.py` pauses its own child group when the two physical flows plus gate compilation would exceed six worker threads. The replay is against the synthesis netlist until explicitly rerun with the final routed netlist.

The delivered full benches were rerun after removing full-suite trace instrumentation; both passed. `evidence/source-hashes-initial.json` retains the earlier manifest; `evidence/testbench-manifest-refresh.json` explains the two testbench-only changes. Exact rerun and numerical-bound commands:

```sh
W2B_SIM_JOBS=1 bash overnight-20261014/fabric-k64/verify.sh array_port full
W2B_SIM_JOBS=1 bash overnight-20261014/fabric-k64/verify.sh sc_rom full
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python overnight-20261014/fabric-k64/finalize_checks.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python overnight-20261014/fabric-k64/audit_numeric_bounds.py
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/fabric-k64/gate_guard_sc.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/collect_gate.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/collect_results.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/seal_artifacts.py
```

A first rerun launcher exposed Bash 3's empty-array behavior with `set -u`; that launcher error was fixed before either rerun executed. Full-mode simulation no longer enables tracing. The dedicated trace mode remains unchanged.

The initial ARRAY-PORT gate monitor encountered a transient JSON read race and exited while its simulation continued. `recover_gate_guard.py array_port` adopted the existing process without restarting it. Its normal-completion check requires PASS, `$finish`, and Verilator statistics; the adopted process OS exit status remains unavailable and is recorded as such. The old exception and recovery receipt are preserved in `evidence/array_port-gate-monitor-*`. Future gate monitors conservatively retry incomplete physical status through the next poll.

Activity annotation probe (pre-route, no power values):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/flatten_vcd_names.py array_port
bash overnight-20261014/fabric-k64/run_activity_probe.sh > overnight-20261014/fabric-k64/logs/activity-probe.log 2>&1
```

The current probe uses the placed step-28 netlist/SDC and header-flattened trace. Its coverage was identical to the original trace with corrected slash scope. Restore the step-28 netlist from its `.gz` if later archived. Trace event bytes are verified unchanged. Earlier dot-scope and hierarchical-probe logs are retained separately.

Completed gate build intermediates may be stored in `evidence/<variant>-gate-build.tar.gz`, with per-file SHA-256 in the adjacent JSON. The passing `gate-<variant>/sim` executable stays available. Extract the archive into its gate build directory if the old compiler outputs are needed.

The SC mapped gate replay window was extended from the worker’s default one hour to 90 minutes after observing the ARRAY replay cost and SC compile duration. This does not extend the stopped SC physical run. `extend_sc_gate_window.py` is the PID-bound one-off controller that keeps the original parent available to collect the child’s exit status; its receipt is `evidence/sc_rom-gate-window-extension.json`. Future `gate_guard_sc.py` runs use the 90-minute limit directly. Disk protection remains 21 GiB.

Disk-preserving archival commands used only on this workspace:

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/fabric-k64/archive_synthesis.py
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/fabric-k64/archive_gate_build.py array_port
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/fabric-k64/archive_gate_build.py sc_rom --completed-compile
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/fabric-k64/archive_old_sta.py
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/fabric-k64/compress_retained_sdf.py
```

These are historical archival commands, not prerequisites to rerunning verification. Each preserves full data with hashes; build archives keep the simulation executable in place. The SC compiler output was archived while its completed executable continued running. Some archival commands intentionally reject overwriting an existing archive.

The currently running/delivered gate binaries were compiled with the original `verify_gate.sh`, preserved at `evidence/verify_gate-original.sh`. The reusable launcher now adds Verilator’s supported `--autoflush` option so future per-vector progress is recorded immediately. This changes logging only; no existing binary was restarted or credited with new results. The exact native option help was checked: “Flush streams after all $displays”.

After both full mapped regressions passed, a compact gate-SAIF path was verified with a standalone API probe (four pins annotated out of four, not projection evidence). Complete-projection activity run commands:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/make_gate_activity_tb.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/activity_guard.py array_port
```

The activity run uses the full mapped netlist, checks vector0’s320 outputs/4163cycles, and requests `--trace-saif --trace-underscore --trace-depth 2`. It has two compiler threads, one simulation thread, a22GiB disk stop and one-hour activity-only runtime guard. No activity coverage or power pass is implied until actual projection reports are collected. `power.tcl` supports either W2B_SAIF or W2B_VCD and prints units to its retained invocation log (this OpenSTA command rejects report_units redirection arguments).

A six-hour ARRAY monitoring extension was prepared, then withdrawn before its trigger during final contract review. The approved proposal states a four-hour ceiling for the first bounded physical trial. The original 14,400-second cumulative supervisor remains active and was never paused by this controller; `evidence/array_port-window-extension.json` records the correction. The historical controller is disabled. SC physical remains stopped under its separate forecast rule.

Complete ARRAY mapped SAIF collection and placement coverage check:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 .venv/bin/python overnight-20261014/fabric-k64/collect_activity.py array_port
W2B_DIR="$PWD/overnight-20261014/fabric-k64" TMPDIR="$PWD/overnight-20261014/fabric-k64/tmp" OMP_NUM_THREADS=1 nice -n 10 /nix/store/sc7lam0v6gsfzzcn993qcnkdzkzvnsk9-opensta/bin/sta -exit overnight-20261014/fabric-k64/saif_projection_probe.tcl > overnight-20261014/fabric-k64/logs/saif-projection-probe-success.log 2>&1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/fabric-k64/activity_guard.py sc_rom
```

The first coverage command annotated every pin but then rejected unsupported report_units redirection. Its error log is retained. The corrected command prints units to stdout and completed without errors. A mistyped Nix store path in a retry returned127 before executing OpenSTA; that log is also retained. Neither error receives pass credit. The actual successful projection annotation is1,253,320 SAIF pins /0 unannotated at step28. Recheck against the eventual routed netlist because repair/CTS can create new cells.

The additional SC-ROM mapped-SAIF build stopped after934.2s when free space reached21.994GiB, below its22GiB safety guard. It produced no executable simulation pass or complete trace. `archive_stopped_activity.py` preserves all generated partial compiler files in a verified lossless archive; no retry was launched. The reusable activity launcher now accepts an optional netlist path (default unchanged) for lead-operated reproduction after cloud synthesis.

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n10 .venv/bin/python overnight-20261014/fabric-k64/compress_completed_activity.py
PYTHONDONTWRITEBYTECODE=1 nice -n10 .venv/bin/python overnight-20261014/fabric-k64/archive_stopped_activity.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/collect_diagnostics.py
```

A final hash-only integrity check confirmed all 39 entries in `evidence/source-hashes.json` remain unchanged after the functional tests; see `evidence/tested-source-integrity.json`. Completed RTL/gate simulator executables were also transparently APFS-compressed in place with per-file byte hashes in `evidence/transparent-completed-binaries.json`; no executable was running during that operation.

`ARRAY-CONTINUATION.md` contains a checked CLI recipe for a later bounded phase, not an executed retry. `evidence/array_port-checkpoint31-manifest.json` verifies all 11 ordinary paths referenced by the latest completed state. The in-memory unfinished repair work has no saved database and cannot receive completed-stage credit.

Final bounded result commands, executed only after the physical guard stopped:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/save_stop_receipt.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/collect_results.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/fabric-k64/write_bounded_report.py
PYTHONDONTWRITEBYTECODE=1 nice -n10 .venv/bin/python overnight-20261014/fabric-k64/seal_artifacts.py
```

ARRAY stopped at 14,401.928 cumulative seconds under the 14,400 s guard (two-second polling), return −15 from the terminated physical process group; the monitor itself completed normally. No live members remained in the flow process group. The last completed state is 31-openroad-stamidpnr; step32 has no state_out or saved repaired database. `evidence/final-delivery.json` binds the final report, results, handoffs, placement PNG and manifests.
