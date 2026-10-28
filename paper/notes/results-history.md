# RouteVoice: results and engineering history (paper notes)

Compiled 24 Oct 2026 from repository files only. No builds or simulations were run to write this.

**Path conventions.** Every path is relative to the repo root `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/`, with these abbreviations:
- `OP` = `OVERNIGHT-PROGRESS.md`, the lead-verified log. Its "RELEASE SUMMARY" is authoritative as of Fri 23 Oct ≈06:30 IST.
- `OVN/` = `routing-voice-chip-design/overnight-20261014/`
- `FIN/` = `OVN/finish-1023/`
- `W10/` = `FIN/w10-route/`
- `SSD-RUN/` = `/Users/sanju/rvssd/` (the local run directories on the SSD link; outside git)

**Verification labels.**
- "Lead-verified": the lead re-read the tool output (rule stated in `OP` line 7).
- "Claimed": a worker report not re-checked.
- "INFERRED": my own arithmetic or reading of file timestamps. These are not stated in any source.

---

## 1. Headline results

### 1.1 Functional: full recognizer, bit-exact, with Taalas index+codebook weights

| Item | Value | Source |
|---|---|---|
| Model | Moonshine Tiny Streaming English, four-bit K64 codebook selections (4-bit index + 16-entry UINT8 book per 64×1 group) | `FIN/w11-taalas-e2e/RESULTS.md`; `routing-voice-chip-design/AGENTS.md` |
| Main clip F64 "Switch on the lights" | tokens [28176, 373, 278, 26068, 2], 18/18 output hashes, **312,578,649 clocks, delta 0 vs v2**; 27 milestone clocks and 63 non-progress console lines identical | `FIN/w11-taalas-e2e/RESULTS.md`, `results.json` |
| Extra clips | "Plant present." (wispr-031-seg1): 18/18 hashes, 309,272,913 clocks. "Seasonable." (software-1919-142785-0022-seg0): 18/18, 308,976,820 clocks | `FIN/w11-taalas-e2e/RESULTS.md` §Consolidated corpus |
| Weight storage, new services | 28,641,280 B → **17,497,600 B** (saves 11,143,680 B, 38.91%) | same; `results.json` `storage.total` |
| Storage breakdown | 78,970,880 index bits (9,871,360 B) + 4,935,680 B books + 2,073,600 B affine INT8 frontend + 616,960 B metadata | `FIN/w11-taalas-e2e/results.json` |
| Round-trip check | 0 mismatches over all 28,641,280 original bytes | same |
| Exhaustive responder RTL tests | 565,960 encoder/decoder packets + 2,074,560 frontend packets + 163,840 position packets | `FIN/w11-taalas-e2e/RESULTS.md` |
| Stage wall times (Mac) | lint 34.5 s, generate 74.6 s, compile 260.6 s, positive **4,047 s** (includes resource suspensions) | same |
| Earlier milestone, v1/v2 all-on-chip (byte ROMs) | all 6 services on-chip, 28,641,280 B in 17 images, `host_replies=0`, same 312,578,649 clocks; v2 has 31 runtime inputs and no weight or constant inputs | `OP` 03:05 and 04:07 entries; commits 27fc2b99d, 484c00212 |
| Lossless frontend | the source model's affine INT8 + FP32 scale/offset rebuilds all 2,073,600 FP32 coefficients bit-exactly: 8,298,240 B → 2,090,240 B. Symmetric re-quantized INT8 **fails** the WER gate (+2.42 / +4.62 / +0.61 pp) | `OP` 03:27–03:29; `OVN/accuracy-int8/RESULTS.md` |
| Corpus tally (separate, older track) | 53/83 exact original segments, 37/62 complete recordings, 27 common-clock cases; WER 18.52% (35/189 words) on 37 dev recordings, equal to the frozen graph | `routing-voice-chip-design/docs/ROUTEVOICE-V1-VERIFICATION-SNAPSHOT-2026-10-12.md` |

Scope caveat (from the source): W11 is functional index/book lookup. It does not establish array geometry, timing, power or a new connected negative suite (`FIN/w11-taalas-e2e/RESULTS.md`, `FAILURES.md`).

### 1.2 The 1280×320 projection engine: physical results per iteration

Common conditions:
- Engine-only top `rv_k64_array_port`: 409,600 four-bit selections with the index fabric outside the physical top. The bench supplies the index fabric.
- 150 ns SDC, GF180MCU-D 7-track 5LM, LibreLane.
- 54-vector bench: 17,280 FP32 outputs (`W10/OPERATOR.md`).
- Energy per projection = P × cycles × 150 ns; pJ/MAC = energy ÷ 409,600.

**Pre-route ancestors (14 Oct overnight):**

| Design | Result | Source |
|---|---|---|
| W2b ARRAY-PORT, unbuffered | 6.137 mm² cells; gate-level 54 vectors pass; 4,163 cycles/projection | `OP` 01:24, 03:20 (claimed); 01:20 SC-ROM lead-verified |
| W2b SC-ROM (indices as constant logic) | 8.255 mm² cells; 34 min synthesis | `OP` 01:52 (claimed) |
| Unrepaired `apnorepair` with SAIF | 8.59 W (≈1.75 nJ/MAC). Nets with 4,074 / 4,428 fanout; not representative | `OP` 04:13 |
| W2 64×320 slice, repaired, pre-route | 106.1 mW at 200 ns, ≈66 pJ/MAC, 88% annotated | `OP` 04:57 |
| W9 `buf-v4` (fanout ≤16) | 340,582 cells incl. 19,045 buffers; 6.435 mm² cells; die 16.27 mm²; **0.798 W at 20 ns, 66.4 µJ/projection, ≈162 pJ/MAC**; 1,299,526/1,299,526 pins annotated; no CTS; placement RC | `OP` 06:04, 07:30; `OVN/power-bufv4/RESULTS.md` |
| buf-v4 post-CTS at 150 ns | worst setup +0.05 ns over all corners | `routing-voice-chip-design/AGENTS.md`; `FIN/PAUSED-2026-10-14.md` |

**Routed iterations (21–24 Oct):**

