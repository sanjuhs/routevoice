# W14 partial results — 6 READY macro(s)

Updated 2026-10-20T23:55:09.726587+00:00. **6 signed-off macro(s); complete non-weight recognizer hardening is not achieved.**

All active W14 EDA is resource-suspended. Free internal disk: 23.95 GiB; resume requires 26 GiB, identity checks and the six-core allowance. See [NEED-SPACE.md](NEED-SPACE.md).

Fourteen provisional ownership groups and all 144 mutable-array declarations are recorded in [PARTITION.md](PARTITION.md) and [partition.json](partition.json). These are not yet 14 complete hardenable wrappers: W12 whole-recognizer GF180 mapping is blocked by its generic-stage failure in the latest remote report, SRAM latency/port adaptation is incomplete, and the previous two-die floorplan is only an abstract capacity/PDN screen.

Lead guidance 1 applied: metal density is **deferred to chip-level fill (W15)** and does not block READY. Block standard-cell fill stays enabled. No supported GF180 metal-density fill stage was found in the installed LibreLane Classic flow. Every reported slew/cap violation in the three existing routed candidates was classified as internal using exact ODB connectivity; see [electrical-guidance1/](electrical-guidance1/). Buffered-boundary STA does not remove these internal failures. New runs use buf4 input drivers, 20 fF output loads, input/output buffering flags, post-GPL repair disabled and post-GRT repair enabled. The io_token_sequencer_g1 launcher additionally inserts port buffers explicitly before post-GRT repair because the installed stock post-GRT step ignores those flags. Physical runs are limited to one core each.

## Actual routed leaf attempts

| Block/run | Die mm² | Stdcell mm² | Magic DRC | LVS | Setup/hold WNS ns | Slew/cap violations | Status |
|---|---:|---:|---:|---:|---|---|---|
| decoder_embedding_calibrated_retry | — | — | — | — | — | — | suspended_disk_reserve: 37-openroad-stamidpnr-3 |
| io_token_sequencer_resume | 0.178650 | 0.085362 | 0 | 0 | 0/0 | 139/3 | NOT READY |
| io_token_sequencer_retry | 0.206804 | 0.095379 | 0 | 0 | 0/0 | 459/1 | NOT READY |
| quantizer_value_signoff | 0.202280 | 0.086969 | 0 | 0 | 0/0 | 342/1 | NOT READY |
| quantizer_value_retry | — | — | — | — | — | — | stopped_resource_growth: 31-openroad-stamidpnr |
| quantizer_value_g1 | 0.231979 | 0.077523 | 0 | 0 | 0/0 | 1414/3 | NOT READY |
| frontend_cmvn_g1 | — | — | — | — | — | — | stopped_disk_guard: 30-checker-powergridviolations |
| frontend_cmvn_margin0 | — | — | — | — | — | — | stopped_preCTS_resource_growth: None |
| frontend_cmvn_ideal_preCTS | — | — | — | — | — | — | running: 24-openroad-rcx |
| io_token_sequencer_g1 | 0.189898 | 0.084096 | 0 | 0 | 0/0 | 888/14 | NOT READY |
| rom_position_g1 | 0.065185 | 0.029664 | 0 | 0 | 0/0 | 0/1 | NOT READY |
| rom_position_retry | 0.075075 | 0.030169 | 0 | 0 | 0/0 | 0/0 | NOT READY |
| frontend_preprocess_g1 | — | — | — | — | — | — | stopped_disk_guard: 05-yosys-jsonheader |
| frontend_preprocess_resume | — | — | — | — | — | — | STOPPED_DISK_GUARD_DURING_SYNTHESIS: None |
| rom_position_binary | 0.090494 | 0.042824 | 0 | 0 | 0/0 | 34/0 | NOT READY |
| rom_position_slew_eco | 0.090494 | 0.042855 | 0 | 0 | 0/0 | 0/0 | READY |
| source_phase_control_g1 | — | — | — | — | — | — | failed_flow: 33-openroad-detailedplacement |
| source_phase_control_retry | 0.019600 | 0.001675 | 0 | 0 | 0/0 | 0/0 | READY |
| decoder_embedding_g1 | — | — | — | — | — | — | stopped_disk_guard: 43-openroad-stamidpnr-3 |
| decoder_embedding_resume | — | — | — | — | — | — | stopped_source_functional_failure: None |
| decoder_embedding_verified | — | — | — | — | — | — | STOPPED_DISK_GUARD_AFTER_EXTRACTED_STA: 12-openroad-stapostpnr |
| frontend_conv_logic_g1 | — | 2.176798 | — | — | — | — | synthesis_only: 06-yosys-synthesis |
| producer_metadata_g1 | 0.163140 | 0.091970 | 0 | 0 | 0/0 | 74/12 | NOT READY |
| producer_metadata_retry | 0.188779 | 0.096468 | 0 | 0 | 0/0 | 2/0 | NOT READY |
| producer_metadata_eco | 0.188779 | 0.096490 | 0 | 0 | 0/0 | 0/0 | READY |
| decoder_learned_norm_g1 | 0.108849 | 0.061369 | 0 | 0 | 0/0 | 0/0 | READY |
| frontend_conv_physical | — | — | — | — | — | — | stopped_mapped_functional_progress_mismatch: 05-openroad-checkmacroinstances |
| quantizer_calibrated_eco | 0.231979 | 0.107780 | 0 | 0 | 0/0 | 0/0 | READY |
| io_token_sequencer_calibrated_eco | 0.189898 | 0.097798 | 0 | 0 | 0/0 | 0/0 | READY |

