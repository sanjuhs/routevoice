# W2 — fixed-weight GF180 projection fabric

**Work in progress.** V2 global routing is active. Full V1 stopped at its time budget, and the V1 slice stopped at the disk guard; both retained post-CTS checkpoints. Final routed timing, power and signoff are not yet available.

All measurements concern one raw integer projection primitive. V1 freezes the real image-0 indices and books in standard-cell logic; V2 excludes the external array and its peripherals. This is not a complete speech recognizer or a characterized one-transistor array.

| Variant | Weight positions | RTL vectors / comparisons / failures | Synthesized cells | Cell area (mm²) | Cell µm² / weight |
|---|---:|---:|---:|---:|---:|
| `rv_fixed_proj320_rom` | 102,400 | 32 / 10272 / 0 | 265,388 | 5.674713 | 55.417117 |
| `rv_fixed_proj320_dp` | 102,400 | 32 / 10272 / 0 | 222,596 | 5.276646 | 51.529747 |
| `rv_fixed_proj64x320_rom` | 20,480 | 32 / 10272 / 0 | 190,460 | 4.229742 | 206.530376 |

Cell area is the synthesis cell sum, not a routed die area. V2 per-weight values amortize its datapath across 102,400 logical positions; they do not measure stored-weight area. Constant folding differs between variants, so subtraction of their areas is not a physical storage measurement.

| Variant | Allocated die / core (mm²) | Checkpoint instance area (mm²) / utilization | Target period (ns) | PDN connectivity violations | Last completed baseline step |
|---|---:|---:|---:|---:|---|
| `rv_fixed_proj320_rom` | 28.612630 / 28.353067 | 10.743300 / 37.891% | 200 | 0 | `02-openroad-stamidpnr-2` |
| `rv_fixed_proj320_dp` | 26.613756 / 26.376030 | 11.803700 / 44.752% | 200 | 0 | `02-openroad-stamidpnr-2` |
| `rv_fixed_proj64x320_rom` | 14.267764 / 14.085907 | 6.238010 / 44.285% | 200 | 0 | `02-openroad-stamidpnr-2` |

These are block floorplans without a package pad ring. Checkpoint instance area is the current OpenROAD `design__instance__area` after physical transformations; it is separate from synthesis cell area. Auxiliary power/render runs are excluded when selecting the baseline checkpoint. V2 presents 42,240 index/book input bits at the block boundary across Metal1–5; its footprint and timing therefore depend on this interface test configuration.

Latest `rv_fixed_proj320_rom` attempt: `runs/rv_fixed_proj320_rom-route-util20-density35-noinflate-200ns`; last started `03-openroad-globalrouting`, last completed `02-openroad-stamidpnr-2`. Exit `1`; stop reason `Existing full-ROM time budget; stop leaf OpenROAD 12 seconds before supervisor deadline to permit LibreLane log buffer closure. This is not a tool-reported routing violation.`. [Flow log](logs/rv_fixed_proj320_rom-route-util20-density35-noinflate-200ns.flow.log).

**`rv_fixed_proj320_rom` signoff:** incomplete: no extracted final timing/signoff result. Routed DRC: `unavailable`; LVS: `unavailable`; antenna: `unavailable`. Achieved target MHz: unavailable; STA-inferred MHz: unavailable.

Latest `rv_fixed_proj320_dp` attempt: `runs/rv_fixed_proj320_dp-route200`; last started `03-openroad-globalrouting`, last completed `02-openroad-stamidpnr-2`. Exit `pending`; stop reason `None`. [Flow log](logs/rv_fixed_proj320_dp-route200.flow.log).

**`rv_fixed_proj320_dp` signoff:** incomplete: no extracted final timing/signoff result. Routed DRC: `unavailable`; LVS: `unavailable`; antenna: `unavailable`. Achieved target MHz: unavailable; STA-inferred MHz: unavailable.

Latest `rv_fixed_proj64x320_rom` attempt: `runs/rv_fixed_proj64x320_rom-clock200`; last started `03-openroad-globalrouting`, last completed `02-openroad-stamidpnr-2`. Exit `-15`; stop reason `disk safety margin: free below 22 GiB`. [Flow log](logs/rv_fixed_proj64x320_rom-clock200.flow.log).