| Metric | First route (variant C, `runs/full`, pod) | Closure ECO pass 1 (Mac) | Closure ECO pass 2 "eco2" (Mac) | Fix 2 "pipe2" (Mac) |
|---|---|---|---|---|
| RTL | `engine_local.sv` (local partials) | same | same | `engine_local_pipe2.sv` + affine pipe register |
| Cycles/projection | 4,163 | 4,163 | 4,163 | **4,165** |
| Flow settings | FP_CORE_UTIL 30 / PL 35, no post-GPL repair, CTS NDR none | + post-GRT design/timing repair, 10 antenna iterations, margin 30%, heuristic diodes | + setup margin 45 ns, buffer cap 50%, TNS 100%, 20 antenna iterations, margin 50 | eco2 settings |
| Mapped cells at synthesis | 356,524; max fanout 16 | — | — | — |
| Die area | 22.74 mm² (22,738,700 µm²) | 22.74 mm² | 22.74 mm² | **22.84 mm²** (22,836,000 µm²) |
| Std-cell area / utilization | 7.54 mm² instance area at GRT, 33.5% | 12.33 mm² stdcell (incl. tap/antenna/repair), 54.8% | 12.41 mm², 55.1% | 12.20 mm², 53.9% |
| Instance count (incl. fill) | — | 1,868,271 (1,137,086 stdcell + 731,185 fill) | 1,894,271 | 1,961,063 (1,145,233 stdcell) |
| GRT overflow | **575** | (resumed from GRT state) | — | **9** |
| DRT violations, final | 0 (68,834 → 25,987 → 22,316 → 1,794 → 296 → … → 0) | 0 (9,329 → … 25 → 25 → 0) | 0 | 0 (12 → 0 in the last pass) |
| Routed wire / vias | 68.9 m / 4.29 M; 359,580 nets | 71.6 m / 5.42 M; 375,395 nets | 71.7 m / 5.53 M | 68.9 m / 5.44 M |
| Magic DRC / KLayout DRC | 0 / 0 | 0 / 0 | 0 / 0 | 0 / **0** (see note a) |
| Netgen LVS | unique match | unique match | unique match | **pending** (Magic SPICE extraction running at 02:34, 24 Oct) |
| XOR | — | — | — | 0 |
| Antenna nets / pins | **130 / 151** | 4 / 5 | 4 / 4 | **11 / 12** |
| Setup WNS nom TT | −72.94 ns | **+54.95 ns** | +56.71 ns | **+67.60 ns** |
| Setup WNS nom SS | −251.2 ns | −40.04 ns (30 endpoints) | −36.2 ns | **+21.65 ns** |
| Setup WNS max SS (worst) | −306.8 ns | −55.46 ns (31 endpoints) | −53.08 ns | **+8.34 ns** |
| Setup violations | 1,883 at TT; 3,296 at nom SS | 0 TT/FF; 30–31 at SS | 30 at SS | **0 in all 9 corners** |
| Hold worst | +0.162 ns (max FF); all pass | +0.076 ns; all pass | +0.080 ns | +0.300 ns (max FF); all pass |
| Max-slew / max-cap counts, TT | 575,101 / 25,513 | 322,109 / 27,301 | — | 389,136 / 21,432 (worst corner 902,170 / 24,383) |
| Setup-limited clock | 223 ns TT ≈ 4.48 MHz; 402 ns nom SS ≈ 2.49 MHz | ≈10.5 MHz TT; ≈5.3 / 4.9 MHz SS | ≈5.4 MHz SS | 150 ns met everywhere (6.67 MHz) |
| Routed SAIF power at 150 ns (TT, nom SPEF) | **0.158 W** (seq 25.3, comb 114, clock 18.8 mW) | **0.168 W** (comb 121, seq 26.4, clock 20.8 mW) | not measured | **0.188 W** (seq 24.3, comb 142, clock 21.5 mW) |
| Pins annotated | 1,364,228 / 32,552 not (97.7%) | 1,364,228 / 649,985 not (≈68%) | — | 1,365,355 / 656,169 not (67.5%) |
| Energy/projection; per MAC | 98.7 µJ; **241 pJ/MAC** | 104.9 µJ; **256 pJ/MAC** | — | ≈117 µJ; **≈287 pJ/MAC** |
| Default-activity power (bound only) | 0.101 W | 0.110 W | — | 0.0865 W |
| Post-layout simulation | zero-delay routed replay 54/54 vectors, identical cycles (300,952); SDF timing simulation unsupported | — | — | RTL 54/54 (301,005 cycles); gate activity run 320/320 outputs bit-exact |

Sources by column:
- **First route:** `OP` 21 Oct 10:30 and 15:51 entries; `W10/RESULTS.md`; `W10/results.json` (`variants.C`, `mapped_audit`, `physical_signoff_checks`, `signoff_audit`); `W10/routed-power-lead/RESULTS.md`, `power.log`.
- **ECO pass 1:** `W10/closure-lead/final-metrics.json`, `sta-postpnr-corners.txt`, `manufacturability.rpt`, `power-eco.log`; `OP` release summary.
- **ECO pass 2:** `W10/closure-lead/final-metrics-pass2.json`, `full-eco2-local.json`; `OP` "Biggest open items" §1.
- **pipe2:** `W10/pipe2/README.md`; `W10/pipe2/evidence/sta-postpnr-summary.rpt`, `grt-overflow.txt`, `drt-violations.txt`, `power-pipe2.log`, `activity-results.json`; die area, utilization, KLayout DRC, XOR and antenna counts from `SSD-RUN/pipe2-local/runs/pipe2/69-checker-klayoutdrc/state_out.json`.

Notes:
- (a) The pipe2 README (written 23 Oct) says "DRC, LVS and antenna results are added when signoff finishes". The KLayout DRC 0, antenna 11/12 and XOR 0 values above come from the run's own state file, read on 24 Oct ≈02:40. They are not yet in the README, and LVS had not finished.
- Fix 1 (`W10/pipe/README.md`): one elastic register before `taalas_fp32_affine`, 4,164 cycles, RTL 54/54 pass (300,964 cycles). Its flow was stopped at detailed routing, because the SS estimate showed the 320:1 select would still fail by ≈10 ns (`W10/pipe2/README.md`). It has no routed result.
- Throughput: 409,600 MAC ÷ (4,163 × 150 ns) ≈ 0.66 GMAC/s, against a real-time need of ≈0.6 GMAC/s (`OP` release summary). At the first route's 223 ns it would be ≈0.44 GMAC/s (`OP` 21 Oct 10:30).

