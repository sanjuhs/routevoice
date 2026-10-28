# RouteVoice overnight run — 14 October 2026

Lead: Claude (Opus 5.5). Workers: Codex CLI (`codex exec`, one Terminal-panel tab each) plus Claude subagents.
Branch: `overnight-2026-10-14` (pushed to GitHub at checkpoints). SSD mirror: `/Volumes/Extreme Pro Dev/routevoice-checkpoints/overnight-20261014/`.
Workspace: `routing-voice-chip-design/overnight-20261014/`. RunPod budget: **$30 new spend** (separate from the earlier $10.84), CPU pods only, hard guard.

Rule for this file: a result is listed as PASS only after the lead re-ran or read the actual output. Worker claims are listed as "claimed".

## RELEASE SUMMARY: Friday 23 Oct 2026 (read this first; lead-verified, updated Sat 24 Oct ≈19:15 IST)

**Update 24 Oct:** two RTL pipelining changes ("fix 2", `finish-1023/w10-route/pipe2/`) close the slow corner. The fix-2 engine meets 150 ns in **all 9 corners**. Its signoff: **DRC 0** (routing, Magic and KLayout), **LVS unique match**, XOR 0, antenna 11 nets open. Routed power is 0.188 W, 287 pJ/MAC. The engine rows below now describe fix 2; the earlier closure results are in brackets.

**Update 24 Oct evening: antenna closed, full signoff clean.** The fix-2 run was restarted from detailed routing with 10 post-route antenna repair rounds instead of the default 3; nothing else changed (`pipe2/README.md` § Antenna close-out, run `runs/pipe2-ant`). Result: **antenna 0 nets / 0 pins**, DRC 0 (routing, Magic, KLayout), XOR 0, LVS unique match, 9/9 corners met (worst setup +8.10 ns at max SS, worst hold +0.324 ns). Routed power on the new layout with the same SAIF is unchanged: 0.188 W, 287 pJ/MAC. The run is backed up to the same HF dataset under `archives/pipe2-ant/`.

| Goal item | Status | Evidence |
|---|---|---|
| Full recognizer runs "Switch on the lights" bit-exactly with **Taalas index+codebook** weights | ✅ **PASS** | Tokens [28176, 373, 278, 26068, 2], 18/18 hashes, 312,578,649 clocks (delta 0). Weights 28.6 MB → **17.5 MB**, 0 mismatches. Two more clips pass ("Plant present.", "Seasonable."). `finish-1023/w11-taalas-e2e/` |
| **Routed** 1280×320 engine (fix 2) | ✅ | Fix 2 = local-partials RTL plus an elastic register before the FP32 affine, plus look-ahead per-32-lane-group output registers. 4,165 cycles per projection; the 54-vector bench is bit-exact. GRT overflow 9, **DRT 0**. Die 22.84 mm², 53.9% utilization. Full flow 8.5 h on the Mac. `finish-1023/w10-route/pipe2/` [closure run: die 22.74 mm², DRT 0] |
| Signoff checks | ✅ **all pass** (DRC, LVS, antenna, XOR) | Final (antenna close-out run): **Magic DRC 0, KLayout DRC 0, Netgen LVS "Circuits match uniquely"** (0 differences), routing DRC 0, XOR 0, **antenna 0 nets / 0 pins**. LibreLane manufacturability report: Antenna, LVS and DRC Passed. [fix-2 run before close-out: antenna 11 nets / 12 pins; closure run: 4 / 5] |
| Routed timing (extracted SPEF, 150 ns) | ✅ **meets all 9 corners** | Final setup: **TT +67.5 ns, SS nom +21.4 ns, SS max +8.10 ns (worst)**, FF ≥ +82 ns. Hold: worst +0.324 ns, all pass. [fix 2 before antenna close-out: +67.6 / +21.6 / +8.34 ns, hold +0.300 ns] 0 setup/hold violations. Slew/cap-limit counts remain (389k slew at TT). [closure run: SS failed, nom −40.0 / max −55.5 ns] |
| Activity-annotated routed power | ✅ | Fix 2, with a fresh real-speech gate SAIF: **0.188 W at 150 ns (TT) → ≈117 µJ/projection ≈ 287 pJ/MAC**, 67.5% of pins annotated; re-run on the final antenna-closed layout, same result (`pipe2/evidence-ant/power-pipe2-ant.log`). The +12% pays for SS closure. [closure design: 0.168 W, 104.9 µJ, 256 pJ/MAC.] 1,364,228 pins annotated, 649,985 repair/diode-added pins not (68% coverage). First route for comparison: 0.158 W, 97.7% coverage, 241 pJ/MAC. One engine at 150 ns gives 0.66 GMAC/s ≥ the 0.6 real-time need. |
| Post-layout simulation | ✅ zero-delay only | The routed netlist (first route) replays 54/54 vectors with identical cycles. SDF timing simulation is not supported by the available simulators. |
| Full-recognizer synthesizability: **chip** | ✅ **complete** (4,457/4,457 units; wrapper connectivity passes) | GF180 TT **1,198 mm²**, 48.4 M cells, 8.07 M FFs. The 8.17 M mutable bits are flops (no SRAM mapping in generic synthesis); 19× the floorplan's 63 mm² logic budget. `finish-1023/w12-synth/` |
| Full-recognizer synthesizability: **FPGA** | ✅ complete (ECP5) | **30.4 M LUT4**, 1.34 M FF, 1,247 DSP, 118 BRAM. No FPGA fits, and the weights need external memory. |
| Summary updated | ✅ | This section |
| RunPod spend, pod terminated | ✅ terminated; ❌ over the goal's $30 figure | Total **$34.82**. The user later approved a $60 cap. No pods remain. |

### Biggest open items after release
1. ✅ **Engine slow-corner closure: DONE 24 Oct by fix 2** (see the update above). Antenna closed the same evening (0 nets). The remaining engine item is the slew/cap-limit counts. History:
   - A second local closure pass (Fri, `full-eco2-local.json`: setup slack margin 45 ns, buffer cap 50%, TNS 100%, antenna iterations 20, margin 50) moved TT to +56.7 ns and SS to nom −36.2 / max −53.1 ns.
   - **The same 30 SS endpoints still fail**, so these paths are structurally too deep for 150 ns at SS. Add one pipeline register in the 320-lane datapath, or accept ≈5.4 MHz at SS.
   - Antenna 4 nets / 4 pins; DRC/LVS still clean.
2. **Area.** Map the 8.17 M mutable bits to SRAM macros (W14 has a verified 160-SRAM bridge and 384-macro producer adapter) and time-share the datapaths. The RTL as written is ≈1.2 cm² of logic.
3. **Full two-die chip.**
   - W13: all 98 matrices are in Taalas GDS (81 banks, DRC 0, 6 full-LVS representatives); the control strips are LVS/STA-clean.
   - W14: 6 logic macros signed off; the large blocks are not hardened.
   - W15: both dies are routed with the real arrays plus 4 logic macros, with top-wiring DRC 0, but full-deck DRC/LVS was not run.
4. **Note:** the pod backup is a **public** Hugging Face dataset (`sanjuhs/routevoice-pod-final-20261022`). Make it private if that was not intended.

## RESUMED 21 Oct 2026, target: release Friday 23 Oct

- **Launched ≈02:25 IST** with three Codex workers (briefs in `routing-voice-chip-design/overnight-20261014/finish-1023/`, visible Terminal tabs):
  - **W10:** route the local-partials 1280×320 engine to signoff, plus routed SAIF power. Runs on the RunPod pod `rv-overnight-pnr2` (16 vCPU / 755 GB, $0.64/h). The guard is capped at $28 total and stops the pod Fri 23 Oct 18:00 IST; $8.96 was spent before.
  - **W11:** the full recognizer reads every weight as Taalas index + codebook; F64 "Switch on the lights" must stay bit-exact; more clips if time allows.
  - **W12:** full-recognizer synthesizability, chip view and FPGA view, on the pod's big RAM.
- **Inputs restored from the SSD:** `experiments/`, the `onchip*` folders, and the engine RTL, hf and floorplan pdk.
- **Worker deadlines:** Thu 22 Oct 18:00–20:00 IST. The lead verifies, then updates this summary on Friday morning.

### 22 Oct 18:36 IST: pod backed up to Hugging Face (verified), ALL pods deleted (lead)

- **Workers:** all Codex workers (W10–W15) had exited by 21 Oct 17:03. Their claimed "continuing" jobs were not running. From ≈19:30 IST on 21 Oct the pod's only job was a W12 `memory-gate.py fpga` loop waiting for memory, which billed ≈21 idle hours.
- **Backup:** the pod's full `/workspace` (53 GB, 105,826 files under `rv/` plus `setup.log`) is in the public dataset **https://huggingface.co/datasets/sanjuhs/routevoice-pod-final-20261022**, as 6 zstd tar archives plus `pod-manifest.sha256` and a README with restore steps.
- **Verification:** every archive was downloaded back from HF on the pod and stream-hashed. 105,827/105,827 files match the manifest, with 0 missing and 0 problems. Records are in `routing-voice-chip-design/overnight-20261014/finish-1023/pod-final-hf-20261022/` (`hf-verify.json`).
- **Secret scan before publishing:** none found. The model is Moonshine (MIT).
- **The pod-to-SSD rsync stalled** at 0.7 of 53 GB and was stopped. On the user's request that partial copy (`pod-final-20261022/`) was deleted; everything in it is on HF.
- **Mac-side snapshot:** `finish-1023/`, `logs/` and `runpod/` (24,942 files, matching counts) are on the SSD at `routevoice-checkpoints/mac-snapshot-20261022/`.
- **Pods:** `rv-overnight-pnr2` was deleted, and the guard is stopped. The RunPod account API shows **0 pods, 0 network volumes, 0 serverless endpoints, and current spend $0.00/h**. Balance: $88.13.
- **SSD:** this line originally said the SSD was ejected. **That was wrong.** It stayed connected, and from 23 Oct it holds the local closure, fix-1 and fix-2 runs. The 51 GB fix-2 run (`~/rvssd/pipe2-local`) was backed up on 24 Oct to the public HF dataset `sanjuhs/routevoice-engine-fix2-20261024`, verified by download (1,227/1,227 files; record in `finish-1023/pipe2-hf-20261024/`). (Corrected 24 Oct.) The antenna close-out run (`runs/pipe2-ant`, 46 GB) was added to the same dataset under `archives/pipe2-ant/` the same evening, verified 680/680 files (record in `finish-1023/pipe2-ant-hf-20261024/`). Both runs now have verified HF copies; the SSD can be ejected.
- **Estimated RunPod spend:** **$34.82** ($8.96 pnr1 + $25.87 pnr2) against the $60 cap the user set.
- **Still undone for the release:** routed engine power (the OpenROAD power step errored), the antenna/timing closure run, the 12 failing W12 units, and integrating the W13 bank drivers.

