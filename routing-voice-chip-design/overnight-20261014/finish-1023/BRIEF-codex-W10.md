# Codex brief W10: route the fixed 1280×320 engine to signoff and measure routed power (cloud pod)

AUTHORIZATION: the user resumed the RouteVoice physical goal on 21 Oct 2026 and wants it finished for a release on **Friday 23 Oct**. The lead (Claude) re-checks everything. Never fabricate results, and keep failures on record.

Read first (≤10 min):
- `finish-1023/CONGESTION-DIAG-2026-10-15.md` (D1/D3/D4 results)
- `finish-1023/PAUSED-2026-10-14.md` (what failed and why)
- `engine-buffered/` (W9: `librelane_pi.py` + `synthesize_pi.py` = patched ABC buffering, fanout ≤16; `tb/`, `run-gate.sh`)

## Facts
- `engine-buffered/rtl/engine_local.sv` passes the 54-vector RTL bench cycle-identically. It is W9's engine with per-32-lane-group copies of the partial-product registers.
- At FP_CORE_UTIL 40 / PL_TARGET_DENSITY_PCT 45, with a short global route (3 iterations), it has 260k overflow (92% demand).
- A full global route (50 iterations) made it WORSE: 767k overflow, 99.9% demand. Detailed routing then stalled at ≈570k violations by iteration 7 of 64.
- The post-placement repair (RepairDesignPostGPL) earlier stalled for hours on a multi-driver net, and grew area by +56% on the shared-partials netlist.
- Timing at 150 ns closes post-CTS in all corners.

## Goal (by Thu 22 Oct 20:00 IST)
A **routed, signoff-checked** engine with extracted-parasitic timing and **activity-annotated routed power**: area, MHz, W, energy per projection, pJ/MAC.

## Steps
1. **Short-GRT sweep, run in parallel** (each `--to OpenROAD.GlobalRouting`, GRT_OVERFLOW_ITERS 3, GRT_ALLOW_CONGESTION true, CTS_APPLY_NDR none, CLOCK_PERIOD 150). Base it on `finish-1023/w10-route/cfg_d4.json` (engine_local, ABC buffering, max fanout 16):
   - A: FP_CORE_UTIL 30, PL_TARGET_DENSITY_PCT 35, RUN_POST_GPL_DESIGN_REPAIR true
   - B: FP_CORE_UTIL 35, PL_TARGET_DENSITY_PCT 40, repair true
   - C: FP_CORE_UTIL 30, PL_TARGET_DENSITY_PCT 35, repair false

   Run synthesis ONCE with `librelane_pi.py`, and start the variants from its state (`--from OpenROAD.Floorplan` with a state containing `nl` and `json_h`).
   - If RepairDesignPostGPL in A or B goes over 45 min with no progress line, kill it and record it.
   - Find the multi-driver net, if one exists, from the mapped netlist (e.g. OpenSTA/`report_net`, or a Yosys `check`) and record it.
   - Record per variant: total and per-layer overflow, demand %, wirelength, die area, utilization, and post-CTS TT setup/hold.
2. **Full route of the best variant** (lowest overflow, with repair finished if possible), run to the end of the LibreLane flow: DRT, RCX/SPEF, multi-corner STA, Magic/KLayout DRC, LVS, antenna.
   - Use a SHORT global route (GRT_OVERFLOW_ITERS 3–10). Do NOT let it run 50 iterations again.
   - DRT_THREADS = 12.
   - If detailed-routing violations are not falling well (target < 10k by iteration 20), stop and report.
3. **Gate-level activity on the NEW mapped netlist.** The old SAIF does NOT match these instance names.
   - Use W9's `run-gate.sh` / `tb/activity_array_port.sv` flow, adapted to this netlist: one real-activation projection.
   - Also replay the full 54-vector gate-level bench on the mapped netlist (the sharded flow is fine).
4. **Routed power.** Final ODB + nom SPEF + signoff SDC + the new SAIF (`read_saif -scope tb/dut`), using plain OpenROAD/OpenSTA (`finish-1023/w10-route/power_routed.tcl` is a template).
   - Note: the SAIF is captured at the bench's clock. Use `scale_saif.py` to stretch its time base to 150 ns if the bench period differs, so that toggles per cycle are preserved.
   - Report annotation coverage, internal/switching/leakage/total W, energy per projection (W × 4,163 × 150 ns), and pJ/MAC (÷ 409,600).

## Cloud pod (already created; do NOT create or delete pods; the lead's guard stops it at the $28 cap / Fri 18:00)
- `overnight-20261014/runpod/pod-ssh '<cmd>'` and `overnight-20261014/runpod/pod-rsync` (16 vCPU, 755 GB RAM).
- The repo subset is at `/workspace/rv`, and the Mac path `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design` is symlinked to it, so configs with Mac absolute paths work there.
- Nix: `. /nix/var/nix/profiles/default/etc/profile.d/nix.sh; export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash; nix-shell /workspace/rv/tools/librelane/shell.nix --run '…'`.
  - Setup may still be finishing: wait for `SETUP-DONE` in `/workspace/setup.log`.
- PDK root: `/workspace/rv/overnight-20261014/fabric-k64/pdks`.
- Run directory: `/workspace/rv/overnight-20261014/finish-1023/w10-route/runs/`. W12 also uses this pod, so keep your total threads at ≤12.

## Rules
- Write ONLY in `finish-1023/w10-route/` (Mac) and its pod mirror. Copy reports (not huge DBs) back to the Mac as you go.
- No git. Keep ≥22 GiB free on the Mac.
- Print `W10-STATUS: <result>` after each step.
- Write `RESULTS.md` + `results.json` by Thu 22 Oct 20:00 IST, even if partial, saying which steps completed.