### 1.3 Earlier global-route diagnostics (Mac, 15 Oct)

| Run | Utilization | GRT demand | Total overflow | Wirelength | Wall | Source |
|---|---|---|---|---|---|---|
| D1 (shared partials, buf-v4) | 44.8% | 136.8% | 3,374,766 | 111.6 m | 1,506 s | `FIN/CONGESTION-DIAG-2026-10-15.md` |
| D3 (lower density) | 29.9% (die 25.97 mm²) | 109.0% | 2,581,164 (−24%) | 136.5 m | 3,689 s | same |
| D4 (local partials) | 43.6% | 92.3% | **260,340 (−92%)** | 81.3 m | 2,733 s | same |
| d4-full (50 GRT iterations) | — | 99.9% | 767,380 | 96.7 m | DRT ≈1 h/iteration; 1.40 M → ≈0.57 M by iteration 7 of 64; killed | `FIN/PAUSED-2026-10-14.md` |
| Variant C (final) | 33.5% | 70.75% | **575** | 80.6 m (GRT) | — | `W10/results.json` |

### 1.4 Full-recognizer synthesis (W12, per-module, complete 22 Oct)

| Item | Value | Source |
|---|---|---|
| Scope | `rv_allonchip_top_all_v2`, ROM services as black boxes; 30,545 elaborated modules → 4,457 distinct logic units + 17 ROM macro types | `FIN/w12-synth/RESULTS.md` |
| Status | generic 4,457/4,457 pass; GF180 4,457/4,457; FPGA 4,457/4,457; top wrapper connectivity pass | same |
| Generic | **48,377,943 cells, 8,073,841 FFs**; 311 inferred memories / 8,169,778 bits mapped into flops | same |
| GF180 TT area | **1,198.30 mm²**, 19.02× the floorplan's 63 mm² logic allowance | same; `AREA-COMPARISON.md` |
| ECP5 | **30,391,157 LUT4, 1,339,678 FF, 1,247 DSP, 118 BRAM18** | same |
| Work totals (sum of per-unit stage times) | generic 7,767 s; GF180 18,313 s; FPGA 24,572 s | same |
| Weight capacity (FPGA view) | 229,130,240 bits native (≥6,216 RAMB36; 6,633 with banking); 139,980,800 bits in K64 form; all ROMs 300,019,892 bits (210,870,452 compressed). Largest ECP5 has 3,833,856 BRAM bits, so the weights cannot fit | `FIN/w12-synth/FPGA-CAPACITY.md` |
| Intermediate state (21 Oct 19:33 IST) | complete_with_failures: 12 generic failures, 6 FPGA failures; 430.7 mm² partial | `FIN/w12-synth/RESULTS-pod-20261021.md` |

### 1.5 Whole-chip pieces (W13/W14/W15) and floorplan

| Item | Value | Source |
|---|---|---|
| Single pitch-matched Taalas bank (W6, 14 Oct) | 1,004 × 2,258.81 µm = 2.268 mm² = **5.537 µm²/selection incl. readout**; DRC 0; full-bank Netgen unique match, 827,201 devices, 438.7 s | `OP` 02:57, 03:58 |
| W13, all weights | 98 matrices, 31,457,280 selections (125,829,120 bits), **81 banks**, readback 81/81, DRC 0 81/81, full LVS on 6 representatives; **174.71 mm²** vs 174.17 mm² floorplan estimate; views load in OpenSTA/OpenROAD/Yosys | `FIN/w13-arrays/RESULTS.md` |
| W13 drivers | 4 control shapes: DRC 0, full LVS, 9-corner STA at 150 ns (setup +56.4…+77.2 ns); control area 56.585 mm²; capture/escape staged; full peripheral qualification pending | `FIN/w13-arrays/DRIVERS-RESULTS.md` |
| W14 | **6 READY leaf macros**: rom_position_slew_eco, source_phase_control_retry, producer_metadata_eco, decoder_learned_norm_g1, quantizer_calibrated_eco, io_token_sequencer_calibrated_eco. All fail the supplemental density check (5–7 markers; deferred to chip fill). Large blocks not hardened. SRAM bridge (160 macros, 33.5 mm² bare SRAM) and producer adapter (384 macros, 77.42 mm²) pass replay but have no physical design | `FIN/w14-blocks/RESULTS.md`, `bridge-sram/RESULTS.md` |
| W15 batch 2 | two 25 × 29 mm dies. A: 19 real banks + 1 logic macro, 60 stubs. B: 29 banks + 3 logic macros, 59 stubs. Routed nets 649/649 and 733/733; router and pre-fill top-wiring DRC 0; PG connectivity pass; **assumed-load IR FAIL** (A 0.869/0.866 V, B 1.44/1.35 V); post-fill density timed out (metal coverage <30%); full-chip LVS/STA not run | `FIN/w15-chip/RESULTS.md`, `batch-2/STATUS.md`, `batch-2/FAILURES.md` |
| Floorplan (14 Oct, abstract macros) | one die 25 × 31 mm (dense SRAM, assumed 12 µm²/bit) or two dies 25 × 29 mm (open SRAM, no numerical change); IR 2.2–2.5% at the assumed 1.08 W | `OP` 03:02, 03:38 |
| Floorplan with measured engine | at continuous 50 MHz (1.077 W) IR **fails** (277–358 mV). At the 150 ns clock (0.144 W) it passes: 77.8 / 90.1 / 85.4 mV | `OVN/floorplan/MEASURED-ENGINE-UPDATE.md`; `OP` 09:55, 20:20; commit d8abf1bf5 |

---

## 2. Engineering timeline

Dates are IST. Commit lines come from `git log --format='%ad %h %s' --date=iso`: 55 commits on `overnight-2026-10-14` since 1 Sep. The 169 Taalas checkpoint commits dated 19 Sep–5 Oct are on branch `codex/taalas-proof-checkpoint-2026-09-19` (`git log` on that branch).

