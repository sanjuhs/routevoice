# W8 complete GF180 projection — partial result

Finalized 14 October 2026, 05:56 IST.

**The requested complete placed-and-routed projection was not achieved.** Provisional macro views and a guarded RTL integration are delivered. The combined engine, decoder/drivers, bank and capture flops reached placement and CTS with connected macro power pins, then failed global routing. No achieved frequency, complete projection energy or real-time power is established.

| Stage | Result |
|---|---|
| 1 — Macro views | Delivered LEF, black-box Verilog and explicitly provisional Liberty. All 2,563 ports were checked against unchanged W6 GDS labels and real metal shapes. |
| 2 — Integration | RTL simulation with the real-index behavioral bank passes 54 vectors, 17,280 FP32 outputs, 17,280 integer checks, random stalls and 11 reset-abort cases. **The requested 60 ns schedule is not implemented.** |
| 3 — Physical | Placement, CTS and macro PDN connection completed. Global routing failed `GRT-0116` after 50 repair iterations, with total overflow 100. No detailed routing, extracted RC or final signoff. |
| 4 — Activity power | Not qualified. The mapped simulation stalled after reset; its trace is rejected. A native retry stopped at the disk guard before simulation. No activity-based post-route power run was possible. |

## Delivered integration and its limits

The unchanged bank contains all **409,600 real four-bit selections**. It implements the stored-index readable-cell branch, with shared coefficient products in the downstream engine. No synthesized substitute index ROM is used in the physical composition. This is one selected projection, not a complete recognizer.

The controller commands PC rising at 20 ns, WL rising at 40 ns, capture at 80 ns, WL falling at 100 ns and PC falling at 120 ns, evaluated at the target 20 ns clock. The next row is accepted after nine clocks: **180 ns target-derived cadence**. An unstalled projection takes 11,843 clocks, implying 236.86 µs at that target; these are functional schedule calculations, not achieved physical performance.

The commanded 120 ns sequence passes the retained extracted SS slice: 320 output samples, no protocol/data failures, and 23.374847 ns worst sampled settling. Full-bank timing, distributed loading, simultaneous current, supplies, capture loading and analog reset remain unqualified. The original 20 ns capture probe fails 12 checks. See [contract](CONTRACT.md), [RTL log](logs/rtl-simulation.log), [analog result](protocol/RESULTS.md), and [controller review](protocol/guarded-rtl-review.md).

The macro Liberty uses a **44 ns PC-to-OUT engineering proxy**: a 20 ns command guard plus rounded 24 ns sampled settling. The bank has no clock pin. Independent WL timing arcs, full-bank PVT characterization and internal/leakage power tables are absent. Wordline capacitance 2 pF, precharge capacitance 10 pF and output slew 1 ns are explicit assumptions. See [macro verification](macro/verification.json) and [model derivation](macro/timing-model.json).

## Physical measurements from the retained checkpoint

The trial used a 4,500 × 4,500 µm floorplan, target clock 20 ns, ten routing threads and two STA threads. Post-placement/global-route design repair and post-CTS/global-route timing repair were disabled to bound runtime. The bank is at (500, 1200) µm, orientation N.

| Quantity | Measured checkpoint value |
|---|---:|
| Chosen die area, **unrouted** | 20.250000 mm² |
| Logic and clock cell geometry after CTS | 6.535268 mm² |
| Taps | 0.504488 mm² |
| Endcaps | 0.015112 mm² |
| Bank LEF footprint | 2.267885 mm² |
| Total occupied instance geometry | 9.322753 mm² |
| Total instances | 446,077 |
| Same-net macro PDN via contacts | 16 per supply |

Area values come from actual saved OpenDB master dimensions and instance counts. The source bank GDS bounding box is 1,004 × 2,258.81 µm, or 2.26784524 mm²; the LEF retains its original 0.04 µm bottom-coordinate allowance. PDN checks establish connectivity and physical intersections, not IR-drop or electromigration qualification. See [exact area audit](evidence/post-cts-exact-area.json) and [PDN audit](physical-audit-v3/RESULTS.md).