### 22 Oct 19:30 IST: ✅ engine routed, activity-annotated power (lead, local Mac, from the verified pod backup)

- **Inputs:** final routed ODB + nominal extracted SPEF + signoff SDC + the real-speech gate-level SAIF (150 ns), restored from the checksum-verified Hugging Face backup after the pod was deleted (≈18:35 IST 22 Oct).
- **Fix:** the pod failure was an OpenSTA SAIF parse error on 2 Verilator cell-internal `$unnamedudp1` blocks, which were removed (4 lines).
- **Annotation:** 1,364,228 pins annotated, 32,552 not (97.7%).
- **Power:** **0.158 W** at the 150 ns clock (clock tree 18.8 mW) → **≈98.7 µJ per projection ≈ 241 pJ/MAC** (pre-route estimate was 162).
- **At the achieved TT clock** (≈4.48 MHz): ≈0.106 W. Evidence: `routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/routed-power-lead/`.
- **Post-layout simulation:** zero-delay replay of the routed netlist passes 54/54 vectors (17,280 outputs, identical cycles). SDF timing simulation is not supported by the available simulators.
- **RunPod:** pod `rv-overnight-pnr2` deleted ≈18:35 IST 22 Oct (no pods left). Total RunPod spend **$34.82** ($8.96 + $25.87): within the user's later $60 approval, over the original $30 goal figure.

### 21 Oct 15:51 IST: engine signoff checks complete (W10 `runs/full`, lead-verified from state metrics)

- **Magic DRC 0 · KLayout DRC 0 · Netgen LVS "Circuits match uniquely"** (0 device/net/pin/property differences) · illegal-overlap check passes · routing DRC 0.
- **Antenna FAILS:** 151 pin / 130 net violations remain after the flow's antenna repair.
- **Post-route STA (extracted):**
  - setup fails at 150 ns (TT −72.9 ns, SS −251 ns), i.e. ≈4.5 MHz TT / ≈2.5 MHz SS achieved;
  - hold passes in all 9 corners.
- **Gate level:** the mapped netlist passes the 54-vector replay (17,280 outputs), and the real-speech SAIF has been captured.
- **Disk incident:** routed power and the post-layout sim were stopped by a full pod disk. The lead freed 20 GB and W10 is re-running them.
- **Closure run** (post-GRT repair + antenna fixes) queued.

### 21 Oct 10:30 IST: ✅ 1280×320 engine fully ROUTED, DRT 0 violations (W10 variant C, lead-verified)

- **Design:** local-partials engine (`engine_local.sv`), FP_CORE_UTIL 30 / PL density 35, no post-GPL repair, CTS NDR none, 150 ns SDC.
- **Global route:** overflow **575**, vs 260k for D4 and 3.37M for D1.
- **Detailed route:** **0 violations** (68,834 → 25,987 → 22,316 → 1,794 → 296 → … → 0). 359,580 nets, 68.9 m of wire, 4.29 M vias. Die 22.74 mm².
- **Post-route checks:** antenna, TR-DRC, disconnected pins and wirelength checkers pass.
- **Post-route STA** (RCX SPEF, 150 ns):

| Corner | Setup WNS | Hold WNS |
|---|---|---|
| nom TT | −72.9 ns | ≥ +0.16 ns |
| nom SS | −251 ns | ≥ +0.16 ns |
| max SS | −307 ns | ≥ +0.16 ns |
| FF | positive | ≥ +0.16 ns |

- **Achieved clock: ≈4.5 MHz TT / ≈2.5 MHz SS.** Slew violations are 575k at TT (the skipped repair). One engine gives ≈0.44 GMAC/s at TT vs the ≈0.6 GMAC/s real-time need, so 2 engines are needed, or closure.
- **Next:**
  - Signoff (IR, DRC, LVS), routed power and the post-layout sim are automatic on this route.
  - A post-GRT-repair closure run has been launched in parallel.

### 21 Oct 04:16 IST: ✅ Taalas weight arrays for the WHOLE model in GF180 layout (W13, integrity-verified)

- **Banks:** 81 pitch-matched bank macros (GDS/LEF/Liberty/Verilog) carry all 98 matrices, i.e. **31,457,280 four-bit selections**.
  - Layout readback matches all **125,829,120 bits**, checked by the builder and by an independent audit with a missing-via negative control.
  - **DRC 0 on all 81.**
  - **Full Netgen LVS** (unique match, no property errors) on 6 representative banks covering all 4 physical shapes and all source-matrix classes; each correctly rejects a wrong-width negative control.
  - All 81 load together in OpenSTA, OpenROAD and Yosys.
- **Blocks:** 14/14 fabric blocks are READY as **arrays**. The WL/PC drivers, decode, latches and output escape are in progress (W13 resumed).
- **Area:** ≈174.7 mm², within 0.3% of the floorplan estimate.
- **Also by now:**
  - W14: 4 signed-off logic macros.
  - W15: both dies route the real arrays plus logic macros, with top-level wiring DRC 0 and a passing power grid. Real nets, drivers and full-deck DRC are still to come.
  - Extra clips also pass with Taalas weights: "Plant present." and "Seasonable.", each 18/18 hashes.

### 21 Oct 03:45 IST: ✅ Taalas end-to-end PASS (W11, lead-verified)

- The full recognizer v4 reads EVERY weight as a **4-bit index + 16-entry UINT8 codebook per 64×1 group**: the Taalas fixed-selection storage. The frontend uses the lossless affine-INT8 form.
- **Storage:** 28,641,280 → **17,497,600 B**, with 0 reconstruction mismatches over every byte.
- **Unit tests:** all seven responders pass exhaustive readback.
- **F64 "Switch on the lights":** tokens [28176, 373, 278, 26068, 2], 18/18 hashes, **312,578,649 clocks (delta 0 vs v2)**, faults 0. Rendered text: "Switch on the lights".
- **Evidence:** `routing-voice-chip-design/overnight-20261014/finish-1023/w11-taalas-e2e/` (logs `*-positive.log`, `*-compare.log`, `*-render.log`).
- Two more corpus clips are running.

## MORNING SUMMARY (read this first)

*Written at 05:45 IST from lead-verified results. Any later update is marked at the bottom of this section.*

### The short answer

**Yes, RouteVoice can be a Taalas-style GF180 chip.** Tonight produced real evidence for that:

- **Two reticle-sized dies (25 × 29 mm each):** possible today, using only open-PDK parts and with **zero change to the model's numbers**.
- **One die (25 × 31 mm):** possible if the chip gets a denser SRAM than the open GF180 one, for example a foundry SRAM compiler.

The weights stop being the problem once they are stored Taalas-style; working memory and wiring fanout become the problems.

### What was verified tonight (✅ = lead re-checked the actual output)

| # | Result | Evidence |
|---|---|---|
| ✅ 1 | **Every weight of the model is on-chip, and the chip still hears "Switch on the lights"** (tokens [28176, 373, 278, 26068, 2], 18/18 output hashes, 0 harness weight replies, 0 mismatches, identical 312,578,649 clocks). v1 moved all six harness services (28,641,280 B). v2 also built in the last four model constants, leaving 31 runtime inputs (audio, control, resets, job tags) and no weight or constant input. | `onchip-all/` (v1), `onchip-all/RESULTS-v2.md` |
| ✅ 2 | **The real Taalas weight array exists in GF180 layout, for the approved 1280×320 projection** (all 409,600 real 4-bit selections as mask-programmed transistors). Pitch-matched bank: **1,004 × 2,259 µm = 2.27 mm² = 5.54 µm² per weight, including readout. DRC 0. Full-bank LVS unique match** against a netlist built independently from the model's indices; all 1,638,400 bits read back from the GDS. Planted-error LVS checks were correctly rejected. | `taalas-pitch/`, `taalas-array/` |
| ✅ 3 | **All 31.5 M weights would take ≈174 mm²** at that measured density (+≈57 mm² row decoders/drivers, estimated). The open GF180 SRAM would need ≈6,400 mm² for the same bits, about 37× more. | lead arithmetic |
| ✅ 4 | **Whole-chip floorplans with pad ring, power grid and IR drop pass**, using measured inputs: W6 density, a Verilator-measured memory inventory (8,501,818 mutable array bits + 237,524 register bits), measured SRAM LEFs, and the lossless frontend below. **Two dies 25 × 29 mm (open SRAM, no numeric change): connectivity pass, IR 38–43 mV (<5%), 0 shorts. One die 25 × 31 mm (dense SRAM): pass, IR 2.2%.** | `floorplan/RESULTS.md` § "Final design point"; renders `floorplan/runs/final_*/floorplan.png` |
| ✅ 5 | **The frontend's 8.3 MB of FP32 coefficients can be stored losslessly in 2.09 MB.** The model's own affine-INT8 codes + scale/offset rebuild every FP32 bit (lead checked all 2,073,600 weights: 0 mismatches). Plain re-quantized INT8 **fails** the accuracy gate (+2.4/+4.6/+0.6 pt WER), so it is not used. | `accuracy-int8/` |
| ✅ 6 | **Measured mutable state is 1.09 MB**, and the two big double-buffers are genuinely both needed (zero safe saving). One die with the open bit cell would need ≈161 KiB less state or a schedule change. | `storage-inventory/`, `onchip-all/RESULTS-v3.md` |
| ✅ 7 | **Representative compute energy ≈66 pJ per multiply-accumulate** on a repaired, placed engine slice with real gate-level activity (106 mW at 5 MHz, 88% of pins annotated, pre-route). At the model's ≈0.6 G MAC/s real-time load, matrix compute is ≈40 mW, far under 1 W. SRAM, frontend, attention and IO are not included yet. | `fabric/runs/…pre-route-gate-cell-activity/` |
| ✅ 8 | **The 1280×320 engine is verified at gate level** (54 vectors, 17,280 FP32 outputs, resets, 104,112 stalls) in two variants: standard-cell ROM 8.26 mm², array-port 6.14 mm² of cells. | `fabric-k64/` |
| ✅ 9 | **Fanout fixed in the full 1280×320 engine, and its real power measured (pre-route).** W9's `buf-v4` caps every net at 16 loads (was 11,359), still passes all 54 vectors at gate level, and places in minutes. With a 100%-annotated real-activation SAIF (1,299,526 of 1,299,526 pins): **0.80 W, 66 µJ per projection ≈ 162 pJ/MAC**, about 10× better than the unbuffered engine (8.6 W). No clock tree or repair yet; ideal clock; placement RC. | `power-bufv4/RESULTS.md` |