| Phase | Dates | What it achieved | Evidence |
|---|---|---|---|
| Research baseline and media kit | 1 Sep | "Routing Edge AI" media kit and research baseline (3 commits) | e779fe2bc, f6129e12e, 6d6c3dabc |
| STT routing workspace + first GF180 | 6–7 Sep | snapshot of existing research; native local STT routing workspace; GF180 tile experiments; Nix OpenROAD installed; first GF180 physical smoke; proof gates documented | dcbc9680d, 593542b26, 843ca1628, 956e0a988 |
| Taalas proof experiments (Codex-driven) | 19 Sep – 5 Oct | 169 checkpoint commits. Access-cell specimens (DRC/LVS-clean); K64 quality pilot (clean 4.49% / other 13.63% / noisy 15.77% WER, software); static projection compiler over all 31,457,280 indices; common-v9 integration. Monday 5 Oct deliverable: one-die fit **unproved**; conditional bank screen 934.3 mm² vs 900 mm² budget. RunPod $8.51 of a $15 cap | branch `codex/taalas-proof-checkpoint-2026-09-19`; `routing-voice-chip-design/docs/TAALAS-MONDAY-FEASIBILITY-DELIVERABLE-2026-10-05.md` |
| RTL corpus qualification | ≈5–13 Oct | tally rose to 53/83 segments, 37/62 recordings; learned tables on-chip; 128-col × 1,280-row RC110 array electrical pass at SS 720 ns. RunPod closed at $10.8448 / $15 | `routing-voice-chip-design/STATUS.md`; `docs/ROUTEVOICE-V1-VERIFICATION-SNAPSHOT-2026-10-12.md` |
| Direction change | 13 Oct | user prioritizes measuring the fixed-weight fabric and an FPGA view over the corpus tally; 28.6 MB of weights still served by the harness | `docs/ROUTEVOICE-PROPOSED-PHYSICAL-GOAL-2026-10-13.md`; user memory note |
| **Overnight run** | 14 Oct 00:30–07:55 | W1/W1b/W1c all weights on-chip, F64 pass (03:05); v2 has every constant on-chip (04:07); W5/W6 Taalas arrays measured (5.54 µm²/selection, DRC/LVS clean); W3 floorplans with PDN/IR; W7 lossless frontend; W9 `buf-v4` fanout fix (0.80 W, 162 pJ/MAC pre-route). **No routed engine.** Pod pnr1 $8.96 | `OP` Morning Summary + log; 32 commits, 5cff7a2a4 … 90e667a65 |
| Post-overnight route attempts | 14 Oct 09:55 – 16 Oct | floorplan IR re-screen; 150 ns route attempts stalled (repair on a multi-driver net; 11 h in GRT; NDR-relax loop). D1/D3/D4 diagnostics found the broadcast-wiring fix (−92% overflow). d4-full DRT did not converge | `FIN/PAUSED-2026-10-14.md`; `FIN/CONGESTION-DIAG-2026-10-15.md`; f1d558502, d8abf1bf5 |
| Pause | 16 Oct 02:21 → 21 Oct | user paused the physical goal; all EDA killed | 30d88268f; `routing-voice-chip-design/AGENTS.md` |
| **Release push** | 21 Oct 02:25 → 23 Oct 06:30 | W10–W15 Codex workers launched. 03:45 W11 Taalas F64 pass; 04:16 W13 81 banks; 10:30 engine routed (DRT 0); 15:51 signoff (DRC/LVS clean, antenna 130/151); 22 Oct 18:36 HF backup and pod deleted; 19:28 routed power 0.158 W; 22:11 release summary; 23 Oct 06:16 closure pass 1 (TT +55 ns, SS −40 ns, antenna 4 nets, 0.168 W) | `OP` 21–23 Oct entries; b34fd98f4, aa34b01b5, 228742051, 847586f6b, 5c4c856e8, f3a38994d, bd85328ec, deae00b91 |
| **SS timing fix** | 23 Oct 06:17 → 24 Oct | closure pass 2 still fails SS on the same 30 endpoints (15:48). Fix 1 (affine register, 15:53) was judged insufficient. Fix 2 (look-ahead group registers, 18:56) routed by 23:34: **all 9 corners met**, 0.188 W, 287 pJ/MAC. KLayout DRC 0 by 02:34, 24 Oct; LVS pending | 50f11c568, 4876ff0fd, 5ae007c69, a6b679794; `W10/pipe2/README.md` |

---

## 3. Failures and fixes

Each entry gives the symptom, the root cause, the fix, and the time cost.

**F1. Unbuffered high fanout (14 Oct).**
- *Symptom:* post-GPL repair ran for hours; the unrepaired netlist drew 8.59 W; W8 stopped at GRT after 50 iterations.
- *Cause:* single nets drove 4,074–11,359 loads (row-index bits, shared products, reset), and synthesis inserted no buffers. W9's first attempt, `buf-v3`, silently failed on a `cell/pin` vs `cell` format bug.
- *Fix:* `buf-v4` uses 10× duplicated row registers plus ABC buffering with max fanout 16. Power fell 10.8× (0.798 W); global placement took ≈8 min.
- *Time cost:* the run spent ≈01:33–06:04 on repair stalls. The `ap40` run sat >3 h in post-GPL repair.
- *Sources:* `OP` 04:05, 04:13, 05:46, 06:04, 07:30.

**F2. Repair toward 20 ns inflated area.**
- *Symptom:* buf-v4 propagated-clock repair reached +26.3% area with 192,596 endpoints still left; it did not finish before the pod stopped.
- *Cause:* the 320-lane datapath is ≈145 ns deep, so 20 ns was unreachable.
- *Fix:* use a 150 ns clock. Post-CTS, buf-v4 then met timing at +0.05 ns.
- *Time cost:* the last ≈3 h of the overnight run.
- *Sources:* `OP` 07:35, 20:20; `routing-voice-chip-design/AGENTS.md`.

**F3. Post-GPL repair stalls (14 Oct and 21 Oct).**
- *Symptoms:*
  - 14 Oct: `repair_design` was stuck at 73,596 nets on a multi-driver net (`FIN/PAUSED-2026-10-14.md`).
  - 21 Oct: W10 variants A and B stalled at 151,000 nets (A: no progress for 14 min, B: 33 min). The lead killed them at 04:03 (`W10/LEAD-ACTIONS.md`).
- *Fix:* variant C skipped post-GPL repair and was the one that routed.
- *Time cost:* about 1.5 h of the pod sweep (W10 started 02:37; INFERRED from `W10/results.json` `started_utc`).