Global routing ended with overflow by layer: Metal2 **4**, Metal3 **73**, Metal4 **12**, Metal5 **11**. Reported global resource usage was 61.48%. Its failed candidate contained 328,257 routed nets, 3,342,223 vias and 60,267,790 µm wirelength; these are **failed global-route diagnostics**, not a completed detailed route. The flow exited 2, leaving CTS as the last geometry checkpoint. The [routing failure log](evidence/global-route-failure.log) preserves the native counts.

The post-CTS nominal-TT report has setup slack **−24,623.166 ns** and hold slack **−1.543987 ns**. Register-to-register hold slack is +0.834701 ns; the worst hold path starts at `activation_scale[24]` under the 4 ns external-delay assumption. There are 3,586 capacitance and 631,187 slew violations. The placement report shows an engine NOR driving 4,477 loads at 29.191011 pF versus a 0.1829 pF characterized maximum. These extreme extrapolations diagnose a buffering/design-rule failure; they do not yield a credible achieved MHz or timing-qualified power estimate. See [load-limit evidence](evidence/high-fanout-liberty-limits.json) and [CTS setup report](evidence/post-cts-tt-max.rpt).

**Post-route setup/hold at all nine requested PVT/RC corners, routed die area, achieved MHz, final DRC, LVS and antenna counts are unknown.** Those stages did not run. Inherited W6 bank checks do not substitute for integrated-block signoff. No final routed GDS exists from this run.

## Gate activity and power boundary

The first gate attempt could not load four vector/reference files on the pod and was rejected. The exact source files were then staged and hash-checked under W8; only four generated simulator path literals changed before a normal incremental rebuild.

The corrected pod simulation still failed: it accepted the start but transferred zero activations. The one-hot phase controller became all-zero at the first post-reset clock. Recorded D7 was high for 10 ns before the edge, but Q7 did not rise. The run reached its 20-minute wall timeout, exit 124. Both two-flop and exact eight-flop controller probes pass in Verilator 5.044 and 5.050; the two-flop probe also passes in Icarus. These results leave the full-design cause unresolved and do not establish a generic version bug. Both invalid traces and diagnostic logs are preserved; neither was used for activity annotation or power.

The unchanged gate harness passes against RTL and the behavioral bank: one real vector, 320 outputs, exactly 11,843 cycles. A full mapped retry with native Verilator 5.050 was stopped before compilation completed by the **22.5 GiB free-space guard**, preserving the user's 22 GiB minimum. No native activity trace was produced by that attempt. A second bounded retry in `gate-native-v2/` also stopped at the same free-space guard before compilation completed. Its [receipt](gate-native-v2/receipt.json) is retained; neither retry produced a waveform. See [RTL harness crosscheck](sim-gate-harness-rtl/RESULTS.md), [native retry receipt](gate-native/receipt.json), and the `gate-activity-audit/` diagnostics.

The sampled analog slice's source energy is **100.260424 pJ per sampled read**, within its declared partial boundary. It cannot be scaled into a measured complete-row energy. Full-array internal/leakage energy and an evidenced streaming invocation calendar are missing. Complete-row energy, projection energy, activity coverage and real-time power remain `null`. The prepared, API-checked [power recipe](power/README.md) is retained for a later qualified gate trace and extracted design.

## Preserved handoff

- [Machine-readable results](results.json).
- [Last CTS DEF](evidence/final-cts.def.gz), [CTS netlist](evidence/final-cts.nl.v.gz), and [checksum receipt](evidence/final-cts-checkpoint.json).
- [CTS layout image](evidence/final-cts.png): actual DEF plus LEF abstracts; display-layer omissions apply. It is an unrouted view, not a transistor-fabric image.
- [Physical reports and logs](evidence/physical-reports-failed-global-route.tar.gz), with [archive manifest](evidence/physical-reports-failed-global-route.tar.json).
- Earlier launch, protocol, missing-vector and simulation failures remain in their dated/explicitly invalid evidence locations. Interrupted native compiler outputs are preserved in verified lossless archives within each retry directory.

The next physical attempt needs fanout/design-rule repair and renewed congestion closure. Gate-level correctness must be resolved before its activity is used for power. The requested 60 ns protocol and full-bank characterization remain separate unfinished requirements.
