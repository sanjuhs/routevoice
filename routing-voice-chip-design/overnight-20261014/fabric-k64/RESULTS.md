# W2b — complete K64 logic verified; physical trial incomplete

Both full 1280×320 projection variants pass RTL and synthesized-netlist functional verification. Neither has a routed, extracted, signoff-complete result. SC-ROM stopped under the requested local runtime forecast; ARRAY-PORT stopped at its preserved guard boundary. No supported MHz, routed area, dynamic/leakage power or projection energy is claimed. This is a bounded incomplete physical result, not proof that the architecture is infeasible.

| Required result | SC-ROM — standard-cell comparator | ARRAY-PORT — index macro excluded |
|---|---|---|
| Identity/coverage | All 409,600 coefficients, 6,400 books / 102,400 representatives and source metadata verified | Same |
| RTL correctness | 54 vectors; 17,280 integer and 17,280 FP32 outputs; four mid-vector resets; 104,112 stalls | Same |
| Mapped functional replay | 54 vectors / 17,280 FP32 outputs; four resets / 104,112 stalls; PASS | Same; zero-delay functional cells, not routed/SDF |
| Weight boundary | All indices, books, zero points, scales and biases on-chip | Books/metadata on-chip; 1,638,400 index bits and custom periphery excluded |
| Synthesis | 436,025 cells; 8.255467 mm² summed cell area | 318,683 cells; 6.137031 mm² summed cell area |
| Routed footprint | Not obtained | Not obtained; 15.5185 mm² die floorplan is not a routed result |
| State / other mapped cells | 0.824662 / 7.430805 mm² | 0.743176 / 5.393854 mm² |
| Fabric / arithmetic / periphery / routing split | Not separately recoverable from flattened mapping; routing unmeasured | Same; custom macro/periphery additionally uncharacterized |
| Timing | 20 ns initial target; no extracted corner or achieved MHz | Same |
| Cycles / latency | 4,160 integer; 4,163 FP32 cycles, excluding start. 83.26 µs at target only | Same; achieved µs remains unknown |
| Activity evidence | One saved real-vector RTL VCD; no final activity-annotated power | Mapped SAIF: 320 outputs pass; 1,253,320 annotated / 0 unannotated pins (28-openroad-globalplacement; not final routed netlist) |
| Power / energy | Extracted dynamic/leakage mW and energy unavailable | Same; early default-power diagnostic below is not a supported operating point |
| Power grid | Not reached | Generated PDN checker: zero violations; no IR/EM or routed signoff credit |
| Magic DRC / KLayout DRC / Netgen LVS / antenna | Not reached | Not reached |
| Last completed physical step | `11-openroad-checkmacroinstances` | `31-openroad-stamidpnr` |
| Local stop | Forecast exceeded ~2.5 h local SC-ROM budget; see sc_rom-v2-budget-stop.json | bounded runtime limit |
| Cumulative physical runtime | 2950.921 s (49.18 min) | 14401.928 s; two-second guard polling |
| Layout PNG | No placed SC layout | [Actual global-placement preview](evidence/array_port-placed.png), not routed |

Synthesis reports zero unmapped cells, zero inferred latches and zero synthesis check errors in both variants. There are 397 lint warnings; this is not a warning-free lint result. The exact sequential/nonsequential partition above is not an architectural fabric/arithmetic split. SC-ROM minus ARRAY-PORT cell area is not a measured custom-array area.

ARRAY's final printed repair counter was 150,000 of 321,396 nets examined, with 3,181 nets repaired, 8,876 buffers and 7,992 resized cells. Those are unfinished in-memory counters, not final area or a saved repaired database. The [repair log](runs/array_port-v2/32-openroad-repairdesignpostgpl/openroad-repairdesignpostgpl.log) and [stop receipt](evidence/array_port-v2-bounded-stop.json) retain the failure boundary and confirm no live flow process remained. The [continuation recipe](ARRAY-CONTINUATION.md) has not been executed.

The ARRAY floorplan has a 15.3379 mm² core and 6.5831 mm² initial placed cells, utilization 0.4292. Routing overhead and final buffer/CTS area are unknown. The custom index array needs its own layout, decoder/sense/read circuits, DRC/LVS, extracted electrical model and integration accounting.

## Identity and declared test scope

Selected executable model SHA-256: `34c9568cface06242b3b215c4bce01f3b48144e53342addc1c3d5c3603e72ffc`. Selected `val_89_quantized`: `3bdff3a2320a13083aafdb04a166061bd014226698421d6533a59fd9ee67f8a0`. Packed indices: `864fcdc7ec80be2dbb99d76361db338345fb02a1a26d7aaa4a1b40696b921907`. Book bytes: `4c0fe5e44202ef5a2479440c1108b187568b75bdeaad77216d792ea49fec4a49`. Full manifest, zero-point, scale, bias, unpacked-index and original-model hashes are in [identity.json](evidence/identity.json).

The independent dense NumPy reference reads the selected executable tensor bytes and zero points, not generated RTL. It matches 16,960 saved integer outputs and 17,280 saved affine outputs; the independent scheduled shared-partial reference checks 17,280 outputs. Both RTL suites additionally check 17,280 integer and 17,280 FP32 results. Reset tests interrupt LOAD, INDEX, ACCUM and OUTPUT. Tests do not constitute exhaustive formal equivalence. The separate numerical-bound audit proves actual-matrix accumulator bounds for centered inputs [-255,255].