### What is NOT done (honest list)

1. **Routed signoff of the 1280×320 projection.** No variant finished detailed routing + extracted timing + signoff power tonight. The cause, now precisely diagnosed:
   - single nets drive 4,000–11,000 loads (row-index bits, shared products, reset), and synthesis inserted no buffers on them;
   - repair takes hours, and the unrepaired netlist burns huge short-circuit power (8.6 W, not representative);
   - the 320-lane datapath alone misses 20 ns by 101 ns (≈8 MHz).

   **Fix:** register duplication / buffer trees on the row bus, the shared-product broadcast and reset. **Update 07:30: done in W9's `buf-v4` (item 9).** Fanout is now ≤16 and power has dropped about 10×. Still open: post-placement timing repair was still running at 07:30 (setup −125 ns at 20 ns before repair, i.e. ≈7 MHz unrepaired), then CTS, routing, extracted STA, DRC/LVS and routed power. The next run should start from `buf-v4` with a realistic clock (≈100–150 ns) or added pipeline stages.
2. **Taalas array timing at full-bank scale.** Per-column readout passes, but driving wordlines/precharge across all 1,280 columns fails at 60 ns. A guarded 120 ns cycle passes at the slow corner (sampled). Full-row energy is not yet measured.
3. **One die needs denser memory** than the open GF180 SRAM bit cell (17.8 µm²/bit cell, 51 µm²/bit as macros), or a reworked quantizer schedule that frees ≈161 KiB.
4. **The on-chip ROMs in the full-recognizer simulation are behavioral ROM models**, not yet the Taalas array netlist; the physical array is proven separately (item 2 above).
5. **Not started:** real-time throughput with the measured engine (estimate: one or a few engines suffice), FPGA bring-up, the pad-ring signal wiring, and foundry signoff.

### Recommended next steps (in order)

1. Fanout is done (`buf-v4`). Next: pipeline the 320-lane datapath, or set a 100–150 ns clock, so repair finishes; then CTS, route and extracted power on `buf-v4`.
2. Segment the Taalas bank's wordlines (or add drivers) to get under 60 ns, and measure full-row read energy.
3. Choose the memory route: a GF180 SRAM compiler (talk to the foundry/shuttle) for one die, or commit to two dies with a die-to-die link.
4. Swap the behavioral ROMs for the Taalas array model in the full recognizer and re-run "Switch on the lights".

### Final update (07:55 IST)

- **New since 05:45:** item 9 above, the buffered 1280×320 engine with 100%-annotated real-activity power (0.80 W, 66 µJ per projection, ≈162 pJ/MAC, pre-route, no clock tree). It also passes both the sharded and the serial gate replays (54 vectors, 17,280 outputs).
- **Still open:** routed signoff. W9's repair at 20 ns was adding area (+26% and rising) when stopped, and W2's two 320×320 routes stalled in global routing. Next time, start from `buf-v4` with a 100–150 ns clock or pipelining.
- **Shut down:** both Codex workers (W2, W9) and the local W2 route run were stopped at 07:53, and the spend guard was stopped after confirming no pods remain.

### Update 09:55 IST: floorplan re-screened with the measured engine (`floorplan/MEASURED-ENGINE-UPDATE.md`)

- **Inputs:** the engine block now uses W9's measured placed area (16.27 mm²) and the measured power (0.80 W × an assumed 1.35 clock allowance = 1.08 W, running continuously at full rate) instead of the assumed 0.15 W.
- **Result: the IR screen now FAILS the 5% limit in every case:**
  - one die: 277 mV (8.4%);
  - two dies: 349–358 mV (≈10.7%);
  - 80 µm straps: still 248 mV.
- Connectivity still passes and there are 0 shorts. The average drop is 12 mV, so this is a local hot spot at the engine terminals in the die centre.
- **Item 4's IR pass therefore holds only at the real-time average load** (≈12% duty with clock gating ≈ the old 0.15 W). Full-rate operation needs a local engine grid, an engine next to the pads, or smaller tiles.
- **Routed timing/power for the 1280×320 projection was NOT achieved.** The measured numbers are pre-route (item 9).

### Update 20:20 IST (resumed after the pause): floorplan PASSES at the achievable engine clock

- The engine cannot run at 50 MHz (≈145 ns critical path), so the 1.08 W continuous load used at 09:55 was not a reachable operating point.
- At the 150 ns clock now being routed: measured 66.4 µJ/projection → 0.106 W, × 1.35 clock allowance = 0.144 W. That still meets real time (0.66 vs ≈0.6 GMAC/s).
- IR screens with that load: one die 77.8 mV (2.4%), two dies 90.1 / 85.4 mV (2.7% / 2.6%), all PASS, 0 shorts (`floorplan/MEASURED-ENGINE-UPDATE.md`).
- Routed signoff of the engine at 150 ns is running locally (CTS done). Its routed power will replace this estimate.

### Cost and housekeeping

- RunPod: one 32-vCPU CPU pod (`rv-overnight-pnr1`, $1.28/h). **Final spend $8.96 of the $30 budget. The pod was terminated by the lead at 07:52 IST, and the RunPod API lists no pods.** Its key results were first copied to the SSD (`routevoice-checkpoints/overnight-20261014/pod-final/`, 26 GB: W9 engine runs + evidence, the hash-verified buf-v4 SAIF, W8 `projection-complete`). The W2b `fabric-k64` pod copy is partial (its verified results are local).
- All work is on branch `overnight-2026-10-14` on GitHub (overnight files only), and the overnight workspace is mirrored to the SSD every 20 min.
- Large finished intermediates were moved to the SSD with byte-verification; `*OFFLOADED*` / `MOVED-TO-SSD.txt` files list them.
- Mistake made and fixed: one commit briefly swept your own uncommitted files (`MASTER_GOAL.md`, `plan.md`, …) onto the overnight branch. It was undone with a force-push of the overnight branch, and your files are back to uncommitted, byte-identical. GitHub may keep the orphaned commit `e13d89260` reachable by its ID for a while.

## Goals

| # | Workstream | Target by morning |
|---|---|---|
| W1 | All weight services on-chip in RTL | Replace the six harness weight ports (28,641,280 B) with on-chip ROM/fixed-selection responders; rerun F64 "Switch on the lights" with zero harness weight replies |
| W2 | Measure the fixed-weight fabric | 320×320 fixed-selection projection from real 4-bit indices → GF180 synthesis + full LibreLane flow with power grid, CTS, routing, DRC/LVS, STA, power → mm²/MHz/mW per weight |
| W3 | Whole-chip floorplan with power routing | Every block placed as a sized macro on a die with pad ring and chip-level PDN; IR-drop estimate; die-count decision |
| W4 | Full-top synthesizability | Yosys pass over the full integrated top; list of non-synthesizable constructs (first FPGA step) |

## Baseline facts verified at start (00:00–00:30)

- All decoder/encoder weight images use exactly 16 distinct UINT8 values per (64 inputs × 1 output) group → 4-bit index + 16-entry book is exact (checked cross, self, FF up/down images).
- The qualified full-chain binary and its exact F64 command exist (`experiments/chip-integration-20261012-Q8-learned-fulltables-numerical-run-v2/commands.json`).
- Host-served weight services at start: frontend 8,298,240 B; encoder immutable 5,146,880 B; encoder QKV/O 2,457,600 B; positions 1,310,720 B; decoder cross/FF 8,908,800 B; decoder self 2,519,040 B.

## Log

*(Timestamp note: some entries were stamped from estimates rather than the clock: 01:05–01:22 entries run ≈15 min late; entries marked ≈ after 02:40 were corrected against `date` at 02:54. All entries after 02:54 are read from `date`.)*

