# W6 pitch-matched readout

**The new 1,280-row bank measures 2.26784524 mm², or 5.536731543 µm² per selection including analog readout and local wiring.** This is 78.41% smaller than W5's stretched tall-bank implementation. Both the 64-row slice and full bank have selected GF180 DRC = 0 and exact real-image bit readback. Netgen LVS passes for both sizes, with unique matches and no property errors. The doubled-width negative controls are correctly rejected for both sizes. The globally ranked column passes sampled TT/SS reads, but adding full-bank control loads exposes a failed 60 ns sequence. A 120 ns guarded SS sensitivity passes; its TT companion was stopped by the disk guard and remains incomplete. Complete simultaneous row energy is unmeasured, so this is a partial W6 handoff.

## Choice and construction

We chose **A: eight staggered readout rows**, with 16 receivers per row in each 32-lane subbank. Eight rows reuse the retained pre2 receiver circuit and allow short, monotonic local joins. No column multiplexing or additional read subphases are introduced.

The local bit-line pitch stays at 0.66 µm, plus a 1 µm corridor per 16 lines: **0.7225 µm average native pitch**. Subbanks repeat every 100 µm including supplies and separation. The full-bank width divided by 1,280 lines is 0.784375 µm, including edge and group overhead. Metal2/3/4 joins connect the native-pitch bit lines to the staggered receivers.

This is the patent's stored-address branch: four mask-programmed access NMOS per four-bit selection, followed by a precharge device, keeper and restoring inverter per bit. It does not measure the direct one-access-transistor product-selection embodiment. Shared numerical products remain downstream; representative, activation and accumulator precision are unchanged.

## Measured area and verification

| Physical scope | Dimensions (µm) | Area (mm²) | µm²/selection | Selected DRC | Real bits checked | LVS |
|---|---:|---:|---:|---:|---:|---|
| W6 corrected 64-row slice | 1004 × 234.17 | 0.23510668 | 11.479818 | 0 | 81,920; zero mismatches | 87,040 devices; unique match; negative rejected |
| W6 full 1,280-row bank | 1004 × 2258.81 | 2.26784524 | 5.536732 | 0 | 1,638,400; zero mismatches | 1,643,520 raw devices; unique match; negative rejected |
| W5 1,280-row bank | 4669.7 × 2249 | 10.5021553 | 25.640028 | W5 evidence | W5 evidence | Outside this W6 check |
| W5 four-bank 320-row assembly | 4669.7 × 2664 | 12.4400808 | 30.371291 | W5 evidence | W5 evidence | Outside this W6 check |
| W5 twenty-tile 64-row assembly | 4669.7 × 4780 | 22.3211660 | 54.495034 | W5 evidence | W5 evidence | Outside this W6 check |

Measured area covers cells, analog receivers and physical local/common wires. **Output escape from the stacked receiver pins is unfinished.** Placed decoder and WL/PC drivers, phase control, latches, downstream products and accumulation, and complete PDN also remain outside the measured footprint. W5's single 64-row tile was 50.162793 µm²/selection; the 54.495034 assembly figure includes intertile gaps.

Selected DRC uses official GF180 FEOL, BEOL, connectivity and off-grid checks, excluding density and antenna. This is not foundry signoff. Independent readback decodes the original packed K64 tensor and checks programmed Via1 positions in reopened GDS. LVS compares the extracted circuit with an independent source-derived schematic, with bijective name normalization and exact device, connectivity and W/L checks. The negative control doubles one precharge width; it must be rejected even if Netgen still prints its topology-match phrase. The standard GF180 Netgen setup merges parallel/series devices; full-bank comparison reduces both circuits to 827,201 devices. The separate exact graph/W/L comparison checks all 1,643,520 raw devices before that reduction.

The first 64-row revision failed with **160 DRC markers**: 80 Metal3 spacing and 80 Via4 enclosure errors. Revision 2 shifts receiver origins 0.09 µm right and the lower ground-via rail 0.4 µm up. Indices and transistor dimensions are unchanged. The [failed revision](r64-v1/) and [original generator](scripts/build-v1.py) are preserved.

## Extracted timing and energy