**F4. Global-route congestion: 3.37 M → 260 k → 575 overflow.**
- *Symptoms:*
  - The strict GRT run sat ≈11 h without converging (killed 15 Oct 07:52).
  - The overflow-allowed run looped through clock-NDR relaxation (GRT-0273) and would have taken days (killed 15 Oct 13:03).
- *Diagnosis (D1/D3):* overflow is global. Demand was 137% of capacity, worst on Metal3. A 1.6× bigger die cut overflow only 24% while wirelength grew 22%.
- *Root cause:* the 208-bit shared partial-product bus fed 640 selectors across the whole die.
- *Fix:* D4 adds 10 `(* keep *)` per-32-lane-group copies of the partial-product registers. It is cycle-identical on the 54-vector bench, cuts overflow 92% and wirelength 27%.
- *Remaining problem:* the full 50-iteration GRT of d4-full ended worse (767,380), and its DRT was not converging at ≈1 h/iteration (1.40 M → 0.57 M violations after 7 of 64 iterations).
- *Final fix:* lower density (FP_CORE_UTIL 30 / PL 35) with GRT_OVERFLOW_ITERS 3 and no post-GPL repair → overflow 575 → DRT 0.
- *Time cost:* ≈14 Oct 19:48 to 16 Oct (≈2 days of Mac time), then ≈8 h on the pod from W10's start to DRT 0 (02:37 → 10:30, 21 Oct).
- *Sources:* `FIN/PAUSED-2026-10-14.md`, `FIN/CONGESTION-DIAG-2026-10-15.md`, `OP` 21 Oct 10:30.

**F5. Pod OOM at the 64 GB cgroup limit.**
- *Symptom:* the W12 flattened generic synthesis was OOM-killed after 884.775 s at 32,014,648 KiB RSS (exit −9/247).
- *Cause:* `free` showed the host's 755 GB, but the container limit `memory.max` was 64,000,000,000 bytes, and concurrent jobs shared it.
- *Fix:* `FIN/POD-SCHEDULE.md` (21 Oct 05:30) requires checking `memory.current` and keeping the total below 56 GB, with a priority order. The lead also killed W15's KLayout antenna run (36 GB RSS) at 07:02 to protect the engine DRT (`FIN/w15-chip/LEAD-ACTIONS.md`).
- *Time cost:* about 15 min of compute plus scheduling disruption.
- *Sources:* `FIN/w12-synth/pre-per-module-RESULTS.md`, `FIN/POD-SCHEDULE.md`.

**F6. Yosys stalls and a crash on the flattened or hierarchical full top.**
- *Symptoms:*
  - 14 Oct: on the Mac, Yosys reached ≈90 GB and pushed 24 GB into swap, because the `$readmemh` ROMs were being synthesized as logic. On the pod it stuck ≈2 h in PROC_PRUNE (`OP` 01:12, 03:02, last line).
  - 21 Oct: the hierarchical generic run sat 5 h in OPT_MEM_PRIORITY (stopped 12:03). The no-priority retry stalled in OPT_DFF for 50+ min (stopped 15:58).
  - The FPGA run segfaulted in OPT_DFF after 11,666 s (`Yosys::CellTypes::setup_type`).
  - The earlier generic run failed after 17,742 s.
- *Fix:* black-box the ROMs and run per-module synthesis (≤6 GB per process, 1 h timeout per stage). It completed 4,457/4,457 in all three phases by 22 Oct 22:10 IST.
- *Time cost:* ≈14 h of wall time on 21 Oct (INFERRED: elaborate 1,856 s + generic 17,742 s ≈ 5.4 h, plus FPGA 11,666 s ≈ 3.2 h, partly overlapping, plus the stall waits).
- *Sources:* `FIN/w12-synth/LEAD-ACTIONS.md`, `pre-per-module-RESULTS.md`, `RESULTS.md`.

**F7. SAIF parser error.**
- *Symptom:* the pod power step failed with `STA-0169 SAIF syntax error` at line 7,207,294 (`W10/RESULTS.md` "power-150ns exit 1").
- *Cause:* two Verilator-traced cell-internal `$unnamedudp1` blocks.
- *Fix:* `clean_saif.py` removes those 4 lines; the run was redone on the Mac from the HF backup.
- *Time cost:* the step failed 21 Oct; the result arrived 22 Oct 19:28, roughly a day, mostly spent waiting.
- *Source:* `W10/routed-power-lead/RESULTS.md`.

**F8. Pod disk full (21 Oct).**
- *Symptom:* the full disk stopped routed power and the post-layout sim.
- *Fix:* the lead freed 20 GB and W10 reran. The rerun replay took 41.7 min (INFERRED from `started_unix` / `ended_unix` in `W10/RESULTS.md`).
- *Mac side:* disk guards (22 GiB floor) repeatedly suspended work: W11 suspensions, W14 disk-guard stops (head mapping stopped after 633.9 s), and W15 offloads.
- *Sources:* `OP` 21 Oct 15:51; `FIN/w14-blocks/RESULTS.md`; `FIN/w11-taalas-e2e/FAILURES.md`.

**F9. Pod closure ECO stalled.**
- *Symptom:* `full-eco` on the pod logged "RepairDesignPostGRT no progress for 45 minutes" and exited −15.
- *Fix:* the lead reran closure locally on the Mac from the restored state (`W10/closure-lead/run.sh`, `--from OpenROAD.RepairDesignPostGRT`).
- *Time cost:* pass 1 took 28,668 s (7.96 h, ended 23 Oct 06:11).
- *Sources:* `W10/RESULTS.md` §Closure; `W10/closure-lead/flow-deferred-errors.txt`.

**F10. Idle pod billing and workers that claimed to still be running.**
- *Symptom:* all Codex workers had exited by 21 Oct 17:03, while claiming their jobs were "continuing". From ≈19:30 on 21 Oct, the pod's only job was a W12 `memory-gate.py fpga` wait loop: ≈21 idle hours.
- *Fix:* the pod was deleted 22 Oct 18:35 after a verified HF backup.
- *Cost:* INFERRED ≈21 h × $0.64/h ≈ $13.4 of pnr2's $25.87.
- *Source:* `OP` 22 Oct 18:36.

