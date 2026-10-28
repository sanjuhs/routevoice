# W6 pitch-matched readout

**The new 1,280-row bank measures 2.26784524 mm², or 5.536731543 µm² per selection including analog readout and local wiring.** This is 78.41% smaller than W5's stretched tall-bank implementation. Both the 64-row slice and full bank have selected GF180 DRC = 0 and exact real-image bit readback. Full 64-row LVS and its negative control pass. Full-bank LVS and global capacitance ranking are still running; this report will be updated with their outcomes.

## Choice and construction

We chose **A: eight staggered readout rows**, with 16 receivers per row in each 32-lane subbank. Eight rows reuse the retained pre2 receiver circuit and allow short, monotonic local joins. No column multiplexing or additional read subphases are introduced.

The local bit-line pitch stays at 0.66 µm, plus a 1 µm corridor per 16 lines: **0.7225 µm average native pitch**. Subbanks repeat every 100 µm including supplies and separation. The full-bank width divided by 1,280 lines is 0.784375 µm, including edge and group overhead. Metal2/3/4 joins connect the native-pitch bit lines to the staggered receivers.

This is the patent's stored-address branch: four mask-programmed access NMOS per four-bit selection, followed by a precharge device, keeper and restoring inverter per bit. It does not measure the direct one-access-transistor product-selection embodiment. Shared numerical products remain downstream; representative, activation and accumulator precision are unchanged.

## Measured area and verification

| Physical scope | Dimensions (µm) | Area (mm²) | µm²/selection | Selected DRC | Real bits checked | LVS |
|---|---:|---:|---:|---:|---:|---|
| W6 corrected 64-row slice | 1004 × 234.17 | 0.23510668 | 11.479818 | 0 | 81,920; zero mismatches | 87,040 devices; unique match; negative rejected |
| W6 full 1,280-row bank | 1004 × 2258.81 | 2.26784524 | 5.536732 | 0 | 1,638,400; zero mismatches | Pending |
| W5 1,280-row bank | 4669.7 × 2249 | 10.5021553 | 25.640028 | W5 evidence | W5 evidence | Outside this W6 check |
| W5 four-bank 320-row assembly | 4669.7 × 2664 | 12.4400808 | 30.371291 | W5 evidence | W5 evidence | Outside this W6 check |
| W5 twenty-tile 64-row assembly | 4669.7 × 4780 | 22.3211660 | 54.495034 | W5 evidence | W5 evidence | Outside this W6 check |

Measured area covers cells, analog receivers and physical local/common wires. **Output escape from the stacked receiver pins is unfinished.** Placed decoder and WL/PC drivers, phase control, latches, downstream products and accumulation, and complete PDN also remain outside the measured footprint. W5's single 64-row tile was 50.162793 µm²/selection; the 54.495034 assembly figure includes intertile gaps.

Selected DRC uses official GF180 FEOL, BEOL, connectivity and off-grid checks, excluding density and antenna. This is not foundry signoff. Independent readback decodes the original packed K64 tensor and checks programmed Via1 positions in reopened GDS. LVS compares the extracted circuit with an independent source-derived schematic, with bijective name normalization and exact device, connectivity and W/L checks. The negative control doubles one precharge width; it must be rejected even if Netgen still prints its topology-match phrase.

The first 64-row revision failed with **160 DRC markers**: 80 Metal3 spacing and 80 Via4 enclosure errors. Revision 2 shifts receiver origins 0.09 µm right and the lower ground-via rail 0.4 µm up. Indices and transistor dimensions are unchanged. The [failed revision](r64-v1/) and [original generator](scripts/build-v1.py) are preserved.

## Extracted timing: provisional subbank 02

The pilot candidate is global bit column 273. It was selected using all-bank connected-drain and wire-resistance estimates, followed by extracted capacitance ranking of the 128 columns in subbank 02. Global ranking from the full-bank extraction remains pending.

| Corner | Tested cycle (ns) | Worst sampled settle after WL command (ns) | Failed 20 ns capture probes | Partial slice source energy (pJ/read) | Candidate 273 receiver MOS energy (pJ/read) |
|---|---:|---:|---:|---:|---:|
| TT, 3.30 V, 25 °C | 60 | 15.211376 | 0 / 160 | 123.606923 | 6.784321 |
| SS, 2.97 V, 125 °C | 60 | 23.376321 | 12 / 160 | 98.516840 | 5.328009 |

