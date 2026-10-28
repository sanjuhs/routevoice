# Lead local retry of the 12 W12 units that failed on the pod (22 Oct 2026)

**Why they failed:** W12's pod per-module run capped each Yosys process at 6 GiB of address space. 12 generic units (and therefore their 12 GF180 steps) and 6 ECP5 units aborted with `std::bad_alloc` (exit −6).

**Source:** their exact per-unit inputs (`input.il`, `generic.ys`, `gf180.ys`, `fpga.ys`) were restored from the checksum-verified Hugging Face pod backup. The only change was rewriting the PDK path from `/workspace/rv` to the local repo. They were re-run on the Mac (LibreLane Nix shell Yosys) **without the cap**.

**Result:** all 30 jobs pass; peak RSS 29.2 GiB (ECP5).

**Merge:** the original pod attempts are archived per unit under `attempts/pod-6GiB-cap`. W12's own `per_module_report.py` regenerated `RESULTS.md`/`results.json`: generic, GF180 and ECP5 are each 4,457/4,457 pass, and the status is **complete**.

The previous pod-only report is kept as `../RESULTS-pod-20261021.md`. The full merged per-module tree is at `/Volumes/Extreme Pro Dev/routevoice-checkpoints/overnight-20261014/w12-merged/`.