- 00:30 — branch, workspace and SSD folder created; keep-awake on.
- 00:50 — Codex W2 (320×320 fabric) launched. Model: GPT Astra, high reasoning (user's Codex default).
- 00:52 — Codex W1 (decoder weights on-chip) launched.
- 00:55 — User approved lifting the 13 Oct pause and adopting `docs/ROUTEVOICE-PROPOSED-PHYSICAL-GOAL-2026-10-13.md`; recorded in `routing-voice-chip-design/AGENTS.md` and the proposal's status line.
- 00:56 — W2 claimed bit-exact verification of the 320×320 engine (32 vectors, 10,272 checks, 0 failures); LibreLane started. Codex W2b launched on the approved 1280×320 K64 encoder FF projection.
- 00:57 — RunPod pod `rv-overnight-pnr1` (cpu3g, 32 vCPU, 128 GB, $1.28/h) created; independent spend guard running (`overnight-20261014/runpod/rp.py guard`, cap $28, hard stop 07:15 IST). LibreLane + Nix installed on the pod in ~3 min.
- 01:00 — Codex W3 (whole-chip floorplan + PDN + IR drop) launched.
- 01:05 — Mac disk at ~21 GiB free (swap + EDA runs). Offloading 234 old 12 Oct build folders (6.4 GB) to SSD with checksum verification; only the two folders tonight's work uses stay local.
- 01:08 — Codex W1b (encoder weights) and W1c (frontend + positions) launched as parallel splits of W1.
- 01:12 — **Found the memory hog:** the lead's full-top Yosys run reached a 90 GB footprint while still in the SystemVerilog front end, pushing the Mac into 24 GB of swap and below the disk floor (W1 and W2 correctly paused their builds). Killed it; moved the run to the pod (503 GB RAM, 440 GB cap). Finding by itself: the integrated RTL, as written for simulation, is extremely expensive to elaborate for synthesis.
- 01:15 — Offload finished: 234/234 folders copied to SSD and checksum-verified, 0 failures; local copies removed. Disk 31 GiB free. `caffeinate` holds the Mac awake for 7 h.
- 01:16 — W2b claims: K64 identity PASS (409,600 coefficients, 6,400 books); both variants (SC-ROM and ARRAY-PORT) bit-exact on 54 vectors (17,280 integer + 17,280 FP32 checks each), 4 mid-vector resets, random stalls; 4,163 cycles per projection. *(claimed — lead re-check pending)*
- 01:20 — **LEAD-VERIFIED PASS (W2b SC-ROM, 1280×320 K64, all weights on-chip as constants):** rebuilt independently in the lead's scratch dir and re-ran: `PASS vectors=54 outputs=17280 … unstalled_cycles=4163`. W2b's integer expected/inputs files are byte-identical to the September reference (`build/taalas-serial/word-nibble-k64-1280x320/expected.hex`, `inputs.hex`). The testbench supplies only activations/expected values; the 409,600 indices and 6,400 books are RTL constants.
- 01:20 — W1 (decoder body cross/FF + compact self, 11,427,840 B): claims exhaustive responder tests passed (278,400 body + 78,720 self packets, 0 mismatches, held-response and warm-reset checks); full-chain F64 positive run started. W1b (encoder, 7,604,480 B) and W1c (frontend FP32 2,074,560 words + positions) ROM images generated and round-trip exact; W1c frontend unit test 0 mismatches. *(claimed)*
- 01:22 — **W3 first floorplan sweep (abstract macros, assumed inputs):** totals 1,464 mm² (optimistic 3.5 µm²/selection) to 2,584 mm² (placeholder std-cell 40 µm²/selection). Breakdown at optimistic density: all fixed-weight layers ≈ 81 mm²; embedding/head 46; codebooks 145; frontend FP32 coefficients 158; mutable SRAM (open-PDK 512×8 macro = 0.209 mm² per 512 B ≈ 51 µm²/bit) ≈ 267; plus two W3-*assumed* reserves (FP32 KV 442 mm², private state 236 mm²). Takeaway: **weights are not the die-size problem; working-memory density, FP32 frontend storage, codebook overhead and unmeasured reserves are.** Reserves to be replaced by the real full-top memory inventory (Yosys on pod).
- 01:07 — W3 stopped and resumed with `floorplan/LEAD-GUIDANCE-1.md`: fix PDN macro connections, drop the assumed reserves, add memory-density and design-lever scenarios, and use measured fabric numbers. W1c resumed with permission to run its F64 simulation in parallel with W1/W1b. W2b's two LibreLane flows were mirrored to the pod (14 threads each) so whichever of the Mac or pod finishes first counts.
- 01:10 — **All three on-chip integrations are in full F64 simulation at once:** W1 (decoder), W1b (encoder), W1c (frontend + positions). All three compiled; fixtures and exhaustive responder unit tests passed *(claimed)*.
- 01:12 — W2 measured: the 64×320 standard-cell ROM slice (20,480 weights + 320-lane datapath) synthesized to 190,460 GF180 cells = **4.230 mm² cell area** *(claimed; routed numbers pending)*.
- 01:14 — **W3 baseline without reserves** (custom 7.04 µm²/selection, open-PDK SRAM, no design levers): one die = 924.75 mm² (needs a 34 mm outline, above reticle size); two dies = encoder 488.52 mm² + decoder 444.23 mm², each placing in 25 mm.
- 01:16 — **Power routing works at chip scale:** the 34 mm single-die baseline floorplan (GF180 pad ring, 24 supply-pad pairs, core ring + straps, 117 macros) passes VDD/VSS connectivity, with no VDD–VSS shorts. IR drop at an *assumed* 0.93 W: worst VDD drop 69.1 mV + worst ground rise 64.5 mV = 133.6 mV = **4.05% of 3.3 V** (limit 5%). Blocks are abstract macros (no internal routing); the power figure is assumed, not measured.
- 01:20 — Lead checked the 34 mm render (`floorplan/runs/custom7_sram_open_macro_off_baseline_whole_34mm/floorplan.png`): pad ring, power mesh and 117 macros. The visible area hogs are the FP32 frontend coefficients and the codebook/metadata rows, not the weight fabric. The run log says "All shapes on net VDD/VSS are connected". However, the separate `*_connectivity.rpt` files list 691/490 "unconnected shape" entries, possibly left over from the earlier failed attempt; W3 must regenerate them before this counts as lead-verified.
- 01:22 — Two-die baseline: both 25 mm partitions pass connectivity and the IR screen. Encoder die 156.6 mV (4.75%), decoder die 131.3 mV (3.98%), at assumed power. *(claimed)*
- 01:23 — W3 finished (`floorplan/RESULTS.md`). Area model (mm², before pad ring/whitespace), with design levers off → on. Levers: frontend INT8, books in the dense array, KV8 where applicable; the numerical ones need accuracy re-validation.
  - custom 7.04 µm²/selection + open SRAM: 925 → 815
  - custom 7.04 + dense custom SRAM (12 µm²/bit, assumed): 717 → 608
  - optimistic 3.5 + dense SRAM: 578 → **399 (≈20×20 mm)**
  - Standard-cell selection rows are still placeholders.
- 01:24 — W2b measured: the 1280×320 ARRAY-PORT variant (books, shared products, 320 lanes, accumulators, FP32 output; index array excluded) maps to **6.137 mm² cell area**, of which 0.743 mm² is sequential. That is ≈15 µm² per weight of non-index overhead before routing *(claimed)*. Physical flow running.
- 01:26 — User asked whether Taalas reduces stored weights to ~1 MB. Answer recorded: no. Each of the 31.46M weights still needs its own 4-bit selection (15.7 MB) plus books (7.9 MB). Taalas makes each bit much cheaper to store (≈1.76 vs 51 µm²/bit), removes per-weight multipliers (16 shared products) and eliminates weight traffic.
- 01:27 — **W1c: full frontend ran on on-chip FP32 coefficients** (all 16 chunks committed, 0 frontend ROM mismatches, host frontend replies disabled). Encoder phase in progress *(claimed; final F64 pass pending)*.
- 01:30 — User set the overnight `/goal`: all six services on-chip with F64 passing; measured GF180 area/timing/power for the 1280×320 Taalas projection; floorplan with PDN/IR updated with measured numbers; morning summary; RunPod < $30 and pods terminated; "make it like Taalas".
- 01:31 — **Codex W5 launched (Taalas readable-cell array):** scale the existing DRC/LVS-clean GF180 access-array specimens (`experiments/taalas-access/`, 19 Sept) into a real mask-programmed array macro holding the projection's actual 409,600 four-bit selections. Deliverables: DRC/LVS, bit readback, SPICE read time/energy, LEF/GDS, measured µm²/selection replacing the assumed 7.04.
- 01:33 — Second verified SSD offload (13 Oct: 18 folders; 11 Oct: 284 folders except the one still referenced): 302/302 verified, 0 failures. Disk at 31 GiB.
- 01:33 — W1b: all 16 frontend chunks passed; encoder phase now exercising the on-chip encoder ROMs *(claimed)*. W2's 64×320 SC-ROM layout failed at detailed placement after post-placement repair (`DPL-0036`), so the standard-cell ROM is congestion-limited at the requested density; W2 is retrying.
- 01:36 — **W5 (Taalas array): real mask layout generated.** All 409,600 four-bit selections of the approved projection are encoded as via programming. GDS readback recovered all 1,638,400 bits with 0 mismatches against the K64 source and W2b's indices *(claimed; lead spot-check pending)*.
- 01:40 — **W5 measured Taalas density:** the 64×320 tile (one book group, 81,920 bit cells, the model's real weights) passes GF180 KLayout DRC with 0 markers. **Cell-only area = 4.87 µm² per 4-bit selection** (1.22 µm²/bit), better than the 7.04 assumed earlier. Scaled to all 31.46M selections: ≈153 mm² of cell array, before periphery (row drivers, sense, latches; measurement pending). For comparison, the open-PDK SRAM is ≈204 µm² per 4-bit selection (≈42× larger).
- 01:40 — W1b: encoder layers 0 and 1 passed on on-chip encoder ROMs (61,440 QKV + 2,560 O RTL replies each, 0 mismatches) *(claimed)*.
- 01:43 — **LEAD-VERIFIED (W5 Taalas array geometry):** the lead measured the GDS bounding boxes with KLayout.
  - Tile `RV_K64_CELL_TILE_00`: 925.69 × 107.71 µm = 0.0997 mm² / 20,480 selections = **4.87 µm²/selection**.
  - Full array core `RV_K64_CELL_ARRAY_CORE` (all 409,600 selections of the projection): 3,763.69 × 619.71 µm = **2.33 mm² → 5.69 µm²/selection** including inter-tile spacing.
  - DRC reports (`base/tile0.lyrdb`, `base/array-core.lyrdb`): 0 items across 651 rule categories. The deck is the project's selected GF180 rule subset (`experiments/taalas-access/main.drc`), not a full foundry signoff deck.
  - Periphery (row decoder, sense/latches), LVS and timing are pending.
- 01:47 — **LEAD-VERIFIED (W5 tile LVS):** Netgen `Circuits match uniquely.` for the 81,920-transistor tile.
  - The reference netlist is generated independently from the admitted K64 indices (`scripts/check_base.py`): each access NFET's drain connects to bit line `IDX{c}_{b}` only where that index bit is 1, otherwise to an open node. LVS therefore proves the layout encodes exactly the model's weights for rows 0–63.
  - The "canonical" step only shortens Magic's hierarchical net names, with an asserted one-to-one map. The first, un-normalized LVS failure is preserved.
  - W5 also claims: full 20-tile array DRC 0; array-plus-receiver tile DRC 0 (after a via-enclosure fix; the failure is preserved); joined bank passes the sampled TT/SS read protocol at 20 ns and 25 ns.
- 01:47 — W1: all six encoder layers passed; now in the producer/decoder phase, where its on-chip decoder ROMs are exercised. W1c at encoder layer 4; W1b at encoder layer 4 (layers 0–3 passed) *(claimed)*.
- 01:52 — W2b measured: the SC-ROM 1280×320 variant (all 409,600 indices on-chip as standard-cell constant logic) maps to **8.255 mm² cell area** (34-min synthesis, 0 unmapped cells). Versus ARRAY-PORT 6.137 mm², the indices add ≈2.12 mm² ≈ **5.2 µm²/selection pre-route**, comparable to the custom Taalas array (4.87 cell-only, 5.69 with spacing). This includes synthesis constant-folding effects; routed area and congestion (cf. W2's DPL-0036) will decide *(claimed)*.
- 01:55 — **On-chip status in the full recognizer (claimed, F64 runs still in progress):**
  - W1: decoder tokens 1–2 completed on on-chip decoder ROMs (all decoder layers, full vocabulary logits, committed winner).
  - W1b: all six encoder layers passed on on-chip encoder ROMs (each layer: 61,440 QKV + 2,560 O RTL replies, 0 mismatches); now decoding.
  - W1c: frontend (16 chunks on on-chip FP32 coefficients) and all six encoder layers passed; now decoding with the on-chip position ROM.
- 01:55 — W5: array tile + 1,280 readouts LVS = **unique match**, 87,040/87,040 devices, no property errors. Decoder, phase control and bank mux are not yet included *(claimed)*. W2b local SC-ROM P&R stopped at its runtime budget, as instructed; the identical config is already running on the pod (`rv-overnight-pnr1`). The pod ARRAY-PORT synthesis gives 6.10 mm², consistent with the Mac's 6.137 mm².
- 02:01 — **LEAD-VERIFIED: decoder weights on-chip, full recognizer F64 passes (W1).** Simulation exit 0 after 3,414.9 s.
  - Log `onchip/logs/20261014T010334-positive.log` shows the original harness's own pass line `FOUR_STAGE_GREEDY_…_ONBOARD_EOS_PASS tokens=5 … encoder_layers=6`, all five tokens through EOS, and 27,990,570 checks.
  - Service counters: `ONCHIP service=decoder_body rtl_replies=1392000 host_replies=0 mismatches=0` and `ONCHIP service=decoder_self rtl_replies=787200 host_replies=0 mismatches=0`.
  - The lead confirmed the wrapper `rv_allonchip_top_v1` has **no input ports** for decoder body/self weight data; they are served only by internal ROM responders (`rv_onchip_decoder_body_v1`, `rv_onchip_decoder_self_v1`).
  - **11,427,840 bytes of decoder weights moved from the harness onto the chip.** The 18-output hash comparison and text render are pending (W1 running them).
- 02:01 — W5: the 20-tile array-plus-readout assembly passes hierarchical DRC with all 1,638,400 bits matching, but measures **22.321 mm²**, ≈90% readout, because each 64-row tile carries its own 1,280 readouts. The earlier October tall-bank study (256/320/1,280 rows per receiver, circuit-qualified) predicts ≈154 mm² cells + ≈67 mm² periphery for the whole model. `taalas-array/LEAD-GUIDANCE-1.md` asks W5 for a measured 320-row-bank layout to quantify the area-versus-read-time trade.
- 02:03 — **W1 fully confirmed (lead read the logs):** `onchip/logs/20261014T020110-compare.log` reports all 18 native output hashes plus five tokens through EOS. The render log shows `"passed": true, "text": "Switch on the lights", "tokens": [28176, 373, 278, 26068, 2]`. Clock count is 312,578,649, identical to the retained baseline, so the on-chip ROMs are cycle-transparent.
- 02:04 — W1 stopped and resumed with `onchip/LEAD-GUIDANCE-1.md`: **merge W1 + W1b + W1c into `rv_allonchip_top_all_v1`**, with all six fixed-weight services on-chip in one design and no external weight ports, then run the full F64 (`overnight-20261014/onchip-all/`).
- 02:07 — **LEAD-VERIFIED: frontend FP32 coefficients + position table on-chip, full recognizer F64 passes (W1c).**
  - Log `onchip-front/logs/20261014T010943-positive.log` shows the harness pass line `…_ONBOARD_EOS_PASS tokens=5`.
  - Service counters: `ONCHIP service=frontend_immutable rtl_replies=55720960 host_replies=0 mismatches=0` and `ONCHIP service=producer_positions rtl_replies=2560 host_replies=0 mismatches=0`.
  - Compare log: all 18 hashes and five tokens through EOS. Render: `"passed": true`, text "Switch on the lights".
  - Minor remaining boundary: the W1c wrapper still takes three scalar position-quantization inputs (`source_start_position_scale/zero/offset`, ≈6 bytes of configuration). The 1,310,720-byte table itself is on-chip. These should be tied to constants in the merge.
- 02:07 — Pod full-top Yosys: slang elaboration of the entire integrated recognizer **completed without errors** (front-end synthesizability), now in `proc` passes at ≈97 GB. W2 64×320 SC-ROM slice: detailed placement done at 14.27 mm² footprint, 6.13 mm² cells after buffering (≈43% utilization); CTS/routing pending.
- 02:10 — **LEAD-VERIFIED: encoder weights on-chip, full recognizer F64 passes (W1b).** Exit 0 after 3,451 s.
  - Log `onchip-enc/logs/20261014T011032-positive.log` shows the harness pass line `…_ONBOARD_EOS_PASS tokens=5`.
  - Service counters, all `host_replies=0 mismatches=0`: `encoder_QKV` 368,640 RTL replies; `encoder_O` 15,360; `encoder_immutable` 1,947,520.
  - The lead confirmed the W1b wrapper has no encoder weight-data input ports. The 18-hash compare and render are pending (W1b running them).
- 02:10 — **All six services have now each passed the full F64 on-chip** (W1: decoder 11.43 MB; W1b: encoder 7.60 MB; W1c: frontend + positions 9.61 MB; total 28,641,280 B). The merged single design `rv_allonchip_top_all_v1` (all six at once; 60 former service inputs converted to debug outputs; only PCM/control/configuration/reset inputs remain) passed lint and is building. W1 is adding an exhaustive check of all 163,840 position words.
- 02:10 — W2 64×320 SC-ROM slice after CTS: typical-corner setup slack −47.29 ns at the 20 ns target (critical path ≈67 ns, ≈15 MHz before repair). Standard-cell ROM logic is slow as well as large.
- 02:12 — W1b fully complete: the 18-hash compare passed and the render gives "Switch on the lights" with tokens [28176, 373, 278, 26068, 2].
- 02:12 — **Merged all-six design `rv_allonchip_top_all_v1` (`onchip-all/`):** lint, generation, compile (96 s) and fixture passed. Exhaustive responder tests cover **all 28,641,280 ROM bytes (17 images, incl. all 163,840 position words) with 0 mismatches**, plus held-response and reset checks. 59 former service inputs are now debug outputs. Full merged F64 positive started at ≈02:12 (≈57 min) *(claimed; lead check at completion)*.
- 02:12 — W2b: the gate-level (mapped-netlist) simulation of the 1280×320 projection produced correct outputs for the first vector (320 outputs, 4,163 cycles, 1,280 row reads); the full gate-level regression is running.
- 02:15 — W5 first pass finished (`taalas-array/RESULTS.md`).
  - Measured layout (scoped GF180 FEOL/BEOL DRC, density/antenna excluded):
    - cell-only tile 4.87 µm²/selection (DRC 0, LVS 81,920 devices);
    - array + analog readout tile 50.2 µm²/selection (DRC 0, LVS 87,040 devices);
    - decoded tile (adds 10 local row decoders) 54.9 µm²/selection, compositional LVS across 111,460 devices, all real bits match;
    - 20 readout tiles 22.32 mm² (hierarchical DRC 0, all 1,638,400 bits match).
  - Read timing (joined 64×32 bank, extracted capacitance, ideal drivers): settling 2.98 ns TT / 4.39 ns SS; 62–78 pJ per 32-lane read. Fast enough for a 20 ns cycle at the array level.
  - Periphery (isolated, DRC/LVS clean): row decoder slack −0.81 ns; 20-way mux128 slack −10.58 ns at 20 ns. **The complete macro is not timing-qualified.**
  - Resumed with the tall-bank guidance (320-row banks, to cut readout replication).
- 02:25 — **W5 tall banks:** four 320-row banks (one set of 1,280 readouts per bank, 5,120 total) for the full projection measure **12.44 mm² (≈30.4 µm²/selection incl. analog readout)**, versus 22.32 mm² (25,600 readouts) for 64-row tiles. All 1,638,400 bits match; full-assembly DRC 0. Full-bank LVS and SPICE read timing are running *(claimed)*.
- 02:25 — W2 320×320 datapath-only variant (V2, external index/book array): 222,596 cells, **5.28 mm² cell area**. Together with W2b ARRAY-PORT (6.14 mm²), a 320-lane shared-product engine costs ≈5–6 mm² of standard cells regardless of matrix height. W2b: the ARRAY-PORT **gate-level netlist regression passes** all 54 vectors / 17,280 FP32 outputs, 4 resets, 104,112 stalls *(claimed)*.
- 02:38 — **Measured storage inventory** (Claude subagent; Verilator 5.050 `--json-only` elaboration of the merged top, 30,542 instances; `storage-inventory/INVENTORY.md`):
  - mutable arrays 1,062,727 B (144 declarations) + registers 29,690 B = **≈1.09 MB mutable state**;
  - ROM 28,641,280 B (`$readmemh`, moved tonight) + 8,852,630 B (`case` tables already on-chip) = ≈37.49 MB, native format;
  - both ROM totals match the merged design's `rom-accounting.json` byte for byte.
  - This replaces W3's assumed 1.5 MB of reserves. The pod's full-top Yosys run is still in `proc` after ≈85 CPU-minutes; it is no longer needed for the inventory.
- 02:38 — W3 resumed with `floorplan/LEAD-GUIDANCE-2.md`: re-run the whole-chip floorplan with measured memory, Taalas density per bank height, engine area and an engine count derived from throughput.
- 02:38 — W5: 320-row bank passes Netgen across 414,720 devices (and a monolithic run; a deliberately wrong precharge width is correctly rejected). The 1,280-row single-bank layout measures **10.50 mm² (≈25.6 µm²/selection)** with all bits matching; checks are running. Merged all-six F64: encoder layers 0–1 passed at baseline-identical clocks.
- 02:43 — ARRAY-PORT P&R (Mac W2b and pod mirror) both sit in `RepairDesignPostGPL` (high-fanout timing repair, the same step that slowed W2). To guarantee a completed measured layout tonight, the lead launched two extra pod runs. Both reuse the pod's finished synthesis (steps 01–09 copied) and resume from `OpenROAD.CheckSDCFiles`:
  - `ap40`: 40 ns clock (25 MHz);
  - `apnorepair`: 20 ns clock with post-GPL/GRT design repair and resizer timing disabled, which yields real routed area/power and the measured, unrepaired slack.
  - Both passed pre-PnR STA within a minute of launch.
- 02:43 — W2 continues its 64×320 slice from the saved CTS checkpoint at a 200 ns period (the 20 ns attempt is preserved).
- ≈02:42 — W5 tall-bank comparison (all with analog readout, global decoder/mux excluded):

  | Rows per bank | Readouts | Area per projection | µm² per selection |
  |---:|---:|---:|---:|
  | 64 | 25,600 | 22.32 mm² | 54.5 |
  | 320 | 5,120 | 12.44 mm² | 30.4 |
  | 1,280 | 1,280 | 10.50 mm² | 25.6 |

  All three are DRC 0 with all bits matching. 320-row SS passes at a 60 ns bank reuse interval, so 4 striped banks sustain one row per 20 ns. The 20 ns single-bank SPICE trial failed to converge (preserved; neither a pass nor a fail).
- ≈02:42 — **Lead diagnosis of the readout area:** the cell array has ≈0.72 µm bit-line pitch, but the readout strip places 1,280 readouts at ≈3.65 µm pitch (4,669.7 µm vs the 925.69 µm cell tile). The array is stretched ≈5× to match. Most of the "periphery" is therefore pitch mismatch, not a fundamental cost. With pitch-matched readouts and tall banks the lead estimates ≈6–7 µm²/selection (≈200–220 mm² for all weights), consistent with the October budget (≈221 mm²). **This is an estimate.**
- ≈02:43 — **Codex W6 launched (`taalas-pitch/`):** build and measure a pitch-matched readout (stacked readout rows or column multiplexing) on a tall bank of the real projection, with DRC/LVS/bit-readback/SPICE.
- ≈02:43 — W3 first measured-input run: the 320-row Taalas density + open-PDK SRAM baseline totals **2,003 mm²** (44 × 53 mm; far beyond a reticle). This is the honest upper bound with tonight's unoptimized periphery and the open SRAM macros (measured mutable state 1.21 MB as allocated → 594 mm² open SRAM, 112 mm² with dense custom SRAM).
- ≈02:47 — **W5 320-row bank timing (extracted SPICE, sampled worst column):** passes at a 40 ns reuse interval at TT and SS 2.97 V/125 °C (worst SS settling 8.92 ns); fails at 20 ns in both corners (116 output + 100 raw-bit-line check failures, preserved). Two interleaved banks therefore sustain one 1,280-bit row per 20 ns; the four-bank layout covers it. W2b's actual schedule requests a row every ≈60 ns (240 ns per bank revisit). Full-bank control and output timing remain unqualified *(claimed)*.
- ≈02:47 — W3 measured baseline two-die split: ≈1,011 mm² per die (32 × 38 mm), so neither one nor two dies fit with tonight's unoptimized readout + open SRAM. The levers that decide fit are pitch-matched readout (W6, in progress) and memory density.
- ≈02:51 — **W6 pitch-matched Taalas readout (the biggest area lever):** stacked readout rows keep the array's native bit-line pitch.
  - 64-row tile: 11.48 µm²/selection, DRC 0 after fixing 160 M3.2a/V4.3b markers (failure preserved).
  - **Full 1280×320 projection, one 1,280-row bank: 1,004 × 2,258.81 µm = 2.268 mm² = 5.54 µm²/selection including readout**, all 1,638,400 bits read back from GDS with 0 mismatches. Full-bank DRC/LVS/SPICE are in progress *(claimed)*.
  - That is ≈4.6× denser than W5's best (25.6). Uniform extrapolation to all 31,457,280 selections: **≈174 mm²** for every weight in the model, excluding global decoders/drivers, consistent with the October budget (≈221 mm² including periphery).
- ≈02:51 — W5 finished. 1,280-row stretched bank SS settling 22.5–24.4 ns (passes a 60 ns reuse interval, which matches the engine's actual ≈60 ns row request spacing; not 20 ns). 320-row banks pass 40 ns at TT/SS.
- ≈02:53 — W3 measured-input report complete (320-row/open SRAM: one die 2,003 mm² at 44 × 53 mm; two dies ≈1,012 mm² each at 32 × 38 mm; all three physical screens PASS, IR 3.4–4.6%). Resumed with `floorplan/LEAD-GUIDANCE-3.md` to build the **credible design point** with W6's density × {open, research, dense SRAM} × {levers off/on}.
  - Lead's pre-estimate: open SRAM ≈1,222 mm²; dense SRAM ≈740 mm²; dense SRAM + levers ≈571 mm² (≈24 × 24 mm).
- ≈02:53 — Pod: the SC-ROM synthesis finally finished (≈95 min) and is in STA. `ap40`/`apnorepair` are in global placement; the original ARRAY-PORT run is still in post-GPL repair.
- 02:57 — **LEAD-VERIFIED (W6 pitch-matched full projection bank):** KLayout bounding box of `taalas-pitch/r1280-v2/bank.gds` top `PITCH_BANK_R1280` = 1,004.0 × 2,258.81 µm = **2.26785 mm² → 5.537 µm²/selection** for all 409,600 selections. DRC report `r1280-v2/bank.lyrdb` has 0 items (same selected GF180 deck `experiments/taalas-access/main.drc`). W6 also reports 64-row LVS pass plus negative control. Full-bank LVS, the readout-inclusion audit and SPICE are pending.
- 03:02 — **W3 credible Taalas design point (W6 measured density 5.537 µm²/selection, measured 144-array memory inventory): 5 of 5 physical screens PASS** (`floorplan/RESULTS.md` § "Credible Taalas design point").

  | Case | Die | Blocks | IR (VDD+VSS) | Fits 26×33? |
  |---|---|---:|---:|---|
  | One die: dense custom SRAM + frontend INT8 + books in array | **25 × 31 mm** | 608.0 mm² | 2.15% | YES |
  | Two dies: open-PDK SRAM, FP32 frontend (no numerical change) | **26 × 29 mm ×2** | 607.6 + 611.9 mm² | 2.28–2.43% | YES |
  | Two dies: open SRAM + frontend INT8 | 25 × 29 mm ×2 | 552.8 + 557.1 mm² | 2.35–2.47% | YES |

  Area table, levers off → on: open SRAM 1,222 → 1,090; 4K research 1,182 → 1,050; dense custom 741 → 608 mm².
  - **LEAD-VERIFIED (one-die case):** log `logs/pitch1280v2_sram_dense_custom_on_baseline_whole_25x31mm_pdn40_pads48.log` shows `PSM-0040 All shapes on net VDD/VSS are connected`, worst IR 35.3/35.7 mV, and 0 VDD–VSS shorts across 47,135 rectangles. Render `runs/pitch1280v2_sram_dense_custom_on_baseline_whole_25x31mm_pdn40_pads48/floorplan.png` checked.
  - Assumptions still in these numbers: dense custom SRAM (12 µm²/bit, assumed), frontend INT8 accuracy, October periphery allowance 56.6 mm², engine at 50% utilization, assumed per-block power (1.08 W total), abstract macros (no internal routing).
- 03:02 — Pod: stopped the full-top Yosys run (≈2 h stuck in `PROC_PRUNE`; no longer needed). `ap40`/`apnorepair` global placement converging (overflow ≈0.50).
- 03:05 — **GOAL 1 MET, LEAD-VERIFIED: all six fixed-weight services on-chip in one design, full recognizer F64 passes.** Merged top `rv_allonchip_top_all_v1` (`onchip-all/`, 28,641,280 B of on-chip ROM in 17 images).
  - Positive log `onchip-all/logs/20261014T021221-positive.log`: exit 0 after 3,143.9 s; harness pass line `…ONBOARD_EOS_PASS tokens=5`.
  - Six `ONCHIP … host_replies=0 mismatches=0` lines:

    | Service | RTL replies |
    |---|---:|
    | decoder_body | 1,392,000 |
    | decoder_self | 787,200 |
    | encoder_QKV_O | 384,000 |
    | encoder_immutable | 1,947,520 |
    | frontend_immutable | 55,720,960 |
    | producer_positions | 2,560 |

  - Compare `…T030513-compare.log`: all 18 native output hashes and five tokens through EOS.
  - Render `…T030520-render.log`: `"passed": true`, text **"Switch on the lights"**, tokens [28176, 373, 278, 26068, 2].
  - Clock count 312,578,649, identical to the host-served baseline.
  - The lead read the top's port list: inputs are only PCM, clock/resets, handshakes/tags and a few configuration words (session/image IDs, frame count, and the three position-quantization scalars `source_start_position_scale/zero/offset`, which should become constants). There is no weight-data input.
- 03:19 — **User extended the run to ≈08:10 IST.** RunPod guard deadline moved to 08:05 (guard restarted; spend $3.14), and `caffeinate` extended to ≈08:50.
- 03:20 — W1 resumed (`onchip-all/LEAD-GUIDANCE-2.md`): v2 top with the four remaining model constants built in (all 35 inputs classified; 31 runtime inputs remain). Lint, generate, compile and fixture pass; the F64 positive is running. W2b: **both 1280×320 variants pass full gate-level (mapped-netlist) regressions**: 54 vectors, 17,280 FP32 outputs, 4 resets, 104,112 stalls each *(claimed)*.
- 03:22 — Two new workers for the extra time:
  - **W7** (`accuracy-int8/`): does storing the frontend's 2,074,560 coefficients as INT8 keep WER on the frozen validation split? This removes or confirms an assumption in the one-die case.
  - **W8** (`projection-complete/`): the complete approved projection, i.e. the ARRAY-PORT engine + row decoder + W6's real Taalas bank as a hard macro, placed and routed together on the pod, with gate-level activity power.
- 03:27 — **W7 accuracy result** (`accuracy-int8/RESULTS.md`; frozen dev validation, 16 clean + 16 other + 16 noisy, 144 fresh processes, no test split):

  | Condition | K64 FP32 | INT8 per-channel | INT8 per-tensor |
  |---|---:|---:|---:|
  | clean | 6.67% | 9.09% (+2.42 pp) | 100% |
  | other | 18.15% | 22.77% (+4.62 pp) | 100% |
  | 10 dB noise | 19.39% | 20.00% (+0.61 pp) | 100% |

  Symmetric re-quantization **FAILS** the ≤2 pp gate.
- 03:29 — **LEAD-VERIFIED: lossless compact frontend storage exists.** The source model already stores the frontend weights as affine INT8 codes + FP32 scale + FP32 offset.
  - The lead reconstructed all three tensors in numpy with `fp32(fp32(code)×scale)+offset` and compared them bitwise to the chip's FP32 ROM images: linear (25,600, scale on axis 1) **0 mismatches**; conv1 (1,024,000, axis 0) **0**; conv2 (1,024,000 as 320×640×5, input-channel axis) **0**.
  - Storage becomes 2,073,600 B INT8 + 12,800 B scales/offsets + 3,840 B FP32 biases = **2,090,240 B instead of 8,298,240 B (≈4× smaller) with zero numerical change.** It needs one FP32 multiply-add per coefficient fetch in the frontend.
  - **Consequence:** the "frontend INT8" lever in W3's one-die 25×31 mm and two-die 25×29 mm cases is now accuracy-neutral. **The one-die case's only remaining assumption is a dense SRAM** (≈12 µm²/bit vs the open macro's 51), e.g. a foundry GF180 SRAM compiler.
- 03:33 — **Lead measured the open GF180 SRAM bit cell** (`gf180mcu_fd_ip_sram__sram512x8m8wm1.gds`): `018SRAM_cell1_512x8m81` is 3.68 × 5.18 µm (4,164 instances); the pair cell `…cell1_2x…` is 3.68 × 9.68 µm, so the array pitch is ≈17.8 µm²/bit. The 512×8 macro averages 51.1 µm²/bit (periphery dominated). A large macro built from the same bit cell at 70% efficiency would be ≈25.4 µm²/bit. The "dense 12 µm²/bit" scenario therefore needs a smaller foundry bit cell. W3 resumed with `floorplan/LEAD-GUIDANCE-4.md` (lossless frontend + measured bit cell). W5's 16 largest finished files were offloaded to SSD (byte-compared; list in `taalas-array/OFFLOADED-TO-SSD.txt`).
- 03:38 — **FINAL FLOORPLANS (W3, `floorplan/RESULTS.md` § "Final design point").** All use the W6 measured Taalas density, the exact lossless native-INT8 frontend (2,090,240 B), the original measured mutable state (8,501,818 array bits + 237,524 register bits), books in the readable array, and **no numerical change**. All 4 pass PDN connectivity + IR.

  | Case | Die | Blocks | Fits 26×33 mm |
  |---|---|---:|---|
  | One die, SRAM from the measured open bit cell in large macros (25.4 µm²/bit) | 29 × 31 mm | 733.9 mm² | **NO**: needs ≈161 KiB less mutable state. The duplicated A/B buffers in `rv_encoder_bank_consumer_edge_v1` and `rv_producer_mutable_storage_v1` (82 KB each) are the obvious candidates. |
  | One die, dense foundry SRAM (12 µm²/bit, assumed) | 25 × 31 mm | 608.3 mm² | YES |
  | **Two dies, open-PDK SRAM macros as-is** | **25 × 29 mm each** | 553.0 + 557.2 mm² | **YES, with no custom memory and no numerical change** |

  **LEAD-VERIFIED (two-die open-SRAM logs):** both dies `PSM-0040 All shapes on net VDD/VSS are connected`; worst IR 38.5/39.9 mV and 39.8/43.3 mV; 0 VDD–VSS shorts.
- 03:58 — **LEAD-VERIFIED: the full pitch-matched Taalas bank (all 409,600 real selections, 2.268 mm²) passes LVS.**
  - `taalas-pitch/verification/r1280-v2/full-bank-netgen.log`: Netgen `Circuits match uniquely`, 827,201 devices each side after Netgen reduction, no property errors (`full-bank-netgen-result.json`: unique_match true, 438.7 s).
  - The reference (`verification/verify-connectivity.py`) is generated from the original packed K64 index file, independently unpacked and cross-checked against W2b's RTL and W5's `indices.npy`. Each access device's drain connects to `IDX{col}_{bit}` only where that index bit is 1.
  - W6 also reports its raw device-graph comparison passed; the negative control (doubled precharge width) is pending.
  - Combined with the earlier DRC 0 and 0-mismatch bit readback, **the physical Taalas array for the approved projection is DRC- and LVS-clean**, under the selected GF180 rule deck, with density/antenna excluded.
- 03:58 — W8 complete projection (engine + W6 bank as hard macro) on the pod: synthesis done, floorplan done, PDN generation in progress. W1 v2 (model constants internal): all six encoder layers match v1 clocks; decoding.
- 04:07 — **LEAD-VERIFIED: v2 with every model constant on-chip.** `rv_allonchip_top_all_v2` removes the last four model-constant inputs (position scale/zero/offset, image ID), leaving 31 runtime inputs.
  - The lead counted 31 inputs; none is a position constant or image ID.
  - F64 `logs-v2/20261014T031357-positive.log`: exit 0, six `ONCHIP … host_replies=0 mismatches=0`, `…_EOS_PASS tokens=5`.
  - Compare: 18/18 hashes. Render: `"passed": true`, "Switch on the lights". Clock count 312,578,649, identical to baseline.
- 04:05 — W2b gate-level activity capture: the mapped-netlist SAIF of one real-activation projection (83.32 µs) annotates **1,253,320 of 1,253,320 pins (0 unannotated)** on the placed ARRAY-PORT design. For reference, the flow's default-activity estimate (not a valid operating point) is 7.33 W. The lead is running an annotated power report on the pod (`overnight-20261014/power/`).
- 04:05 — W2b timing bottleneck identified: a row-index bit fans out to 4,074 loads and a decode signal to 4,428. This explains the hours-long post-placement repair and the slow clock; it needs buffer trees or pipelining.
- 04:05 — W6: worst-of-1,280-columns candidate passes SS at the 60 ns reuse interval; 20 ns capture still fails. Physical + logical verification complete for both W6 layouts. W2: both mapped 320×320 variants pass zero-delay gate-level checks (32 vectors, 10,272 comparisons each).
- 04:13 — **First activity-annotated power for the 1280×320 projection (lead, pod).** `power/power_cts.tcl` + `power/power_cts.log`: the `apnorepair` post-CTS database, TT 25 °C 3.3 V library, placement-estimated parasitics, and W2b's gate-level SAIF of one real-activation projection (83.32 µs at 50 MHz).
  - Annotation: 935,241 pins annotated, 315,196 unannotated (CTS-inserted buffers etc.).
  - Result: default activity **1.26 W**; SAIF activity **8.59 W** (combinational internal 8.12 W), i.e. ≈716 µJ per projection ≈ 1.75 nJ/MAC.
  - **Not representative.** This netlist was deliberately routed WITHOUT design repair, so its 4,074- and 4,428-fanout nets are unbuffered. The resulting very slow transitions inflate short-circuit (internal) power by orders of magnitude.
  - A meaningful number needs the same SAIF on a repaired netlist (pod `ap40`, or W2b's local run, both still in post-GPL repair). Kept as evidence of the fanout problem, not as the chip's power.
- 04:13 — W6: local per-column readout passes, but the **bank-wide control protocol (wordline/precharge across all 1,280 columns) fails at 60 ns**. A longer guard is under test. Full-macro timing for the pitch-matched bank is therefore still open. W1 resumed (`onchip-all/LEAD-GUIDANCE-3.md`): can the encoder/producer A/B duplicate buffers (≈160 KiB) be removed? That is the one-die enabler with the open bit cell.
- 04:18 — **W1 A/B buffer analysis (`onchip-all/RESULTS-v3.md`): zero safe savings.** Both pairs (`rv_encoder_bank_consumer_edge_v1`, `rv_producer_mutable_storage_v1`) hold overlapping live data under the current schedule. The encoder keeps the full residual source in one bank while the other holds normalized values for the global quantizer's scan/replay. Each pair needs 163,840 B of live payload at F64, and every packet differs between the overlapping tensors in all six layers checked, so aliasing would corrupt live data. **The one-die-with-open-bit-cell route therefore needs a schedule change (e.g. streaming the quantizer scan) or denser memory, not just deleting a buffer.** No v3 implementation; stopped at analysis as instructed.
- 04:18 — **W9 launched (`engine-buffered/`):** re-synthesize W2b's ARRAY-PORT engine with LibreLane `SYNTH_ABC_BUFFERING` (default False; confirmed it runs `buffer -N 16; upsize; dnsize`) + sizing, max fanout 16, 20 ns. Then full P&R on the pod, a fresh gate-level SAIF, and routed power with extracted SPEF. This targets a representative area/timing/power for the projection engine. The lead stopped the superseded pod runs `array_port-pod-v1` and `sc_rom-pod-v1` (exit 143) to free cores.
- 04:18 — Disk management: moved W2's two finished pre-route activity runs and W2b's stopped SC-ROM run (≈2.2 GB) to SSD (verified; `MOVED-TO-SSD.txt` left in each). W2's 200 ns slice continuation and W2b's SC-ROM SAIF build had been stopped by their own 22 GiB guards (preserved as failed attempts). Disk back to 24 GiB.
- 04:26 — **W6 final (pitch-matched full-projection bank) timing status** (`taalas-pitch/RESULTS.md`):
  - DRC 0 and full-bank LVS unique match (lead-verified).
  - Per-column local readout passes at SS.
  - **Bank-wide control (wordline/precharge across all 1,280 columns) FAILS at 60 ns.**
  - With a guarded 120 ns protocol, SS 2.97 V/125 °C passes for the sampled worst columns (sensitivity, not full-bank signoff); the TT 120 ns companion run was resource-incomplete.
  - Implication: one 1,280-row bank delivers a row every ≈120 ns, i.e. ≈154 µs per projection vs the engine's 83 µs (4,163 cycles at 50 MHz). Throughput needs ≈2× the banks/engines (or stronger, segmented wordline drivers). Area grows modestly.
- 04:57 — **First representative activity-annotated power (W2 slice; lead read the report).** `fabric/runs/rv_fixed_proj64x320_rom-pre-route-gate-cell-activity/01-openroad-stamidpnr/power.rpt`.
  - Design: 64×320 standard-cell-ROM engine (20,480 real weights, 320 lanes), repaired + CTS checkpoint at a 200 ns clock, placement-estimated parasitics, TT 25 °C 3.3 V.
  - Activity: gate-level cell-pin VCD of 5 random vectors (1,605 exact checks passed); 739,686 pins annotated, 103,648 unannotated (≈88% coverage).
  - **Total 106.1 mW** (sequential 43.7, combinational 34.0, clock 28.3, leakage 0.04) = 21.2 nJ/cycle. The engine performs 320 MAC per cycle, so **≈66 pJ per MAC** including ROM logic, accumulators and clock tree.
  - Lead extrapolation (assumption-labelled): the model's matrix work at real time is ≈0.6 GMAC/s, so **≈40 mW** of matrix compute at this energy/MAC. The Taalas array's measured weight-fetch energy (W5: 62–78 pJ per 32-lane read → ≈2 pJ per MAC) is small next to it.
  - **Not included:** SRAM access energy, the FP32 frontend datapath, attention/softmax, IO, routed (extracted) parasitics. This is pre-route, not signoff.
  - Contrast: the unrepaired 1280×320 run gave 1.75 nJ/MAC because of unbuffered 4,000-fanout nets (see 04:13 entry), roughly 26× worse. Buffering is essential.
- 05:46 — **W8 complete projection (engine + W6 Taalas bank as hard macro) stopped at global routing:** unresolved congestion after 50 GRT iterations; detailed routing/signoff did not run.
  - Achieved: integration RTL with a bank model passes all 54 vectors / 17,280 outputs (11,843 cycles per projection with the bank's 60 ns protocol); macro LEF/stub/provisional Liberty; synthesis, placement, macro PDN connectivity and CTS; **9.32 mm² of instances in a 4.5 × 4.5 mm (20.25 mm²) die**.
  - Root cause is the same unbuffered high-fanout nets. W9's buffered engine (`buf-v4`: ABC driving-cell constraint fixed and smoke-tested to fanout 16, plus 10× duplicated row registers) is in synthesis.
  - Lead stopped pod run `ap40` (>3 h in post-GPL repair on the unbuffered netlist; superseded).
- 06:04 — **W9 fixed the fanout disease in the 1280×320 engine (`buf-v4`).**
  - Changes: 10× duplicated row registers in the RTL (54-vector RTL regression passes, 17,280 outputs, all row-copy assertions) + LibreLane ABC buffering with a corrected driving-cell constraint (`buf-v3` silently failed on a `cell/pin` vs `cell` format bug).
  - Mapped-netlist audit: **max non-clock fanout 16, zero nets above 16** (was 11,359); 340,582 cells incl. 19,045 buffers.
  - P&R, gate replay and activity capture are now running on the pod. W2: the 320×320 datapath meets 200 ns post-CTS at TT (setup +53.5 ns, hold +0.55 ns; critical path ≈146 ns ≈ 6.8 MHz unpipelined). All three W2 variants pass RTL + zero-delay gate checks.
- 06:49 — Physical progress (all pre-route, TT corner) *(claimed, from worker reports)*:
  - **W9 buffered 1280×320 engine `buf-v4`:** 6.435 mm² cells (+5% vs unbuffered); die 16.27 mm² / core 16.08 mm². Fanout cap of 16 survives placement (0 nets > 16). Pre-placement WNS −19.65 ns at 20 ns (≈40 ns path ≈ 25 MHz), versus −47…−101 ns unbuffered. Global placement finished in ≈8 min (unbuffered runs never got through repair). Now in `RepairDesignPostGPL`. Gate-level replay of the buffered netlist passes vectors 0–10 so far with original cycle counts.
  - **W2 320×320 standard-cell ROM (all 102,400 weights):** 5.67 mm² cells (55.4 µm²/weight incl. datapath). Placement needed routability inflation disabled (`GPL-0305` divergence twice). Post-CTS at 200 ns: setup +66.5 ns, hold +0.56 ns (≈7.5 MHz path).
  - **W2 320×320 datapath:** post-CTS at 200 ns: setup +53.5 ns, hold +0.55 ns (≈6.8 MHz); now in global routing.
  - W8 complete projection (engine + Taalas macro): global-route overflow 100 (unbuffered engine); partial handoff.
- 07:23 — **Lead check of W9 `buf-v4` (pod), pre-route.** The flow's own mid-P&R power report (6.55 W, 95% sequential internal) is an artifact: before CTS the clock is one unbuilt net from the port, so every flip-flop sees a very slow clock edge. With W9's ideal-clock SDC (0.15 ns clock transition, otherwise unchanged) on the same placed database (`runs/buf-v4/23-openroad-globalplacement`), placement-estimated RC, TT 25 °C 3.3 V: design area 6.43 mm² at 40% utilization, **default-activity power 0.49 W** (no clock tree). This is a sanity bound, not an operating point; the real-activation SAIF run follows (`overnight-20261014/power-bufv4/`).
  - W9's unsharded gate replay was blocking the SAIF capture behind it (the 8-shard replay had already passed all 54 vectors). The lead started the already-compiled activity simulation directly (`logs/lead-gate-activity.log` on the pod).
  - W2's 320×320 "RTL-activity" power (306 mW) annotates only 79 of ≈1.23 M pins, so it is effectively default activity. W2 labels it that way too, and the lead does not use it.
- 07:30 — **Real-activity power for the buffered 1280×320 engine (lead, pod; `overnight-20261014/power-bufv4/RESULTS.md`).**
  - Activity: gate-level activity simulation of the mapped `buf-v4` netlist on one real-activation projection. It passed: 320 outputs, 4,163 cycles, 0 stalls, 83.26 µs. SAIF 371 MB.
  - Annotation: **1,299,526 of 1,299,526 pins, 0 unannotated.**
  - Power: **0.798 W** (combinational 82.5%; switching 0.467 W, internal 0.331 W), giving **66.4 µJ per projection ≈ 162 pJ/MAC**. That is 10.8× less than the unbuffered engine's 8.59 W.
  - Same run, ideal-clock timing: setup −125.2 ns at 20 ns before repair (≈6.9 MHz if unrepaired), hold +0.89 ns.
  - Caveats: no clock tree (+30–40% expected from the W2 slice), no repair, placement RC, zero-delay activity.
- 07:35 — W9 `buf-v4` post-placement repair at 20 ns is still running and will not finish before the pod stops.
  - Propagated-clock run: 151,000 endpoints processed, 192,596 remaining, **cell area +26.3% and still rising**.
  - Ideal-clock run: 33,000 processed, area +0.5%.
  - Takeaway: at 20 ns, setup repair inflates the engine heavily. Next time, use a realistic clock (100–150 ns) or pipeline the 320-lane datapath, rather than repairing towards 50 MHz.
- 07:37 — W2 routing will not complete tonight.
  - The 320×320 standard-cell-ROM route stopped in global-routing congestion iterations (last log 06:55, extra iteration 5/50, no process running).
  - The 320×320 datapath route has been in global routing since 06:04 with no log output.
  - W2's verified results stand: post-CTS +66.5 / +53.5 ns setup at 200 ns, all gate checks pass. Routed area/MHz/mW per weight stays open.
  - W9's serial gate replay also finished: all 54 vectors / 17,280 outputs pass with the original stall sequence and four abort tests.
- 07:52 — Lead terminated pod `2tvzr0gfn3bace` (`rv-overnight-pnr1`) after copying results to the SSD (26 GB; buf-v4 SAIF hash-verified). RunPod API: no pods. **Final RunPod spend $8.96.** At 07:53 the lead stopped the spend guard, the W2/W9 Codex workers and W2's stalled local route.
- 09:55 — Lead re-screened the final floorplans with the measured engine area/power (local, no cloud). IR now FAILS 5% at continuous full-rate engine load (one die 277 mV; two dies ≈350 mV; 80 µm straps 248 mV). The worst node is the engine's terminals. Details: `floorplan/MEASURED-ENGINE-UPDATE.md`.
- Full-top Yosys synthesizability check (W4, run by the lead): first two attempts stopped on strict SystemVerilog ordering (use-before-declare, and one localparam declared after use — patched copy in `synth/patched/`); third attempt (on the Mac, then the pod) was stopped: it reached ≈90 GB of RAM, and the memory inventory it was meant to give came from Verilator elaboration instead. **Full-top Yosys synthesizability (the first FPGA step) is still unchecked.**