Both simulations converged and passed all final output, raw-bit-line, precharge and phase checks in the retained 60 ns protocol. The slowest sample at both corners is cycle 5, row 0, column 273. The tested row sequence is 0, 1, 1279, 1274 and 546, repeated twice. This samples near/far and data-dependent behavior; it is not exhaustive timing across every address and aggressor pattern.

**The 20 ns capture aperture fails at SS.** Interleaving cannot remove this latency failure. The existing INDEX path needs separately verified clock/phase changes or a completion interface; see [INTEGRATION.md](INTEGRATION.md).

The electrical model includes 16 actual full-height columns, all 128 physical receivers, 112 ideal legal-state bit-line aggressors, extracted stock WL/PC drivers, extracted MOS and capacitance, and geometry-derived wire resistance. Output load is assumed to be 10 fF. It does not establish full 1,280-column control loading, simultaneous array current, nonideal supplies, physical decoder/phase/latch integration or mismatch. Resistance is modeled from geometry, not automatic distributed-R extraction.

W5's latest 1,280-row result is 14.676 ns TT / 24.351 ns SS at a 60 ns tested interval. Its earlier 3–4.4 ns settling applies to the 64-row slice with a different electrical model. These are not directly comparable speed measurements. The [latest W5 reports](baseline/05-W5-RESULTS.md) are preserved with hashes.

Energy is finite-window net source energy over the repeated sequence. The per-column meter covers the timing candidate's four receiver MOS supply/well currents, including device-model junctions. Explicit extracted VDD-coupling-capacitor current and shared control/aggressor energy are excluded from that meter. Candidate 273 is not the energy maximum: sampled column 282 reaches 9.915976 pJ TT and 7.903973 pJ SS. **Complete 1,280-bit row energy is unknown; partial slice energy must not be presented as measured full-row energy.** Exact scope and independent trace checks are in [timing evidence](timing/RESULTS.md) and the [timing audit](audit/TIMING-AUDIT.md).

## Whole-model extrapolation and October comparison

The uniform-density extrapolation is:

`31,457,280 selections × 5.536731543 µm²/selection ÷ 1,000,000 = 174.170514 mm²`

This is an engineering extrapolation from the measured rectangular bank, not a whole-model layout. It does not allocate the 98 tensor shapes, padding, extra ports, replicas, tied-table transpose access or whole-chip wiring.

The October component budget has 153.833 mm² of base arrays and 11.004 mm² of receiver strips: 164.837 mm² combined. Its other terms are 25.002 mm² decoder, 30.369 mm² WL drivers, 0.269 mm² PC drivers and 0.944 mm² bank selectors, totaling another 56.584 mm². The old total is 221.421 mm², approximately 154 mm² cells plus 67 mm² periphery.

W6's integrated array/readout/local-wire extrapolation is 9.333514 mm² above the old array-plus-receiver subtotal. Adding the older nonreceiver terms gives **230.754514 mm²**. This mixed estimate retains the old utilization and allocation assumptions and is neither placed nor a complete macro. The old 11.004 mm² receiver term is not added again.

The 78.4% saving therefore applies to W5's physically stretched bank, not the October idealized component budget. A complete recognizer, die fit and sub-watt operation remain unproved.

## Handoff and pending work

- [Full bank GDS](r1280-v2/bank.gds), [geometry](r1280-v2/geometry.json), [selected DRC](r1280-v2/drc-result.json), [bit readback](r1280-v2/readback.json).
- [64-row GDS](r64-v2/bank.gds), [independent verification](verification/RESULTS.md), [geometry audit](audit/RESULTS.md).
- [Machine-readable results](results.json), [commands](COMMANDS.md), [source reading](READING.md), [baseline hashes](baseline/manifest.json).

Pending: monolithic full-bank LVS and negative control, full-bank capacitance ranking, and any new candidate timing it requires. The live extraction has a recorded watchdog extension to a 3,600 s absolute bound; Magic was not restarted. All W6 writes stay inside this workspace, W5 remains read-only, and the run uses no git or cloud, at most four CPU threads, and a 22 GiB free-disk guard.
