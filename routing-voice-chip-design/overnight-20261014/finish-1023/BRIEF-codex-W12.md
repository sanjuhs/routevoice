# Codex brief W12: full-recognizer synthesizability (chip + FPGA view) on the big-RAM pod

AUTHORIZATION: the user resumed RouteVoice on 21 Oct 2026 for a release on **Friday 23 Oct**. The lead (Claude) re-checks everything. Never fabricate results, and keep failures on record.

Read first (≤10 min):
- `../OVERNIGHT-PROGRESS.md` (search "Full-top Yosys")
- `overnight-20261014/synth/` (earlier attempts and a patched copy)
- `onchip-all/RESULTS-v2.md` and `commands-v2.json` (the RTL file list of the all-on-chip top `rv_allonchip_top_all_v2.sv`)
- `storage-inventory/INVENTORY.md`

## Problem
The whole recognizer has never been synthesized. Earlier attempts stopped on strict SystemVerilog ordering (slang: use-before-declare, plus a localparam declared after use; patched copy in `synth/patched/`). One then reached ≈90 GB of RAM on the Mac, because the 28.6 MB of weight ROMs (`$readmemh`) were being synthesized as logic.

## Goal (by Thu 22 Oct 18:00 IST)
A **complete synthesizability result** for `rv_allonchip_top_all_v2`. On a real chip the weight ROMs are the Taalas array / ROM macros, and on an FPGA they are BRAM, so treat them that way:
1. **Find every weight/coefficient ROM** module or memory, and make them **black boxes** with the same ports. Do this with a Yosys `blackbox` attribute or a stub file, not by editing the originals; keep stubs in your folder.
2. **Generic Yosys synthesis** (`synth -top rv_allonchip_top_all_v2`, slang frontend as the earlier attempts used, `--allow-use-before-declare` or the patched copy). Report:
   - pass/fail;
   - every unsupported construct with file:line;
   - cell counts by type;
   - flip-flop count, memory bits inferred (excluding the black boxes);
   - peak RAM and wall time.
3. **GF180 standard-cell mapping** (LibreLane `Yosys.Synthesis` step only, or `abc -liberty` with the GF180 7-track TT lib): logic cell area in mm², excluding the black-box macros. Compare it with the floorplan's assumed logic areas (`floorplan/RESULTS.md`, Final design point).
4. **FPGA view.** `synth_xilinx` (or `synth_ecp5` / `synth_ice40` if xilinx is missing), with the ROMs as BRAM-sized black boxes.
   - Report LUT/FF/DSP counts and the BRAM bits needed for the 28.6 MB of weights; for comparison, also the bits needed as 4-bit index + codebook.
   - Say which FPGA classes could hold it.

## Cloud pod (shared with W10; do NOT create or delete pods; the lead's guard stops it at the $28 cap / Fri 18:00)
- `overnight-20261014/runpod/pod-ssh`, `pod-rsync` (16 vCPU, **755 GB RAM**). Repo subset at `/workspace/rv`; the Mac path is symlinked to it. Upload whatever RTL you need with `pod-rsync -az --relative <paths> pod:/workspace/rv/`.
- Nix + LibreLane shell (it includes yosys + slang): `. /nix/var/nix/profiles/default/etc/profile.d/nix.sh; export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash; nix-shell /workspace/rv/tools/librelane/shell.nix --run '…'`. Wait for `SETUP-DONE` in `/workspace/setup.log`.
- Use ≤4 threads; W10 uses the rest.

## Rules
- Write ONLY in `finish-1023/w12-synth/` (Mac) and its pod mirror. No git. Keep ≥22 GiB free on the Mac.
- Print `W12-STATUS: <result>` after each step.
- Write `RESULTS.md` + `results.json` by Thu 22 Oct 18:00 IST, even if partial.
