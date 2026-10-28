# Codex brief W8: the complete GF180 projection (engine + real Taalas array, placed and routed together)

AUTHORIZATION: the user lifted the 13 Oct pause on 14 Oct 2026 (`AGENTS.md`), approved `docs/ROUTEVOICE-PROPOSED-PHYSICAL-GOAL-2026-10-13.md` (read its "First bounded experiment" and "Required result" sections; this is that deliverable), and extended tonight's run to ≈08:10 IST. The lead (Claude) re-checks everything. Never fabricate; preserve failures. Reading ≤10 min: `skills/taalas-fixed-weight-routing/SKILL.md`, then the files below.

## Inputs (read-only)
- **Engine:** W2b's ARRAY-PORT variant of the approved 1280×320 K64 projection, `overnight-20261014/fabric-k64/`:
  - RTL `rtl/rv_k64_array_port.sv`, `rtl/engine.sv`, `rtl/metadata.sv`, `rtl/taalas_*.sv`, `hf/`; contract `CONTRACT.md`;
  - verified RTL and gate-level testbenches `tb/array_port.sv`; LibreLane config `configs/array_port.json`;
  - the engine requests one 1,280-bit index row about every 3 cycles.
- **Taalas array:** W6's pitch-matched readable-cell bank, `overnight-20261014/taalas-pitch/`:
  - `r1280-v2/bank.gds`, top `PITCH_BANK_R1280`, 1,004 × 2,258.81 µm, all 409,600 real selections;
  - DRC 0 (lead-verified), bit readback 0 mismatches;
  - SS read passes at 60 ns reuse; fails at a 20 ns capture;
  - see its `RESULTS.md` / `results.json` for the pin/port list, wordline count, and which periphery (decoders/drivers) is or isn't inside.
- W5's periphery components (row decoder, bank decoder, latch128; GDS/LEF/netlists): `overnight-20261014/taalas-array/periphery/handoff-v2/`, `handoff-latch128/`.

## Goal
One placed-and-routed GF180 block = engine + row decoder/drivers + W6 array as a **hard macro** + output latches. Measure the complete projection's routed area, timing and power: what the approved proposal requires.

## Stages (deliver each; stop at the last one that works and report honestly)
1. **Macro views for W6's bank:**
   - LEF abstract with real pin shapes taken from the GDS (row/wordline inputs, the 1,280 readout outputs, precharge/phase controls, VDD/VSS on a top metal for PDN hookup) and obstructions; generate with Magic `lef write` or KLayout.
   - Black-box Verilog stub; Liberty timing model (create a simple `.lib` with the measured 60 ns reuse / SS settling as setup/clock-to-out, clearly labelled as derived from W6's SPICE).
   - Check the LEF pins against the GDS labels programmatically.
2. **Integration RTL:** a top `rv_k64_projection_complete` containing the ARRAY-PORT engine, a row decoder/driver for the bank's wordlines (std cells or W5's decoder), phase/precharge control matching W6's measured protocol (60 ns per row; the engine's ≈3-cycle row cadence at a 20 ns clock), output latches into the engine's index port, and the macro instance.
   - Simulate it with a behavioral model of the bank that reads the REAL indices (from W6's `indices.npy` / generators) and returns rows with the measured latency.
   - Re-run W2b's testbench vectors: all 54 vectors / 17,280 outputs must still match.
3. **Physical (on the 32-core cloud pod):** LibreLane with the macro (`MACROS` config: gds/lef/nl/lib), manual macro placement, PDN connecting the macro's power pins, then placement/CTS/routing. Use settings that finish:
   - CLOCK_PERIOD 20 ns with post-GPL/GRT design repair disabled (the lead found repair takes hours on this engine);
   - or 40 ns with repair enabled.
   Report routed die area, macro vs logic area, worst setup/hold slack per corner, achieved MHz, DRC/LVS/antenna counts, and power.
4. **Power with real activity:** generate a **gate-level** VCD from the mapped/routed netlist simulation of one real-activation vector. W2b found that RTL VCDs annotate only 0.11% of netlist pins. Annotate the post-route design (OpenSTA `read_vcd` / `report_power`), add the array's measured read energy from W5/W6 × reads per projection, and report energy per projection and power at the real-time rate.

## Cloud pod (already running; do NOT create or delete pods; the lead's spend guard terminates it at 08:05)
- SSH wrapper: `overnight-20261014/runpod/pod-ssh '<cmd>'`; rsync wrapper: `overnight-20261014/runpod/pod-rsync <src> pod:/workspace/...`.
- On the pod: repo mirror at `/workspace/rv` (`/Users/sanju/…/routing-voice-chip-design` is symlinked to it, so absolute paths in configs work). Nix + LibreLane are installed: `. /nix/var/nix/profiles/default/etc/profile.d/nix.sh; export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash; nix-shell /workspace/rv/tools/librelane/shell.nix --run '…'`. PDK at `/workspace/rv/pdks/gf180mcuD`.
- See `overnight-20261014/fabric-k64/run-pod-*.sh` for the lead's working pod launch scripts. Other LibreLane jobs are running there: use ≤ 12 threads and your own run directory `/workspace/rv/overnight-20261014/projection-complete/`.

## Rules
- Local workspace (write ONLY here): `overnight-20261014/projection-complete/`. Keep ≥ 22 GiB free on the Mac. No git.
- Print `W8-STATUS: <result>` after each stage. Write `RESULTS.md` + `results.json` by ≈07:40 IST, even if partial: say exactly which stage completed and which numbers are measured vs derived. Copy pod results back to the local workspace (small files: reports, logs, final DEF/GDS if < 200 MB, PNG render).
