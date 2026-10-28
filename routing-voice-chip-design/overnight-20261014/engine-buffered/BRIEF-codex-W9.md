# Codex brief W9: a routable 1280×320 engine with real-activity power (fix the fanout at synthesis)

AUTHORIZATION: the user lifted the 13 Oct pause on 14 Oct 2026 (`AGENTS.md`) and extended tonight's run to ≈08:10 IST. The lead (Claude) re-checks everything. Never fabricate; preserve failures. Reading ≤10 min: `overnight-20261014/fabric-k64/` (`CONTRACT.md`, `PHYSICAL-NOTES.md`, `COMMANDS.md`, `configs/array_port.json`, `evidence/pre-route-diagnostics.json`).

## Problem (found tonight)
W2b's ARRAY-PORT engine for the approved 1280×320 K64 projection is verified (RTL + gate level), but its P&R runs sit for hours in `RepairDesignPostGPL`.
- Cause: a row-index bit fans out to **4,074** loads and a decode signal to **4,428**.
- LibreLane's `SYNTH_ABC_BUFFERING` defaults to **False**, so these unbuffered nets reach placement.
- An unrepaired version routed, but its activity-annotated power was 8.6 W, inflated by the slow transitions on those nets (`overnight-20261014/power/`).

## Goal
A **repaired, routed, signoff-checked** ARRAY-PORT engine with **activity-annotated power**, in time for the morning (≈07:30 IST). This gives the approved projection's engine area, achieved MHz, and energy per projection.

## Steps
1. Config `configs/array_port_buf.json` (copy of W2b's ARRAY-PORT config):
   - `SYNTH_ABC_BUFFERING: true`, `MAX_FANOUT_CONSTRAINT: 16`, optionally `SYNTH_SIZING: true`;
   - keep CLOCK_PERIOD 20 ns and all repair/CTS/route/DRC/LVS/STA settings;
   - `DRT_THREADS` 12, `STA_THREADS` 4.
   If synthesis-level buffering alone doesn't tame the fanout (check the post-synthesis max fanout), add **RTL register duplication** for the row-index and decode signals: e.g. 10 copies, one per 32-lane group, in a copy of the RTL. Re-run W2b's RTL testbench (`tb/array_port.sv`: all 54 vectors / 17,280 outputs) on any changed RTL.
2. Run the full LibreLane flow **on the cloud pod** (≤12 threads, its own run tag/dir).
3. **Gate-level equivalence + activity:** reuse W2b's mapped-netlist replay and SAIF capture flow (`fabric-k64/` scripts: `verify_gate*.sh`, the mapped-activity scripts, `evidence/array_port-mapped-activity.json`). Run them on the NEW synthesized netlist: all 54 vectors must pass, then capture a SAIF of the same real-activation vector.
4. **Power:** on the routed design, use the flow's extracted SPEF (nom TT 25 °C 3.3 V) + the new SAIF with OpenSTA/OpenROAD `read_saif -scope tb/dut`. Report annotated pins (target ≈100%), internal/switching/leakage/total W, **energy per projection** (power × projection time), and **energy per MAC** (÷ 409,600).
   - Do NOT use LibreLane's `common/io.tcl` helpers outside a step. Plain `read_liberty` / `read_db` / `read_sdc` / `read_spef` works (see `overnight-20261014/power/power_cts.tcl`).
5. Report die/core area, cell area, utilization, worst setup/hold slack per corner, achieved MHz = 1000/(20 − WNS), DRC/LVS/antenna counts, and the power numbers.

## Cloud pod (already running; do NOT create or delete pods; the lead's spend guard terminates it at 08:05 IST)
- `overnight-20261014/runpod/pod-ssh '<cmd>'`, `overnight-20261014/runpod/pod-rsync`.
- On the pod: the repo mirror is `/workspace/rv`, and the Mac's absolute repo path is symlinked to it.
- Nix: `. /nix/var/nix/profiles/default/etc/profile.d/nix.sh; export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash; nix-shell /workspace/rv/tools/librelane/shell.nix --run '…'`.
- Working pod launch script example: `/workspace/rv/overnight-20261014/fabric-k64/run-pod-flow.sh`. Use your own dir `/workspace/rv/overnight-20261014/engine-buffered/`.
- Other jobs (ap40, apnorepair, W8 complete-v3) are running there; don't touch them.

## Rules
- Local workspace (write ONLY here): `overnight-20261014/engine-buffered/`. Keep ≥ 22 GiB free on the Mac. No git.
- Print `W9-STATUS: <result>` after each step. `RESULTS.md` + `results.json` by ≈07:30 IST, even if partial; say which steps completed.
