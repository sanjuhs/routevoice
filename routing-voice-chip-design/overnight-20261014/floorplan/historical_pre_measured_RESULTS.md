# W3 whole-chip abstract floorplan and power distribution

Updated 2026-10-13T19:53:05.717466+00:00

**The abstract baseline places in 34 × 34 mm and its VDD/VSS grids pass connectivity and the 5% IR screen. This does not establish a complete RouteVoice recognizer on one manufacturable die.** The baseline omits uncounted private/KV state pending the full-top inventory; macros have no routed internals, and IO signals are not configured/routed. The 34-mm outline is a diagnostic geometry, exceeds the prior 900-mm² study budget, and has no foundry/reticle approval.

The most credible *available comparison* is custom 7.04 µm²/selection with 25% periphery, the actual open SRAM geometry, and numerical levers off. This preserves the selected model numerics and uses a concrete SRAM footprint. Neither custom selection density at full scale nor the periphery/logic allowances are qualified. The standard-cell measured selection-only result remains pending.

## Completed physical screens

| Case | Die mm | Block area mm² | Core utilization | Supply pairs / signal pads | Assumed W | VDD drop mV | VSS rise mV | Sum / 3.3 V | PDN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| whole | 34² | 924.75 | 87.2% | 24 / 16 | 0.930 | 69.1 | 64.5 | 4.05% | PASS |
| encoder | 25² | 488.52 | 87.8% | 16 / 16 | 0.545 | 81.0 | 75.6 | 4.75% | PASS |
| decoder | 25² | 444.23 | 79.9% | 12 / 16 | 0.465 | 73.3 | 58.0 | 3.98% | PASS |

The sum of separate worst supply drop and worst ground rise is a conservative bound; both are screened together against 165 mV. OpenROAD includes exactly the per-macro assigned load. These watts are assumptions, not measured speech-recognition power. Supply-pad count uses ceil(2 × P / (3.3 V × 25 mA)), rounded to a multiple of four; 25 mA and 2× margin are assumptions, not qualified pad/package current limits. Four real corner cells and abutting real filler cells are additional.

The deterministic shelf packer fails at the preceding integer-mm outline (33 mm for whole, 24 mm for each partition). That is a minimum within this packing policy, not a proof of globally minimum die size. Macro rectangles have 30-µm halos, and an independent rectangle check found zero overlaps. A separate geometry check found zero positive-area VDD/VSS overlaps in special wires, macro pins and via enclosures; it excludes IO internal layout and is not foundry DRC.

Two-die partition: frontend/encoder/producer with their ledger memories on die A; decoder, tied table, codebooks, history and global control on die B. Both receive an assumed 4 mm² / 40 mW link-interface allowance. Total block area is 932.75 mm² and assumed total power 1.010 W. Codebook/activation/metadata traffic across this partition, protocol bandwidth, package energy and timing are not implemented. It is a physical partition screen, not an operational two-die recognizer.

## Physical artifacts

- **whole**: [actual OpenROAD PNG](runs/custom7_sram_open_macro_off_baseline_whole_34mm/floorplan.png), [IR heatmap](runs/custom7_sram_open_macro_off_baseline_whole_34mm/ir_heatmap.png), [DEF](runs/custom7_sram_open_macro_off_baseline_whole_34mm/floorplan.def), [ODB](runs/custom7_sram_open_macro_off_baseline_whole_34mm/floorplan.odb), [Tcl](runs/custom7_sram_open_macro_off_baseline_whole_34mm/floorplan.tcl).
- **encoder**: [actual OpenROAD PNG](runs/custom7_sram_open_macro_off_baseline_encoder_25mm/floorplan.png), [IR heatmap](runs/custom7_sram_open_macro_off_baseline_encoder_25mm/ir_heatmap.png), [DEF](runs/custom7_sram_open_macro_off_baseline_encoder_25mm/floorplan.def), [ODB](runs/custom7_sram_open_macro_off_baseline_encoder_25mm/floorplan.odb), [Tcl](runs/custom7_sram_open_macro_off_baseline_encoder_25mm/floorplan.tcl).
- **decoder**: [actual OpenROAD PNG](runs/custom7_sram_open_macro_off_baseline_decoder_25mm/floorplan.png), [IR heatmap](runs/custom7_sram_open_macro_off_baseline_decoder_25mm/ir_heatmap.png), [DEF](runs/custom7_sram_open_macro_off_baseline_decoder_25mm/floorplan.def), [ODB](runs/custom7_sram_open_macro_off_baseline_decoder_25mm/floorplan.odb), [Tcl](runs/custom7_sram_open_macro_off_baseline_decoder_25mm/floorplan.tcl).

