# Gate activity audit

The monitor waits for the existing speech gate simulation to exit zero and report exactly 320 matching outputs for vector 0. It then runs the unchanged binary with `+idle`, `+vcd=.../evidence/gate-idle.vcd`, and one-CPU affinity. The idle run is bounded to 600 seconds and stops its own process group if free remote storage drops below 9 GiB, providing a margin above the required 8 GiB floor. Other jobs are untouched.

`monitor_and_idle.py` is the recorded implementation. Its remote working directory is `/workspace/rv/overnight-20261014/projection-complete`. Runtime logs and JSON receipts stay under `gate-activity-audit/`; speech and idle simulation logs and exit receipts stay under `logs/`. Raw VCDs stay under `evidence/` on the pod.

Completion requires an actual `speech-correctness.json`, `idle-execution.json`, two VCD metadata receipts, and `results.json`. The monitor being alive is not completion. No power, annotation coverage, or projection energy is established by this task.

VCD receipts preserve actual header scope and pin references, timestamp interval, file size, SHA-256, and a file stability check. The suggested STA scope `tb/dut` must still be tested on the complete physical design. No VCD name rewriting is performed. `metadata-parser-fixture.json` tests the parser against a tiny local escaped-instance fixture and is not projection evidence.

Both workloads use zero-delay mapped synthesis gates and a behavioral hard-array model; no SDF delays or routed glitches are simulated. The idle workload has 10,000 clocks, reset/release, and no projection start. Array internal energy remains uncharacterized. The selected mapped-netlist hash and unchanged-binary hashes are included in actual completion receipts.

The later authorized `run_annotation_only.py` uses the TT cell library, current macro proxy, matching mapped netlist, and unmodified `tb/dut` scope for both traces. It creates a 20 ns clock on `clk` because native activity reporting requires a clock; it reads neither SDC nor SPEF and requests no power or timing report. Both subprocesses share a 600-second budget and one-CPU affinity. The exact Tcl and wrapper are frozen into each output directory. The failed no-clock API fixture is preserved; the corrected escaped-instance fixture gives 4/4 directly VCD-annotated pins and is not projection evidence.