**`rv_fixed_proj64x320_rom` signoff:** incomplete: no extracted final timing/signoff result. Routed DRC: `unavailable`; LVS: `unavailable`; antenna: `unavailable`. Achieved target MHz: unavailable; STA-inferred MHz: unavailable.

The configured final STA matrix is nom/min/max RC × TT 25°C 5.0 V, SS 125°C 4.5 V, and FF −40°C 5.5 V. If no extracted table appears above, no final corner has been measured. STA-inferred frequency uses the requested formula `1000/(period_ns − worst_setup_slack_ns)` with the existing constraints; it is not a separately rerun timing qualification.

| Variant | Synthesized mm² / weight | Allocated footprint µm² / weight | Routed mm² / weight | mW / weight at qualified clock | Full 320×320 matvec µs at qualified clock |
|---|---:|---:|---:|---:|---:|
| `rv_fixed_proj320_rom` | 0.000055417 | 279.420215 | unavailable | unavailable | unavailable |
| `rv_fixed_proj320_dp` | 0.000051530 | 259.899963 | unavailable | unavailable | unavailable |
| `rv_fixed_proj64x320_rom` | 0.000206530 | 696.668160 | unavailable | unavailable | unavailable |

The slice has only 64 input rows. It cannot supply a full 320×320 matvec time or a full-fabric routed area by itself; no fivefold area/power extrapolation is used.

| Variant | Pre-route TT setup / hold slack (ns) | Target MHz | Setup-inferred MHz |
|---|---:|---:|---:|
| `rv_fixed_proj320_rom` | 66.547300 / 0.556417 | 5.000 | 7.493292 |
| `rv_fixed_proj320_dp` | 53.503200 / 0.548467 | 5.000 | 6.826088 |
| `rv_fixed_proj64x320_rom` | 90.329400 / 0.597714 | 5.000 | 9.118214 |

This separate table uses placement-estimated parasitics at TT and `1000/(period − setup_slack)`. It does not establish routed frequency, other-corner closure, or power at the inferred clock.

**Pre-route power — `rv_fixed_proj320_rom`:** typical corner, 5 MHz; default activity **189.7365302 mW**, selected VCD activity **305.5831492 mW**. 79 pins annotated and 1,226,425 unannotated (0.006% annotated). RTL top-level port activity: 79 directly annotated pins; internal activity propagated/default. No gate-level glitch modelling. Zero matched pins is a failed annotation attempt.

The corresponding checkpoint ratios are 0.001852896 and 0.002984210 mW per weight at that **unqualified target clock**. They are not the missing routed/qualified ratios above. Source: `runs/rv_fixed_proj320_rom-pre-route-rtl-activity/01-openroad-stamidpnr/openroad-stamidpnr.log`.

**Pre-route power — `rv_fixed_proj320_dp`:** typical corner, 5 MHz; default activity **245.1654822 mW**, selected VCD activity **394.8503733 mW**. 42,319 pins annotated and 1,076,008 unannotated (3.784% annotated). RTL top-level port activity: 42319 directly annotated pins; internal activity propagated/default. No gate-level glitch modelling. Zero matched pins is a failed annotation attempt.

The corresponding checkpoint ratios are 0.002394194 and 0.003855961 mW per weight at that **unqualified target clock**. They are not the missing routed/qualified ratios above. Source: `runs/rv_fixed_proj320_dp-pre-route-rtl-activity/01-openroad-stamidpnr/openroad-stamidpnr.log`.

**Pre-route power — `rv_fixed_proj64x320_rom`:** typical corner, 5 MHz; default activity **150.6443769 mW**, selected VCD activity **106.0931012 mW**. 739,686 pins annotated and 103,648 unannotated (87.710% annotated). Zero-delay synthesis-netlist cell-pin activity. Inserted/changed physical cells rely on propagated/default activity; no routed glitches.

The corresponding checkpoint ratios are 0.007355682 and 0.005180327 mW per weight at that **unqualified target clock**. They are not the missing routed/qualified ratios above. Source: `runs/rv_fixed_proj64x320_rom-pre-route-gate-cell-activity/01-openroad-stamidpnr/openroad-stamidpnr.log`.