[Two-die heatmap](two_die_ir_heatmap.png). Heatmaps show per-macro terminal effective supply loss from the exported voltage CSVs, not macro-internal voltage gradients.

## Area scenario table

All totals below are conditional block-area models in mm², before the external pad ring/halo/placement whitespace. Each SRAM scenario additionally has 10% bank-group placement overhead. **SC rows still use the explicit 40 µm²/selection placeholder; they are not measured standard-cell results.**

| Selection | SRAM | Levers off mm² | Levers on mm² |
|---|---|---:|---:|
| stdcell (PLACEHOLDER) | sram_open_macro | 1906.21 | 2287.41 |
| stdcell (PLACEHOLDER) | sram_4k_research | 1789.66 | 2170.86 |
| stdcell (PLACEHOLDER) | sram_dense_custom | 1698.92 | 2080.11 |
| custom7 | sram_open_macro | 924.75 | 815.21 |
| custom7 | sram_4k_research | 808.20 | 698.66 |
| custom7 | sram_dense_custom | 717.45 | 607.91 |
| optimistic3_5 | sram_open_macro | 785.55 | 606.41 |
| optimistic3_5 | sram_4k_research | 669.00 | 489.86 |
| optimistic3_5 | sram_dense_custom | 578.25 | 399.11 |

Memory densities:

- `sram_open_macro`: **MEASURED-LEF**, 431.86 × 484.88 µm per 512 bytes = 0.2094002768 mm², 51.1231 µm²/bit. Per-bank source capacities are rounded independently.
- `sram_4k_research`: project research-bank footprint 0.9479839488 mm² per 4,096 bytes = 28.9302 µm²/bit; port/timing transfer unproved. Source: `docs/TAALAS-DIE-SIZE-AND-SYSTEM-COSTS-2026-10-02.md` and its linked bank evidence.
- `sram_dense_custom`: **ASSUMED** 12 µm²/bit effective, including approximately 40% periphery; a compiled/characterized macro is required.

Levers on means:

- `frontend_int8`: 2,074,560 INT8 bytes instead of 8,298,240 FP32 bytes; **requires model-accuracy re-validation**. Arithmetic area remains unchanged because no corresponding datapath was measured.
- `books_in_array`: 7,864,320 book bytes at selection density / 4 per bit, with the same periphery factor. Values are unchanged; physical readout needs implementation. This makes the SC placeholder case larger, rather than assuming every lever saves area.
- `kv8`: **requires model-accuracy re-validation** wherever applied. It reduces the explicitly assumed KV reserve fourfold only in `--state conservative`. Baseline has no measured retained-KV allocation to reduce, so it receives zero KV8 savings. Do not reclassify history or arbitrary SRAM as KV.

## Accounting and evidence boundaries

The baseline contains 601,280 logical bytes and 602,112 bytes after open-macro bank rounding from the current F64/history66 service ledger. `KV_retention_reserve` (983,040 B) and `private_state_reserve` (524,288 B) are excluded and remain only under `--state conservative`. The absence of `stat_mem.txt` means this baseline is an incomplete capacity inventory, not evidence that the full top needs only these bytes.