**F11. Pod deleted, then restored from Hugging Face.**
- *Backup:* the full 53 GB `/workspace` (105,826 files) was uploaded as 6 zstd archives to the public dataset `sanjuhs/routevoice-pod-final-20261022`. Downloading it back verified 105,827/105,827 files.
- *Restore:* the inputs were restored to the Mac. Routed power, closure and pipe runs all used these restored inputs.
- *Side failure:* the pod → SSD rsync stalled at 0.7 of 53 GB.
- *Sources:* `OP` 22 Oct 18:36; `FIN/pod-final-hf-20261022/README.md`, `hf-verify.json`.

**F12. SS setup failure, fixed by pipelining.**
- *Symptom:* closure passes 1 and 2 met TT but failed SS (−40.0 / −36.2 ns nom) on the **same 30 endpoints**. Extra repair could not fix it.
- *Cause:* every path runs from `metadata.column` through the 320:1 accumulator mux, the zero-point/metadata lookups, a correction multiply/subtract and `iNToRecFN` into the affine stage (`W10/pipe/README.md`).
  - The pre-route SS estimate was ≈72 ns too optimistic (+36.0 estimated vs −36.2 routed), because of the long wires in the die-wide select.
- *Fix 1:* an elastic register before the affine. It was predicted to still fail by ≈10 ns, so the run was stopped at DRT.
- *Fix 2:* look-ahead per-32-lane-group output registers (a 10:1 final select), a registered zero-point correction and a PREP state.
- *Result:* +2 cycles per vector; all corners met; power +12%.
- *Time cost:* pass 2 took 33,922 s (9.42 h). Fix 2 went from lint (18:56) to routed STA (23:12) in ≈4.3 h (INFERRED from directory mtimes in `SSD-RUN/pipe2-local/runs/pipe2/`).

**F13. Antenna violations.**
- *Symptom:* 130 nets / 151 pins after the first route.
- *Fix:* post-GRT antenna repair (10, then 20 iterations) with heuristic diodes brought it to 4/5 in pass 1 and 4/4 in pass 2. Pipe2 is at 11/12, still open.
- *Sources:* `W10/RESULTS.md`; `W10/closure-lead/*`; pipe2 state file.

**Smaller failures** (kept on record; full lists in `FIN/w14-blocks/FAILURES.md`, `FIN/w15-chip/batch-*/FAILURES.md`, `FIN/w13-arrays/complete-view-checks-v1-failed/`):
- W12's launcher was missing `/usr/bin/time` (exit 127).
- OPT_MERGE `std::bad_alloc` under the 6 GB cap.
- W13 checker pin-name assumption.
- W15 deck-upload directory missing; fill trial timeout; VSS PG orphan fragments; IR fail.
- A commit briefly swept the user's uncommitted files onto the overnight branch. It was undone by force-push (`OP` §Cost and housekeeping).

---

## 4. Compute, cost and time accounting

### 4.1 RunPod

| Pod | Type | Rate | Window (IST, from guard timestamps) | Recorded spend | Source |
|---|---|---|---|---|---|
| `rv-overnight-pnr1` (2tvzr0gfn3bace) | cpu3g, 32 vCPU, 128 GB | $1.28/h | 14 Oct 00:57 → 07:52 (6.92 h, INFERRED) | **$8.9562** | `OVN/runpod/spend.json`; `OP` 00:57, 07:52 |
| `rv-overnight-pnr2` (ysau1eomaqp1w5) | cpu3gx16, 16 vCPU; `free` shows 755 GB but the cgroup allows 64 GB | $0.64/h | 21 Oct 02:20 → 22 Oct 18:35 (40.26 h, INFERRED) | **$25.8653** | `OVN/runpod/spend.json`, `guard.log`; `FIN/POD-SCHEDULE.md` |
| **Total, this physical phase** | | | | **$34.8215** | `OVN/runpod/spend.json` |

- The guard cap was raised from $28 to $58 at 21 Oct 02:54 (`OVN/runpod/guard.log`). The user approved $60 (`OP` release summary).
- A 32-vCPU pod creation failed at 02:19 on 21 Oct, so a 16-vCPU pod was used instead (`guard.log`).
- Account balance after deletion: $88.13 (`OP` 22 Oct 18:36).
- Earlier, separate RunPod spend (Sep–13 Oct): $10.8448 of $15 (`routing-voice-chip-design/STATUS.md`). INFERRED project total ≈ $45.67.
- Everything after 22 Oct 18:35 (routed power, both closure passes, fix 1, fix 2) ran on the Mac at $0 cloud cost.

### 4.2 Major run wall times

| Run | Where | Wall time | Source |
|---|---|---|---|
| Full-recognizer F64 RTL sim (Verilator) | Mac | 3,131.95 s (12 Oct); 3,414.9 s (W1); 3,451 s (W1b); 3,143.9 s (merged v1); 4,047 s (W11 v4, includes suspensions) | snapshot doc; `OP` 02:01, 02:10, 03:05; W11 RESULTS |
| W2b SC-ROM 1280×320 synthesis | Mac / pod | 34 min / ≈95 min | `OP` 01:52, 02:53 |
| W6 full-bank LVS (827,201 devices) | Mac | 438.7 s | `OP` 03:58 |
| D1 / D3 / D4 GRT diagnostics (6 threads) | Mac | 25 / 61 / 45.6 min | `FIN/CONGESTION-DIAG-2026-10-15.md` |
| Strict 150 ns GRT (lead-150ns-cts) | Mac | ≈11 h, no convergence | `FIN/PAUSED-2026-10-14.md` |
| d4-full DRT | Mac | ≈1 h per iteration; 7 of 64 iterations done | same |
| W10 synthesis (356,524 cells) | pod | done 02:45 IST, 21 Oct; W10 had started 02:37 | `W10/OPERATOR.md`; `W10/results.json` |
| W10 launch → DRT 0 (variant C) | pod, 12 CPUs | ≈8 h (02:37 → 10:30) | INFERRED from `results.json` and `OP` 10:30 |
| W10 routed → signoff checks | pod | ≈5.3 h (10:30 → 15:51) | INFERRED from `OP` |
| Routed zero-delay replay, 54 vectors | pod, 3 jobs | 41.7 min | INFERRED, `W10/RESULTS.md` unix times |
| Closure pass 1 (post-GRT → signoff) | Mac, 12 jobs | 28,668 s = 7.96 h. DRT 1 h 26 m; KLayout DRC ≈2.0 h (03:23 → 05:25); LVS ≈45 min | `W10/closure-lead/flow-deferred-errors.txt`; `OP`; INFERRED from `SSD-RUN/eco-local/runs/eco/` mtimes |
| Closure pass 2 | Mac | 33,922 s = 9.42 h. DRT ≈2.9 h; KLayout DRC ≈2.0 h | `flow-deferred-errors-pass2.txt`; INFERRED from `eco2/` mtimes |
| pipe2 full flow | Mac | synthesis ≈8 min; GPL ≈5 min; post-GRT repair ≈40 min; antenna repair ≈56 min; DRT ≈1 h 11 m (README: ≈1 h 15 m); RCX + STA ≈25 min; lint → STA ≈4.3 h; KLayout DRC ≈2.1 h; LVS still running after 7.6 h total | INFERRED from `SSD-RUN/pipe2-local/runs/pipe2/` mtimes; `W10/pipe2/README.md` |
| W12 per-module synthesis | pod (4 CPUs, 2 workers) | work totals: generic 7,767 s, GF180 18,313 s, FPGA 24,572 s | `FIN/w12-synth/RESULTS.md` |
| HF backup of 53 GB | pod | completed and verified by 22 Oct 18:36 | `OP` |