The preserved pre-codebook original differs at 291,832 coefficient positions and 13,239 tested integer outputs. Exactness is to the approved frozen executable K64 tensor; it is not bit-exact to the pre-codebook model. Four-bit index, UINT8 representative, signed 9-bit activation, 13-bit shared partial, 17-bit product and 27-bit accumulator are separate widths.

The mapped ARRAY monitor originally lost its OS exit receipt in a JSON read race. Its recovered functional completion is supported by the full PASS line, normal `$finish` and Verilator statistics; the unavailable OS exit status stays null. SC mapped replay has exit 0. See [gate-correctness.json](evidence/gate-correctness.json) and original logs.

## Timing and power limitations

The requested extracted corners are nominal/minimum/maximum RC crossed with TT 25°C / 3.3 V, SS 125°C / 3.0 V and FF −40°C / 3.6 V. **All nine extracted corner results are unavailable.** Constraints are 20 ns clock, 4 ns input/output delay, 72.91 fF output load, inv_1/ZN driver, 0.25 ns uncertainty, 0.15 ns transition and 5% timing derating. ARRAY's external-port constraint does not prove an actual readable-cell macro meets the access budget.

Before placement repair, ARRAY TT setup WNS was −20,104.754 ns with 629,116 slew and 1,751 capacitance violations. The worst path begins at `array_row[6]` (4,074 loads), then a decode net with 4,428 loads. Such out-of-range early delays cannot be inverted into a supported MHz. Earlier pre-PNR nominal-RC TT/SS/FF WNS values were −9,371.144 / −20,829.494 / −4,784.200 ns; SC's partial TT pre-PNR WNS was −10,538.787 ns. These are diagnostic failures, not extracted results.

The same unrepaired ARRAY stage reported default-activity total 7,327.49 mW (internal 7,235.51 mW, switching 91.9533 mW, leakage 0.019454 mW). It precedes CTS and routing and extrapolates through severe electrical violations; it is not a validated projection power budget. No energy is derived from it. Full reports are preserved in [pre-route-diagnostics.json](evidence/pre-route-diagnostics.json).

The SC mapped-SAIF compilation attempt stopped at the 22 GiB disk-headroom guard and produced no valid trace. Its failed compiler outputs and logs are preserved; it has no activity pass credit. The ARRAY mapped SAIF uses saved real-activation vector 0 (1,280 codes, min −1, max 11, 565 zeros), not a fresh speech capture. Its 83.32 µs window includes 60 ns reset/start overhead beyond 4,163 target cycles. It is a zero-delay functional-cell trace, without SDF glitches, a long speech stream, idle or peak characterization. Coverage must be checked again after repair/CTS/routing adds cells. `power.tcl` is an unexecuted post-route recipe; no recipe receives result credit.

## Reproduction and next bounded step

[COMMANDS.md](COMMANDS.md) contains exact commands and recovery history. [results.json](results.json) contains machine-readable results and explicit nulls. [CLOUD-REQUEST.md](CLOUD-REQUEST.md) provides the exact SC-ROM file manifest and pinned commands for the lead; this worker launched no cloud resource and incurred no cloud spending. The source/config/vector/document manifest and PDK/cloud payload hashes are under `evidence/`.

Tools: LibreLane 3.0.11 commit `33ab64861c5570d65de69295da9a46f5bad32ee3`; physical Yosys 0.62 commit `7326bb7d6641500ecb285c291a54a662cb1e76cf`; OpenROAD `dcf36133a369abc8f3c5e5738cd4d82e4903c0e0`; OpenSTA 2.7.0; Verilator 5.050 (2026-07-01). PDK: GF180MCU-D, open_pdks `54435919abffb937387ec956209f9cf5fd2dfbee`, standard cells `5641d172662a7d9086e5b99c5d54506c05e65cee`. Complete component revisions and actual view hashes are in `evidence/pdk-source-revisions.json` and `evidence/physical-view-hashes.json`. Magic/KLayout/Netgen have no executed signoff result here.

Preserve the existing complete projection checkpoint and resume it only within a new bounded physical phase. If high-fanout repair continues to dominate, test explicit local row/decode distribution while retaining the entire matrix and precision contract, then repeat correctness and physical accounting. The integrated KLayout runset resolves null; the supplied standalone official-deck launcher must actually run on final GDS before claiming KLayout DRC.

The four-hour ARRAY cap includes its interrupted v1 attempt. A proposed six-hour monitor extension was withdrawn before taking effect. SC stopped earlier on the requested forecast. Initial temporary-directory and monitor failures remain logged. Completed duplicate artifacts were losslessly archived or APFS-compressed with verified byte hashes. Final observed root free space: 24.43 GiB. Active inputs/outputs stayed internal; no original model artifacts, frozen retained experiments, sibling workspace, git history or cloud resources were changed by this worker. The initial v1 Nix TMPDIR reset exception under `/tmp` is explicitly retained in COMMANDS.md.

Package pads, upstream activation quantizer, dynamic attention, writable whole-model state and complete recognizer are outside this projection boundary. This result establishes neither one-die fit nor sub-watt STT.