Official capacitance export covers the full bank. All 1,643,520 MOS lines are byte-identical to the LVS export; the producer stream and decompressed artifact have identical SHA256 hashes. Ranking all 1,280 bit lines by incident metal capacitance times geometry-derived resistance selects **column 1153**, group 9/local column 1. It has 680.09041 fF incident metal capacitance and 682 connected drains. This is a load-based candidate, not proof of the slowest transient over every address, coupling state and process variation.

For this candidate, full-bank and cropped-subbank extraction have **exactly the same 2,632 incident capacitor pairs and 680.09041 fF sum**. That equality applies to column 1153, not the whole bank or every neighboring column.

The candidate's local electrical model has 16 actual full-height columns, all 128 physical receivers, 112 ideal legal-state bit-line aggressors, extracted stock WL/PC drivers, extracted MOS/capacitance and geometry-derived wire resistance. Metal resistance scales with temperature. Output load is assumed to be 10 fF. It is not automatic distributed-R extraction or a full-bank simultaneous-current simulation.

| Local slice corner | Tested cycle (ns) | Worst sampled settle after WL command (ns) | Failed 20 ns capture probes | Partial slice source energy (pJ/read) | Column 1153 receiver MOS energy (pJ/read) |
|---|---:|---:|---:|---:|---:|
| TT, 3.30 V, 25 °C | 60 | 15.415282 | 0 / 160 | 105.762761 | 7.936138 |
| SS, 2.97 V, 125 °C | 60 | 23.443325 | 18 / 160 | 84.441125 | 6.135770 |

Both simulations converged and passed all final output, raw-bit-line, precharge and phase checks. These are sampled near/far and data-dependent reads, not exhaustive timing. Recorded trace spacing is approximately 0.2 ns; the displayed calculation digits do not imply equivalent physical precision. **The 20 ns capture aperture fails at SS.** Interleaving cannot remove that latency failure; the existing INDEX path needs separately verified clock/phase changes or a completion interface. See [INTEGRATION.md](INTEGRATION.md).

The preserved pilot, column 273, settles in 15.211376 ns TT / 23.376321 ns SS. A separate maximum-connected-drain candidate, column 1015 with 714 drains, was also tested with its neighboring columns: 14.340919 ns TT / 22.401374 ns SS, passing the sampled 60 ns protocol. It is distinct from the metal-capacitance/resistance candidate. W5's latest tall-bank result is 14.676 ns TT / 24.351 ns SS at a 60 ns tested interval; the earlier 3–4.4 ns result was its 64-row slice. Different electrical scopes and row sequences prevent a direct speed or energy improvement claim.

### Shared-control loading exposes a 60 ns failure

A separate SS sensitivity adds the full-bank extracted WL/PC incident metal capacitance and all 1,280 intrinsic gate loads, retaining one stock buffer per control. It models rails with ten geometry-derived RC nodes. Added mutual capacitance is collapsed to ground, and remote MOS terminals are simplified. This is a control-loading sensitivity, not native distributed-R extraction, a conservative bound, or full-bank current/PDN qualification. The drivers are unplaced.

**The original 60 ns protocol fails this sensitivity:** 63 precharge checks and all 10 phase checks fail, although the final output/raw samples pass. The observed 32.353378 ns settling and 322.286159 pJ partial source energy are diagnostics of a failed protocol, not qualified read performance. Its 20 ns capture probe also fails 80 of 160 bit checks.

Measured worst control-transition delays are 21.553378 ns for PC rising to 90%, 12.105346 ns for PC falling to 10%, and 7.125652 ns for WL falling to 10%. A separate 120 ns guarded SS sequence passes with the identical circuit: PC turns off at 30 ns, WL is commanded at 55 ns, the first capture is at 102 ns, WL falls at 105.8–106 ns, and PC returns low at 119.8 ns. It has zero data, raw-bit-line, precharge and phase failures, 31.688382 ns worst sampled settling, and 149.860013 pJ of partial source energy per commanded read. Its 20 ns aperture still fails 80 of 160 bit checks. The TT companion was stopped at approximately 869.810 ns of its 1,200 ns transient when the 22.2 GiB guard observed 22.132843 GiB free. It has no final trace or timing/energy result: this is a resource abort, not demonstrated convergence or electrical failure. The original native process was not restarted, and its waiting parent was resumed and reaped it. This establishes only the tested interval in the stated sensitivity model, not a minimum cycle time or complete macro timing.