**Mac.** The hardware spec is not stated in the repo. `sysctl`, read on 24 Oct, reports an Apple M4 Pro, 14 cores, 48 GiB RAM and a 460 GiB internal disk (≈25 GiB free at the time). The project enforces a 20–22 GiB free-disk floor (`OP` 01:05; W11/W14/W15 guards). The 14 Oct Yosys run pushed the Mac into 24 GB of swap (`OP` 01:12).

### 4.3 Agent usage

- **Lead:** Claude (Opus 5.5). **Workers:** Codex CLI (`codex exec`), "GPT Astra, high reasoning", one Terminal tab each, plus Claude subagents (`OP` lines 3, 220; `OVN/run-codex.sh`).
- **14 Oct workers:** W1, W1b, W1c (on-chip ROMs), W2/W2b (fabric), W3 (floorplan), W5/W6 (Taalas arrays), W7 (INT8 accuracy), W8 (complete projection), W9 (buffered engine). The storage inventory was done by a Claude subagent (`OP` log).
- **21–23 Oct workers:** W10 (route), W11 (Taalas e2e), W12 (synthesis), W13 (arrays), W14 (blocks), W15 (chip). Briefs: `FIN/BRIEF-codex-W1[0-5].md`.
- **Quota:** Codex sessions were paused at 21 Oct 03:07 with "Codex usage at 78%" (`FIN/PAUSED-CODEX-SESSIONS.md`). All workers had exited by 21 Oct 17:03 (`OP`).
- **Lead-only work after that:** the routed-power fix, both closure passes, fix 1 and fix 2 (`W10/routed-power-lead/`, `closure-lead/`, `pipe/`, `pipe2/`).
- **Not found in the repo:** no token or dollar accounting for Claude or Codex usage.

---

## 5. Lessons for a faster, cheaper flow

1. **Run a short diagnostic route before any full route.**
   - The 3-iteration GRT diagnostics took 25–61 min and identified the problem.
   - The full attempts burned ≈11 h in GRT, days in NDR relaxation, and ≈1 h per DRT iteration without converging (`FIN/CONGESTION-DIAG-2026-10-15.md`, `FIN/PAUSED-2026-10-14.md`).
   - Gate full routes on GRT overflow from the diagnostic: 575 routed in hours; 260 k never did.
2. **Fix wiring structure in RTL, not with die area.**
   - 1.6× the area gave −24% overflow; local register copies gave −92% at the same area (`CONGESTION-DIAG`).
   - Likewise, two closure passes moved SS by only 4 ns, while one RTL pipeline change moved it ≈58 ns (−36.2 → +21.6) and cut GRT overflow 575 → 9 (`W10/pipe2/README.md`).
   - When the same endpoints fail after repair, stop repairing and pipeline.
3. **Pick a reachable clock early.** Repair toward 20 ns grew area by 26% and never finished, while 150 ns closed post-CTS (`OP` 07:35; AGENTS.md).
4. **Audit fanout at synthesis.** Fanout ≤16 cut power 10.8× and made placement take minutes (`OP` 06:04, 07:30). The mapped-netlist audit (`W10/results.json` `mapped_audit`) is cheap.
5. **Do not trust pre-route SS estimates on die-spanning nets.** They were optimistic by ≈72 ns (`W10/pipe2/README.md`). Keep ≥40% margin, or check SS after GRT with estimated parasitics, before committing to a full run.
6. **Signoff dominates wall time.**
   - In every Mac run, KLayout DRC took ≈2 h, versus 1–3 h for DRT (INFERRED from mtimes).
   - Pipe2's LVS was still running >2 h after DRC.
   - Run signoff only on candidates that already meet STA (fix 1 was correctly stopped at DRT), and consider KLayout deep or tiled mode with more threads (`full-eco2-local.json` uses 3 threads).
7. **Most engine work fits on the Mac at $0.** The engine flows (4–9.5 h each) all ran locally. The pod's big RAM was mostly an illusion: a 64 GB cgroup (`POD-SCHEDULE.md`). W12 finally succeeded with ≤6 GB per-module processes. INFERRED: the per-module approach could have run locally with the ROMs black-boxed.
8. **Bill only for active compute.**
   - ≈21 idle pod hours (≈$13.4, INFERRED) came from a wait loop after the workers exited (`OP` 22 Oct).
   - An idle-CPU auto-stop in the guard, and verifying worker process state rather than worker claims, would have saved about half of pnr2's spend.
9. **Verified external backups enable fearless teardown.** The HF backup let the pod be deleted at 18:35, and routed power arrived at 19:28 from the restored inputs (`OP`; commit f3a38994d).
10. **Check tool-format compatibility early.** The OpenSTA SAIF error (Verilator UDP blocks) and the `buf-v3` driving-cell format bug each cost a cycle of runs (`routed-power-lead/RESULTS.md`; `OP` 06:04).
11. **Separate synthesis memory from simulation-oriented RTL.** Black-box `$readmemh` ROMs before Yosys; otherwise elaboration hits ≈90 GB (`OP` 01:12; W12 brief).
12. **Disk floors throttled parallel workers on the 460 GiB Mac.** Repeated suspensions (W11, W14, W15) suggest provisioning a dedicated scratch volume for active EDA. The user's storage rule keeps active runs on the internal disk (AGENTS.md).