All 31,457,280 four-bit selection positions are accounted for: 7,372,800 encoder; 11,059,200 decoder; 10,485,760 tied embedding/head once; 1,228,800 producer K/V coefficients; 1,310,720 positional entries. Four-bit pointers do not change UINT8 representatives, activation widths, FP32 frontend or dynamic attention. Codebook payload, padded producer metadata, a 400,000-byte extra scalar-metadata allowance, dynamic arithmetic, control and clock/interface allowances remain separate.

Logic areas (12 mm² frontend, 30 encoder/dynamic attention, 25 decoder, 6 producer and 12 control/interface) are explicit assumptions pending measured ARRAY-PORT mapping. Binary ROM remains an assumed 1.76 µm²/bit × 1.25 periphery. Full-scale readable-cell periphery is assumed, not characterized.

Sibling files were re-read and hash-snapshotted under `inputs/`. W2b full 1280×320 SC-ROM/ARRAY-PORT physical figures are null. W2 320×320 figures are null. W2 64×320 has 4.229742 mm² synthesized cell area and a 9.537208 mm² allocated die, but it is a partial primitive with arithmetic and failed/unclosed timing at a different operating point. Its 465.684 µm²/position is not a measured selection-only density and is not transferred to this baseline. See `results.json` for exact snapshots.

## PDN implementation and qualification

Nominal 3.3 V standard-cell corner: `gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30`. Supply and return use 40-µm Metal4/Metal5 rings, 20-µm stripes at 400-µm pitch, and per-instance macro-grid connections to vertical Metal4 macro pins. Actual GF180 DVDD/DVSS pads expose the core-facing feed on Metal2; those feeds are connected to the ring with generated via stacks. Routing tracks must exist before PDN generation. Real signal pads, corners and filler cells abut around all four sides.

Voltage sources are supplied at transformed supply-pad pin locations via explicit CSVs, not ideal sources covering the whole core. Pad-internal rails are abstracted by LEF terminals. Bond wires, package/regulator impedance, transient droop, EM, temperature dependence, macro-internal supply resistance, and signal/clock routing are outside the model. The technology LEF itself warns its parasitics are not qualified extraction; IR uses its nominal sheet/via resistances (Metal4 0.09 Ω/square; Metal5 0.06 Ω/square). Passing this screen cannot be promoted to signoff.

The IO ring has verified abstract supply connectivity. Its signal pins and mode/tie controls are not connected into functional logic and no signal routes exist. Therefore a *working functional pad ring / recognizer* is not established by this artifact.

## Reproduction and preserved failures

Read [COMMANDS.md](COMMANDS.md). `make_floorplan.py` accepts selection, memory, lever, state and partition axes. `run_selected.py` runs sequentially at nice 10, four threads, a 600-second per-case guard and a 20-GiB free-space floor. All active PDK views and output are inside this workspace; no git or cloud was used.

Preserved failures include missing placement site, disconnected original horizontal macro-pin grids, and the Metal2 pad-feed trial that crashed before `make_tracks` was added. Interrupted attempts receive no pass credit. Old pre-guidance size-sweep artifacts under `runs/` include unmeasured state reserves and must not be used as the current baseline. Successful evidence is limited to the three named cases above and the small PDN connectivity probe.

Source basis: repository routing skill and complete supplied notes; primary patent descriptions/claims for shared products/readable cells, codebook pointers and shared ROM connections from the preserved US20250123802A1, US20260023566A1 and WO2025217724A1 texts; parent `plan.md`; approved physical-goal review gate; area documents and supplied current service ledger. Old pause text in the plan is superseded by the 14 October authorization.

Tool references: [OpenROAD PDN generator](https://openroad.readthedocs.io/en/latest/main/src/pdn/README.html), [OpenROAD IR analysis](https://openroad.readthedocs.io/en/latest/main/src/psm/README.html), [GF180 power-pad documentation](https://gf180mcu-pdk.readthedocs.io/en/latest/IPs/IO/gf180mcu_fd_io/power.html).