### Energy scope

Energy is finite-window net source energy over the repeated sequence. Signed ideal-aggressor work is retained. The per-column meter covers the candidate's four receiver MOS supply/well currents, including device-model junctions; it excludes explicit VDD-coupling-capacitor current and shared control/aggressor energy. Candidate 1153 is not the maximum-energy column in the sampled group.

**Complete 1,280-bit row energy remains unknown.** Partial slice or per-receiver energy must not be scaled and labeled a measured full-row result. Exact source components, sequence, endpoint discrepancies, decks and traces are in [timing evidence](timing/RESULTS.md); independent checks are under [audit](audit/).

## Whole-model extrapolation and October comparison

The uniform-density extrapolation is:

`31,457,280 selections × 5.536731543 µm²/selection ÷ 1,000,000 = 174.170514 mm²`

This is an engineering extrapolation from the measured rectangular bank, not a whole-model layout. It does not allocate the 98 tensor shapes, padding, extra ports, replicas, tied-table transpose access or whole-chip wiring.

The October component budget has 153.833 mm² of base arrays and 11.004 mm² of receiver strips: 164.837 mm² combined. Its other terms are 25.002 mm² decoder, 30.369 mm² WL drivers, 0.269 mm² PC drivers and 0.944 mm² bank selectors, totaling another 56.584 mm². The old total is 221.421 mm², approximately 154 mm² cells plus 67 mm² periphery.

W6's integrated array/readout/local-wire extrapolation is 9.333514 mm² above the old array-plus-receiver subtotal. Adding the older nonreceiver terms gives **230.754514 mm²**. This mixed estimate retains the old utilization and allocation assumptions and is neither placed nor a complete macro. The old 11.004 mm² receiver term is not added again.

The 78.4% saving therefore applies to W5's physically stretched bank, not the October idealized component budget. A complete recognizer, die fit and sub-watt operation remain unproved.

## Final handoff and remaining scope

- [Full bank GDS](r1280-v2/bank.gds), [geometry](r1280-v2/geometry.json), [selected DRC](r1280-v2/drc-result.json), [bit readback](r1280-v2/readback.json).
- [64-row GDS](r64-v2/bank.gds), [independent verification](verification/RESULTS.md), [geometry audit](audit/RESULTS.md).
- [Machine-readable results](results.json), [commands](COMMANDS.md), [source reading](READING.md), [baseline hashes](baseline/manifest.json).
- [Final independent audit](audit/FINAL-AUDIT.md), [artifact hashes](artifact-manifest.json).

The guarded 120 ns TT companion remains resource-incomplete; the passing SS follow-up and all completed primary G09 traces have been independently audited. Complete row energy, output escape, placed control circuitry and full-macro timing remain unfinished. Full-bank positive and negative LVS, bit readback, global capacitance ranking and local TT/SS characterization are complete. The full-bank extraction completed with native return code 0 in 3,122.505 s. Its recorded watchdog was extended to a 5,400 s bound; Magic was never restarted. A separately configured connectivity-only fallback became redundant and was cancelled with its own retained receipt. The successful original extraction supplies both LVS and the capacitance export. All W6 writes stay inside this workspace, W5 remains read-only, and the run uses no git or cloud, at most four CPU threads, and a 22 GiB free-disk guard.

Large idle extraction and SPICE evidence was losslessly compressed only after no-reader checks, with independent decompressed SHA256 verification before removing the raw copies. Historical command receipts retain their original paths; [restoration instructions](COMMANDS.md) identify the corresponding archives. The resource-aborted TT deck, simulator log and guard receipt are retained. No W6 compute remains active.

W6-STATUS: Final partial handoff: area, selected DRC, independent LVS with negative controls, and real-bit readback complete; sampled primary TT/SS timing complete; whole-row energy and full-macro timing unproved.