---

## 6. Conflicting, superseded or unverified numbers

| # | Issue | Paths |
|---|---|---|
| 1 | The release summary says "SS fails" (nom −40.0, max −55.5 ns). **Superseded** by pipe2 (all corners met). The memory note "Engine setup timing ≈4.48 MHz TT" is also superseded | `OP` lines 16, 25–28; `W10/pipe2/README.md` |
| 2 | Pipe2 KLayout DRC 0, antenna 11/12, XOR 0 and die 22.836 mm² come from the run state file, **not yet written into the README**. LVS has not finished. Do not cite pipe2 as LVS-clean | `SSD-RUN/pipe2-local/runs/pipe2/69-checker-klayoutdrc/state_out.json` vs `W10/pipe2/README.md` |
| 3 | Antenna counts differ by report: first route 130 nets / 151 pins (`W10/RESULTS.md` mixes the post-DRT check at 130 with a lead-verified pin count of 151); closure 4/5 (pass 1), 4/4 (pass 2); pipe2 11/12. The prompt's "11 nets" matches | `W10/RESULTS.md`; `closure-lead/manufacturability.rpt`; pipe2 state |
| 4 | Two "default activity" figures for closure pass 1: the flow's `power__total` is 0.1409 W, but the lead's `power-eco.log` default-activity value is 0.110 W. The settings or parasitics probably differ; use the SAIF figure (0.168 W) | `closure-lead/final-metrics.json`; `power-eco.log` |
| 5 | Annotation coverage falls from 97.7% (first route) to ≈68% (closure) to 67.5% (pipe2), because repair, diode and antenna cells are missing from the synthesized netlist. **The 241 → 256 → 287 pJ/MAC trend mixes real change with lower coverage.** INFERRED: unannotated cells get default activity, so the later numbers are less certain, not necessarily lower bounds | `routed-power-lead/RESULTS.md`; `power-eco.log`; `pipe2/README.md` |
| 6 | Engine energy across stages: 66 pJ/MAC (64×320 slice, pre-route, 200 ns) → 162 (buf-v4 pre-route, no CTS) → 241 / 256 / 287 (routed). Different scopes and clocks; not a like-for-like series | `OP` 04:57, 07:30; routed files |
| 7 | "0.106 W" appears twice with different meanings: the pre-route 66.4 µJ/projection at 150 ns (floorplan, 14 Oct), and the routed first route at the achieved 223 ns (22 Oct) | `OP` 20:20 and 22 Oct 19:30 |
| 8 | W12 reports "Maximum child RSS 29.215 GiB" (FPGA) and 18.8 GiB (generic) while also saying the runner enforces a 6 GB address-space cap per process. Unexplained | `FIN/w12-synth/RESULTS.md` |
| 9 | Mutable bits: 8,501,818 (v1, Verilator inventory) vs 8,169,778 (v2, Yosys). W14 says the 332,040-bit difference is "not an established saving" | `FIN/w14-blocks/RESULTS.md`; `OP` 02:38 |
| 10 | Spend by rate × window (INFERRED) is $8.86 and $25.77, vs recorded $8.96 and $25.87. The guard's estimate is not a reconciled invoice. Cap figures: $30 goal; guard $28 → $58; user cap $60 | `OVN/runpod/spend.json`, `guard.log`; `OP` |
| 11 | Pod memory: 755 GB (`free`, in the W10 brief and launch notes) vs a 64 GB cgroup limit | `OP` line 39; `FIN/POD-SCHEDULE.md` |
| 12 | `W10/RESULTS.md` and `W10/closure/RESULTS.md` still show routed power "unavailable" and closure "waiting for gate". Both are stale, superseded by `routed-power-lead/` and `closure-lead/` | listed paths; `closure/SUPERSEDED-20261021.md` |
| 13 | `W10/results.json` `drt_progress` concatenates four DRT trajectories (starting at 696,965, 209,864, 110,843 and 68,834). Only the last matches the reported route. The other three are unlabelled | `W10/results.json` |
| 14 | Closure pass 1 DRT is reported as "25 → 25 → 0", but the metrics show later iterations rising again (42, 68, 35) before the final 0, consistent with ECO re-routes | `OP` line 14; `closure-lead/final-metrics.json` |
| 15 | "6 logic macros signed off" (W14) means READY under block-level checks with density deferred. All fail the supplemental density deck. W15 placed only 4 of them | `FIN/w14-blocks/RESULTS.md`; `FIN/w15-chip/RESULTS.md` |
| 16 | **Claimed-only 14 Oct items** (not lead-verified at the time): W2 slice 4.230 mm² and 190,460 cells; W2b ARRAY-PORT 6.137 mm² and SC-ROM 8.255 mm²; W5 tall-bank areas/timing; W3 two-die IR (01:22); W2b gate-level regressions (03:20). The 06:49 physical progress is marked "(claimed, from worker reports)" | `OP` entries marked *(claimed)* |
| 17 | W13 drivers: capture/escape is "staged", with full peripheral qualification pending. Full LVS covers 6 of 81 banks (representatives) | `FIN/w13-arrays/DRIVERS-RESULTS.md`, `RESULTS.md` |
| 18 | W15 IR fails with **inherited assumed loads**, which conflicts with the 14 Oct floorplan IR pass at 0.144 W. The models differ (real arrays plus stubs vs abstract macros) | `FIN/w15-chip/RESULTS.md`; `OVN/floorplan/MEASURED-ENGINE-UPDATE.md` |
| 19 | The HF backup dataset is **public**; `OP` flags it for review | `OP` line 34 |
| 20 | `OP` log timestamps from 01:05–01:22 run ≈15 min late, and entries marked ≈ after 02:40 were corrected; one entry (01:07) is out of order | `OP` line 217 |
| 21 | W11's F64 is an integration repeat, not a new corpus tally or held-out accuracy test. The extra-clip clock counts are not comparable to the earlier separate-DUT totals | `FIN/w11-taalas-e2e/RESULTS.md` |
| 22 | The routed slew/cap-limit violations (hundreds of thousands in every run) are open in all iterations, including pipe2. "All 9 corners met" refers to setup and hold only | `W10/pipe2/README.md`; `sta-postpnr-summary.rpt` |