150 ns clock; initial 35% utilization, one 30% retry per block. Both use W9 PI-buffered ABC with max signal fanout 16 verified in synthesized netlists. Lower-density retries also enable slow-corner/typical/fast-corner repair and a tighter clock-tree capacitance target. Signoff limits are unchanged. Full native reports retain all nine extracted corners. The standard flow reports success despite electrical warnings and skips KLayout DRC because its PDK runset is unset; neither is treated as signoff.

GDS/LEF/nine-corner timing Liberty/netlist/SDC copies and SHA256 manifests are under [candidates/](candidates/). Failed views are deliberately not promoted to `macros/`.

## Supplemental physical checks

- io_token_sequencer_resume: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/io_token_sequencer_resume/results.json.
- io_token_sequencer_retry: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/io_token_sequencer_retry/results.json.
- quantizer_value_signoff: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/quantizer_value_signoff/results.json.
- rom_position_retry: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/rom_position_retry/results.json.
- rom_position_slew_eco: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/rom_position_slew_eco/results.json.
- source_phase_control_retry: failed; {'main': 0, 'density': 7, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/source_phase_control_retry/results.json.
- producer_metadata_eco: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/producer_metadata_eco/results.json.
- decoder_learned_norm_g1: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/decoder_learned_norm_g1/results.json.
- quantizer_calibrated_eco: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/quantizer_calibrated_eco/results.json.
- io_token_sequencer_calibrated_eco: failed; {'main': 0, 'density': 5, 'antenna': 0}. Exact GDS/deck hashes in physical-audit/runs/io_token_sequencer_calibrated_eco/results.json.

## Functional and memory evidence

Latest additional evidence: [embedding extracted electrical audit](embedding-electrical-audit/RESULTS.md), [bridge SRAM candidate](bridge-sram/RESULTS.md), and [frontend reset source qualification](group-scale/frontend-conv-validation/reset-source-pass.json). These do not add a READY macro.

- Original and first routed sequencer: 26 cases, 1,606 checks, 1,301 clocks; matching output. Retry receipts are separate.
- Original and first routed quantizer lane: 111,636 fixtures, 112,665 exact value/flag/unsupported checks, 3 reset aborts, 338 held cycles, 937,560 clocks; matching output and latency histogram. Corrupted-oracle negative controls fail as intended.
- The quantizer lower-density retry stopped in post-GPL repair after 16.2G sampled memory footprint and no log progress; no new final netlist exists. See evidence/quantizer_value_retry-stop.json.
- These tests are bounded untimed gate replay, not whole-recognizer proof or SRAM replacement qualification. See [functional-audit/RESULTS.md](functional-audit/RESULTS.md).
- Encoder A/B/Codes SRAM adapter and exact powered mapped netlist passed F64 replay: 105,788 cycles, 14,160 accepts, 14,158 replies (two POR cancellations), and 62,135 valid-response comparisons. Its elaboration contains 384 SRAMs with verified power hooks. Mapped controller cells occupy0.297807mm² with nonclock fanout≤16. P&R, extracted timing and final physical-gate replay remain pending; see encoder-sram/RESULTS.md.
- Memory audit enumerates 144 declarations / 321 occurrences / 8,501,818 v1 bits. W12 v2 reports 311 inferred memories / 8,169,778 bits; their 332,040-bit difference is not an established saving. Exact tiles, macro views/hashes and port/reset/latency blockers are in [memory-audit/MEMORY-AUDIT.md](memory-audit/MEMORY-AUDIT.md).
- Producer A/B/Codes has a local SRAM replacement candidate and complete 384-instance GF180 macro template in `sram-adapter/`. It needs 77.424690 mm² bare SRAM area before control/PDN/routing. F4 and F64 differential tests pass their bounded written-address/protocol cases; the canonical F64 rerun uses internal PDK copies and passes 19,079 valid-cycle comparisons. A wrong-bank negative control is rejected, and the width/depth tile suite passes 1,637 reads. No physical binding or full-recognizer SRAM pass is claimed.

## Guidance 1 scale-up evidence

Published leaves do not qualify the full 14 ownership groups. Supplementary lowering brings component coverage to 15/17; W15-LOWERED-SUPPLEMENT.json records decoder-head and encoder-feedforward ports and hashes. Intermediate cells are not mapped area. Frontend SRAM passes grid, power-connectivity and global-route checks with zero overflow; 7,328 slew/889 capacitance nominal-TT placement-estimated violations remain. See frontend-sram/physical/GRT-RESULTS.md. Producer powered mapped F64 replay passes 19,079 valid comparisons; its 11,934 handshakes include the documented binary substitution for the older X-valid malformed case.

Source closures, disjoint cut manifests, restored ROM-service control candidates and bounded replay evidence are under [group-scale/](group-scale/). CMVN lowered RTL passed12,341 checks. The first ROM-position routed candidate failed final-gate replay despite clean electrical checks; source reduction-X guards collapsed to unconditional rejection during synthesis. The corrected binary-input-domain candidate passed1,346,296 source/lowered comparisons and is a separate physical run. Full recognizer qualification remains pending.

Producer physical preparation is under [producer-hardening/](producer-hardening/):384 SRAM instances survive mapping; explicit control/address buffer trees achieve nonclock fanout≤16, adding282 buf4 cells. Total mapped standard-cell area0.246811mm² is only this producer memory endpoint controller, not the complete producer/quantizer group. The regular 16×24 manual macro grid fits a 150 mm² footprint. All 384 macro positions, halos, VDD/VSS hooks and grid connectivity passed floorplan audits; placement and routing remain pending.

Finished run directories have been SHA256-verified and offloaded to the authorized SSD. Their paths remain archival symlinks; new active EDA inputs are internal. Archive manifests are in evidence/archive-*.json.

## Lead handoff and remaining work

[NEED-POD.md](NEED-POD.md) requests a bounded slice of the existing authorized pod after W12 releases its four threads. A read-only process check on 21 October still found active W12 FPGA Yosys; W14 has not claimed that slice. The remote W12 report records generic failure after884.775s /30.532GiB peak, GF180 blocked, and raw exit247; no OOM diagnosis is asserted here. See evidence/w12-remote-status-0406.txt. W14 launched no cloud resources. Restore excluded ROM-service controllers, derive complete residual cut wrappers, resolve SRAM schedules, measure/split cell areas, add physical macro placement/PDN, and rerun full owner/recognizer equivalence before W15 assembly. The complete target is blocked on these prerequisites; published leaf implementations cannot stand in for the recognizer.

[FAILURES.md](FAILURES.md) retains launch/resource deviations, electrical and density failures. All project edits are inside W14. Automatic Nix caches during the first tool probe and initial excess thread defaults are explicitly recorded; subsequent runs use existing native tools with process/thread limits. The disk guard suspends W14 at 24 GiB to protect the user’s 22 GiB hard floor; resumption requires 26 GiB. No archived input was modified; no git command was used.

Partial report is published before the requested Thursday 20:00 IST deadline. It is not a release/signoff claim.

## Lead guidance 2 — corrected memory schedule

The pod cgroup limit is 64,000,000,000 bytes, not the host RAM figure. Follow ../POD-SCHEDULE.md. Until W12 generic completes, only jobs with expected peak strictly below 5 GB may launch; every launch also requires fresh memory.current plus expected peak below 56 GB. Afterwards, W14 large blocks run one at a time with at most six threads. No W14 compute was present in the initial corrected-schedule process check. Mac large synthesis remains sequential and guarded; head mapping is prepared but deferred below the 26 GiB restart threshold. See head-mapping/RESULTS.md and evidence/pod-schedule-guidance2.json. The head SRAM replay is being checked as a low-memory pod task; no new READY result follows.

## 21 October head mapping attempt

Run `head_baseline_20261021T053333` passed lint (0 errors; 261,811 retained warnings) and completed the Yosys header. Synthesis was stopped by the 24 GiB disk guard after 633.9 seconds; process-group peak sampled RSS was 10.948 GiB. Child exit was -15 from the guard, not an OOM or RTL failure. Mapping did not complete and no area/timing or READY claim exists. Free space immediately after stop: 23.860 GiB. Frozen input, header checkpoint, logs and receipt remain under head-mapping/. A restart needs additional internal headroom or the post-W12 generic pod slot.