The first RTL power attempt used a dot-separated VCD scope and matched zero pins: it is a failed annotation attempt. The corrected slash scope matched only 79 top-level pins and produced 116.4083853 mW for the 5 MHz slice. The improved gate run explicitly enables Verilator underscore tracing, exposes leaf-cell pins, and passes five random vectors / 1,605 comparisons. Its waveform spans 387.101 µs after a hash-verified initial-offset removal. OpenSTA reads the compressed VCD directly. All attempts are retained in `evidence/checkpoint-metrics.json`.

Power uses placement-estimated parasitics unless explicitly labelled extracted. The five-vector workload includes clocked output reads and two idle clocks between vectors: 643 cycles/vector for full variants, 387 for the slice. It is not continuous compute-only activity. No routed glitch simulation was performed. OpenSTA pin matching and scope syntax were checked against its [VCD reader](https://raw.githubusercontent.com/The-OpenROAD-Project/OpenSTA/master/power/VcdReader.cc) and [examples](https://github.com/The-OpenROAD-Project/OpenSTA/blob/master/doc/Examples.md).

**Verification and interface.** Every RTL variant passes 32 vectors: 20 seeded random vectors, zero, all −256, all +255, alternating extremes, and coordinate probes at 0, 63, 64, 127, 128, 255, 256 and 319. Six out-of-slice probes reduce to extra zero vectors for the 64-row variant. The NumPy INT64 oracle uses the original W bytes directly, not generated indices/books. The generator asserts all 102,400 reconstructions and exactly 16 representatives in every book. Tests also cover reset abort, input stalls, start while busy, restart, completion, invalid read address and exact latency. The bench checks `done` deassertion by the end of readout, rather than independently asserting pulse width on every intervening cycle.

Mapped `rv_fixed_proj320_rom` also passes 32 vectors / 10,272 comparisons / 0 failures using GF180 FUNCTIONAL models and Verilator. This is zero-delay, two-state functional checking, not SDF timing simulation.
Mapped `rv_fixed_proj320_dp` also passes 32 vectors / 10,272 comparisons / 0 failures using GF180 FUNCTIONAL models and Verilator. This is zero-delay, two-state functional checking, not SDF timing simulation.
Mapped `rv_fixed_proj64x320_rom` also passes 32 vectors / 10,272 comparisons / 0 failures using GF180 FUNCTIONAL models and Verilator. This is zero-delay, two-state functional checking, not SDF timing simulation.

Widths remain separate: index 4, representative 8, activation 9, shared product 13, reconstructed product 17, accumulator 27, activation sum 18 bits. Full accepted-start-to-done latency is **321 clocks**, or 6.42 µs at the initially requested but unqualified 50 MHz. The slice is 65 clocks. Serial reading adds 320 clocks: 641 clocks for a full transaction, with earliest next start on clock 642. See `INTERFACE.md` for handshake and array timing obligations.

**Physical attempts and limitations.** Initial full-V1 synthesis was interrupted first for console-log overhead and then for disk headroom. The later bounded retry completed synthesis in 635.99 seconds. The full physical attempts share the remainder of a two-hour synthesis-plus-physical budget. Its first 30%/20 ns run was stopped after 3,714.54 seconds; native samples showed ongoing slow legalization, not a returned legalization violation count. A 20%/200 ns retry failed global placement with GPL-0305 numerical instability after 680.95 seconds. Reducing placement density from 55% to 35% also failed with GPL-0305 after 570.74 seconds. A final retry disables routability-driven cell inflation, retaining 20% core / 35% placement density and the original overall deadline. This retry passes global placement, PDN connectivity checks, detailed placement, CTS and post-CTS repair. Typical pre-route setup/hold slack is +66.5473/+0.556417 ns at 200 ns. The remaining-budget continuation stopped during global routing near the original deadline; its recovered log reaches extra routing iteration 5/50. A recorded SIGTERM to the OpenROAD child allowed LibreLane to flush its log before the supervisor deadline; the resulting exit 1 is an intentional time-bound interruption, not a reported routing violation. Full V1 is prepared for the lead to rerun with a longer resource budget; no cloud job was launched. The 64-row slice at 45% core utilization failed legalization (DPL-0036, 840 instances). Its 30% continuation passed placement and CTS; typical setup slack at 20 ns was −47.2934 ns. That setup-repair attempt was stopped and a preserved CTS checkpoint restarted at 200 ns with 40 ns IO delays. It passed pre-route timing repair, with typical setup/hold slack +90.3294/+0.597714 ns, then stopped during global routing when free disk crossed the 22 GiB guard after 5,890.26 seconds. These are not final timing results.

V2 first encountered an IO-placement API mismatch (`1.0` passed to an integer track-spacing argument). Specifying 0.56 µm spacing resolved it; Metal5 pins snap to their 0.9 µm grid. The multicorner repair attempt was stopped after repeated native samples showed input-delay arrival/tag processing; the replacement uses typical-corner resizer optimization while retaining the complete final extracted STA matrix and all signoff checks. The V2 30% floorplan passed CTS but missed typical setup by 101.387 ns at a 20 ns period. A rebuild at 20% core utilization and 200 ns passed CTS with typical setup/hold +53.5032/+0.548467 ns before routing; post-CTS cell area was 11.8037 mm² and utilization 44.7516%. Its full-flow continuation enters global routing, where a native sample confirms active maze routing. These are optimization/flow changes, not changes to arithmetic.

All flows keep the default PDN, CTS, detailed routing, fill, Magic and KLayout DRC, Netgen LVS, extracted STA and antenna checks enabled. No signoff errors are suppressed. PnR uses native LibreLane 3.0.11, GF180MCU D / `gf180mcu_fd_sc_mcu7t5v0`, and the tool/PDK versions in `evidence/software.json`. Commands use nice 10. Routing is capped so concurrent routes use no more than eight threads in total. Supervisors enforce time bounds and at least 22 GiB free-space headroom; auxiliary jobs use higher cutoffs. They cannot control unrelated system writes.

**Images and provenance.** The `*-PRE-ROUTE-NOT-SIGNOFF.png` files are visually checked KLayout renders of retained full-V1, slice and V2 placement/PDN checkpoints. They are not final routed layouts. Final rendered layouts, if produced, are listed in `results.json`.

Exact physical launch commands and their recorded outcomes are in `RUN-COMMANDS.md`, each step’s `COMMANDS`, frozen `resolved.json`, and `evidence/*supervisor.json`. Numerical reproduction from the repository root:

```sh
.venv/bin/python overnight-20261014/fabric/gen_fabric.py --weights overnight-20261014/fabric/vectors/coefficients-source.bin
bash overnight-20261014/fabric/verify.sh
.venv/bin/python overnight-20261014/fabric/compress_vcd.py
.venv/bin/python overnight-20261014/fabric/trim_vcd.py
.venv/bin/python overnight-20261014/fabric/collect_checkpoint_metrics.py
.venv/bin/python overnight-20261014/fabric/summarize.py
.venv/bin/python overnight-20261014/fabric/write_run_commands.py
```

`evidence/generation.json` records the original 12-image file SHA-256 and image-0 SHA-256; `vectors/coefficients-source.bin` is a verified exact copy for replay. All W2 writes are confined to this workspace; no git commit/push, cloud allocation or new agent was used. Read `evidence/SOURCE-READING.md` for the patent/source-reading receipt and scope.

Old large views were hash-verified and losslessly archived in `evidence/superseded-placement-views.tar.gz` and `evidence/pre-cts-views.tar.gz`; restore from the fabric directory with `tar -xzf evidence/<archive>.tar.gz -C .` before replaying affected checkpoints. Completed loose files also use hash-verified APFS clones and transparent macOS compression. Rebuildable Verilator C++/object files were removed after successful builds, retaining source, executables, commands and logs. Another actor left SSD-archive markers in two completed power runs; W2 restored their logs by reading those archives and made no external writes. `evidence/checkpoint-path-audit.json` inventories unavailable paths and archive markers. Active computation uses internal files.
