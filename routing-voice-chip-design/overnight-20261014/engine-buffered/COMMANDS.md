# W9 reproduction

Run from the repository root. Local changes are confined to this directory. Use the existing pod wrappers; do not create/delete pods.

Current physical launch on the pod: `bash /workspace/rv/overnight-20261014/engine-buffered/run-flow-v3.sh`. This loads the pinned LibreLane shell, invokes `librelane_pi.py`, uses the completed v1 JSON-header checkpoint, then executes the normal full Classic flow from synthesis. `synthesize_pi.py` delegates to the installed pinned synthesis script and adds only `-p` to ABC's generated buffering command. Check the actual `AREA_0.abc` in the run.

Mapped replay and one-vector SAIF capture: `watch-gate-v3.sh`, which waits for completed synthesis and runs `run-gate.sh full <new-netlist>` then `run-gate.sh activity <same-new-netlist>`. The library hold guards apply only after rejecting a netlist containing a hold instance. All vectors and expected outputs are unmodified copies; testbench changes are path relocation only.

The compiler uses two jobs and `--output-groups 0` to keep the default split C++ files separate, avoiding two enormous aggregated compilation units. The pinned executable advertises the flag in `logs/verilator-help.txt`; the exact [Verilator 5.044 documentation](https://github.com/verilator/verilator/blob/v5.044/docs/guide/exe_verilator.rst#output-groups-numfiles) documents zero as disabling grouping. This is a build partition choice, not changed stimulus or HDL.

`run-finish.sh` periodically collects partial results, waits for the actual flow exit and completed activity trace, runs `run-power.py`/`power.tcl` on extracted nominal SPEF and TT Liberty, and invokes the supplemental KLayout deck if a completed GDS exists. `power.tcl` is standalone and does not source flow io helpers.

Before the pod cutoff, run `python3 archive.py` after final collection and copy the archive plus its SHA-256 receipt only if the Mac remains at least 22 GiB free. All large execution artifacts remain remote during computation.

## buf-v4
Run `bash run-flow-v4.sh`; full modified-RTL regression `nix-shell /workspace/rv/tools/librelane/shell.nix --run "bash /workspace/rv/overnight-20261014/engine-buffered/run-rtl.sh"`; mapped replay/activity `bash watch-gate-v4.sh`; collection/power/signoff `bash run-finish.sh`. Only v4 uses rtl/engine_dup.sv. Its RTL testbench is the W2b original plus equality assertions for ten row copies.

## Parallel gate replay
`bash run-shards.sh` builds the same mapped netlist with a parameterized vector-range copy of the gate testbench. Eight processes cover disjoint ranges totaling 54 vectors. Each repeats all four abort tests. Seeds are derived from W2b serial cycle counts to retain the original stall sequences; the aggregator requires every vector and exact reference cycle count. The original serial full replay runs independently. Activity waits for verified all-54 pass from either replay; results distinguish them.
