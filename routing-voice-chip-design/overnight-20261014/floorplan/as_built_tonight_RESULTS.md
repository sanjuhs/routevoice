# W3 whole-chip floorplan

## Measured-input floorplan

Input snapshot: **20261013T212403Z**. Final report: 2026-10-13T21:24:04.018697+00:00

**The current measured-bank construction does not fit one 26 × 33 mm die, or two such dies.** The main 320-row/open-SRAM/no-numerical-change budget is **2,003.46 mm² of blocks**, before chip pads and placement space. A 26 × 33 mm maximum field is an explicit planning assumption, not a GF180 foundry-approved limit. The diagnostic one-die outline is **44 × 53 mm**; the balanced two-die option is **32 × 38 mm per die**. These oversized abstract layouts test placement and power distribution; they are not manufacturable-die or working-recognizer claims. At least three assumed reticle fields are needed by block area alone; a three-die implementation has not been placed or validated. Smaller cells, denser memory, revised fanout and numerical levers remain scenarios, not established solutions.

### Completed placement and power screens

| Case | Outline mm | Block mm² | Core utilization | Assumed W | Supply pairs / signal pads | VDD drop mV | VSS rise mV | Combined loss | Result |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| One die | 44 × 53 | 2003.46 | 91.2% | 1.080 | 28 / 16 | 79.2 | 57.2 | 4.13% | PASS |
| Two-die A | 32 × 38 | 1011.27 | 90.4% | 0.666 | 20 / 16 | 80.3 | 69.9 | 4.55% | PASS |
| Two-die B | 32 × 38 | 1012.46 | 90.5% | 0.644 | 32 / 16 | 60.2 | 53.4 | 3.44% | PASS |

PASS requires independent halo/boundary checking, VDD and VSS `check_power_grid`, both IR solves, the sum of worst VDD drop and worst VSS rise below 165 mV, and zero detected opposite-net overlaps in special wires, macro pins and via enclosures. The two extrema need not coincide; their sum is a conservative bound. Geometry checking excludes IO internals and is not DRC.

Preserved first one-die attempt: connected grids, but 20 µm straps gave 182.5 mV combined loss (5.53%), **FAIL**. The selected revisions use40 µm straps. Die B additionally uses 32 supply-pad pairs after 40 µm/16 pairs still failed at 191.9mV (5.82%). Initial two-die A/B cases also failed at 203/227mV (6.15%/6.88%) and are retained in their unsuffixed run directories. See its [original log](logs/measured320_sram_open_macro_off_baseline_whole_44x53mm.log).

The minimum is within a declared search: integer-mm rectangles, width 18–60 mm, height up to 64 mm, width ≤ height, aspect ratio ≤ 33/26, deterministic descending-height shelf placement, 700 µm pad/core margin and 30 µm macro halos. It is not a global optimum. The minimum-area feasible outlines were chosen geometrically before EDA; no old assumption-driven EDA size sweep was repeated.

Two-die A/B use deterministic area-balanced abstract tile assignment, recorded by instance in each manifest. The historical CLI partition names `encoder`/`decoder` mean **A/B here**, not an implemented encoder/decoder architectural boundary. Each gets a complete shared-product engine plus a 4 mm²/40 mW assumed link interface. Memory ownership, cross-die row/codebook traffic, scheduling and link bandwidth need implementation. Total two-die block area includes the extra engine and 8 mm² link allowance.

### Renders and physical artifacts

- **One die:** [OpenROAD PNG](runs/measured320_sram_open_macro_off_baseline_whole_44x53mm_pdn40/floorplan.png), [IR heatmap](runs/measured320_sram_open_macro_off_baseline_whole_44x53mm_pdn40/ir_heatmap.png), [DEF](runs/measured320_sram_open_macro_off_baseline_whole_44x53mm_pdn40/floorplan.def), [ODB](runs/measured320_sram_open_macro_off_baseline_whole_44x53mm_pdn40/floorplan.odb), [Tcl](runs/measured320_sram_open_macro_off_baseline_whole_44x53mm_pdn40/floorplan.tcl).
- **Two-die A:** [OpenROAD PNG](runs/measured320_sram_open_macro_off_baseline_encoder_32x38mm_pdn40/floorplan.png), [IR heatmap](runs/measured320_sram_open_macro_off_baseline_encoder_32x38mm_pdn40/ir_heatmap.png), [DEF](runs/measured320_sram_open_macro_off_baseline_encoder_32x38mm_pdn40/floorplan.def), [ODB](runs/measured320_sram_open_macro_off_baseline_encoder_32x38mm_pdn40/floorplan.odb), [Tcl](runs/measured320_sram_open_macro_off_baseline_encoder_32x38mm_pdn40/floorplan.tcl).
- **Two-die B:** [OpenROAD PNG](runs/measured320_sram_open_macro_off_baseline_decoder_32x38mm_pdn40_pads32/floorplan.png), [IR heatmap](runs/measured320_sram_open_macro_off_baseline_decoder_32x38mm_pdn40_pads32/ir_heatmap.png), [DEF](runs/measured320_sram_open_macro_off_baseline_decoder_32x38mm_pdn40_pads32/floorplan.def), [ODB](runs/measured320_sram_open_macro_off_baseline_decoder_32x38mm_pdn40_pads32/floorplan.odb), [Tcl](runs/measured320_sram_open_macro_off_baseline_decoder_32x38mm_pdn40_pads32/floorplan.tcl).

[Two-die OpenROAD layout](measured_two_die_floorplan.png), [two-die heatmap](measured_two_die_ir_heatmap.png). Heatmaps show actual OpenROAD per-macro terminal voltages under assumed static loads; macro-internal gradients are absent. All block LEFs are generated abstracts, not routed recognizer internals.

### Block-area ledger: selected 320-row/open-SRAM scenario

| Block | mm² | Assumed W | Measurement / assumption and source |
|---|---:|---:|---|
| frontend_FP32 | 158.049 | 0.150 | MEASURED coefficient count; ASSUMED binary ROM1.76 um2/bit x1.25 and 12 mm2 frontend logic; `overnight-20261014/storage-inventory/inventory.json` |
| encoder_fabric_L0 | 37.320 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| encoder_fabric_L1 | 37.320 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| encoder_fabric_L2 | 37.320 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| encoder_fabric_L3 | 37.320 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| encoder_fabric_L4 | 37.320 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| encoder_fabric_L5 | 37.320 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| decoder_fabric_L0 | 55.980 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| decoder_fabric_L1 | 55.980 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| decoder_fabric_L2 | 55.980 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| decoder_fabric_L3 | 55.980 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| decoder_fabric_L4 | 55.980 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| decoder_fabric_L5 | 55.980 | 0.025 | MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED; `overnight-20261014/taalas-array/results.json and current model ledger` |
| embedding_head_tied_once | 318.466 | 0.080 | MEASURED count; ASSUMED transfer of projection-bank geometry to tied/transposed head access; `current model ledger; overnight-20261014/taalas-array/results.json` |
| producer_KV_and_positions | 77.129 | 0.040 | MEASURED count; geometry transfer ASSUMED; `current model ledger` |
| codebooks_and_other_metadata | 146.074 | 0.035 | MEASURED K64 slots and native metadata totals; ASSUMED binary ROM density; engine embedded books retained as conservative cache duplication; `overnight-20261014/storage-inventory/inventory.json; K64 domain count` |
| shared_product_engine | 12.274 | 0.150 | MEASURED synthesis / ASSUMED 0.5 utilization; `overnight-20261014/fabric-k64/results.json` |
| encoder_dynamic_attention | 18.000 | 0.075 | ASSUMED dynamic-only logic allowance; fixed projection replaced by shared engine; `W3 explicit allowance; no full-top mapped logic evidence` |
| decoder_dynamic_attention | 15.000 | 0.060 | ASSUMED dynamic-only logic allowance; fixed projection replaced by shared engine; `W3 explicit allowance; no full-top mapped logic evidence` |
| producer_dynamic | 6.000 | 0.030 | ASSUMED dynamic-only logic allowance; fixed projection replaced by shared engine; `W3 explicit allowance; no full-top mapped logic evidence` |
| control_clock_IO_interface | 12.000 | 0.060 | ASSUMED dynamic-only logic allowance; fixed projection replaced by shared engine; `W3 explicit allowance; no full-top mapped logic evidence` |
| array_decoder_phase_mux_allowance | 56.584 | 0.020 | ASSUMED transfer of October placed-footprint estimates; omits receiver strips already in W5 array. Not complete macro bound; `docs/TAALAS-TALL-BANK-BUDGET.md` |
| mutable_arrays | 593.838 | 0.060 | MEASURED inventory/LEF x ASSUMED banking and 10% internal placement allowance; `overnight-20261014/storage-inventory/inventory.json; memory_allocation.json; SRAM LEFs` |
| ordinary_registers | 30.242 | 0.020 | MEASURED bit count/63.6608 um2 DFF; ASSUMED50% utilization. Conservative duplication versus engine/control internals not subtracted; `overnight-20261014/storage-inventory/inventory.json; gf180mcu7t dffq_1 Liberty area` |

All 31,457,280 immutable selections are counted once; the tied head/embedding is counted once. K64 book allocation reserves 491,520 domains × 16 UINT8 slots = 7,864,320 B, a derived padded capacity. October reports 7,765,892 used representative bytes; padding is not new model content. Native per-projection coefficient ROM formats are replaced by selections/books, not added as SRAM. Native metadata totals are 368,640 readmem metadata B + 61,440 producer/norm case-ROM B + 5,270.5 small case-ROM B = 435,350.5 B. Frontend coefficients remain 8,298,240 B of FP32 binary ROM. Other native coefficient bytes are not added again.

Inventory source reports 28,641,280 newly on-chip ROM B plus 8,852,630.5 already-on-chip case-ROM B. These describe the elaborated native representation, not an extra memory allocation on top of Taalas weights. Ordinary registers are costed separately at 63.6608 µm² per `dffq_1` cell / 0.5 utilization. This can conservatively duplicate register area already embedded in engine/control allowances; no unsupported subtraction was made.

### Mutable memory replaces both reserves

**MEASURED inventory:** 8,501,818 array bits = 1,062,727.25 B, 144 declarations / 321 instances; 237,524 ordinary register bits = 29,690.5 B. Source is Verilator elaboration of the merged all-on-chip top, 30,542 instances, not a Yosys mapped-memory result. Both old reserve blocks are removed; no ungrounded conservative reserve row remains.

The [per-array allocation](memory_allocation.json) preserves each declaration instance and ceil(width/8) byte lanes, flattens array dimensions, and chooses the least-area homogeneous depth banking among the real 64/128/256/512×8 LEFs. This yields **2,892 macros**, **1,210,112 allocated bytes**, **539.853 mm²** of measured LEF rectangles and **593.838 mm²** after an assumed 10% internal placement allowance. Single-port compatibility, simultaneous accesses, bank muxes and RTL replacement are not proven. Small arrays can be inefficient in these macros; no free cross-array packing was assumed.

Research memory uses 0.9479839488 mm² per 4,096 B, independently capacity-rounded per instance: 553.717 mm² with the same 10% allowance. The small research/open difference comes from many small instances wasting large banks; it is not a contradiction in bit density. Dense custom uses an assumed effective 12 µm²/bit plus 10% group placement allowance: 112.224 mm². Its effective density already includes cell periphery, and requires a compiled/characterized macro.

### Bank-height and engine evidence

| Bank rows | Measured partial assembly µm²/selection | Whole-model partial array mm² | Timing qualification |
|---|---:|---:|---|
| 64 | 54.495034 | 1714.266 | Ideal-driver sampled64-row slices; no integrated macro timing |
| 320 | 30.371291 | 955.398 | 40 ns sampled TT/SS pass;20 ns fails; full macro unproved |
| 1,280 | 25.640028 | 806.566 | 60 ns sampled TT/SS pass;40 ns untested; full macro unproved |

Cell-only W5 geometry is 4.8684604443 µm²/selection ≈153.15 mm² whole-model. The 64-row partial assembly is 22.321166 mm² /409,600 selections; 320-row is 12.4400808 mm²; 1,280-row is 10.5021553 mm². These GDS bounding boxes already include local readouts and fanout. Cell-only area is not added again. Density transfer across all 98 matrix shapes and tied-table access is assumed; matrix-by-matrix padding and pin-access implementation are not measured. The 320-row sampled slice passes40 ns and 60 ns protocols at TT/SS and fails20 ns at both (SS:116 output/100 raw failures; TT:14 output/8 raw failures); The 1,280-row slice now passes60 ns at TT/SS but has no passing 40 ns result; it is not selected for the 25MHz 40 ns interval. Neither meets a complete-macro timing contract, so “tallest bank meeting timing” is currently **unestablished**. Consult the frozen timing JSON and final hash check for subsequent changes.

October’s tall-bank budget sums 153.833 mm² base arrays,11.004 receiver strips and 56.584 digital decoder/driver/selector footprints, about 221.421 mm². It is a component sum, with assumed digital placement utilization, not a joined layout. W5’s joined layout retains a128-channel horizontal receiver strip/fanout that fixes a4669.7 µm assembly width; most array columns are much narrower. Increasing bank height reduces receiver replication but retains that unused width. Thus its955.116 mm² 320-row whole-model extrapolation is much larger before missing global periphery. W3 carries the 56.584 mm² October digital subtotal only as an explicit transfer allowance; it is not proof of complete decoder/phase/mux/latch cost.

Engine arithmetic:409,600/4,163 = 98.391 MAC/cycle. At assumed 25 MHz, one engine supplies 2.460 GMAC/s; ceil(2×0.6/that) = **1 engine**. The 2× margin targets1.2 GMAC/s. W2b ARRAY-PORT measures6.137030637 mm² synthesized cells including local books/FP32 output. Routed footprint is null, so this screen uses **12.274061274 mm² = cells/0.5**, explicitly assumed utilization. W2V2’s≈5.28 mm² is a comparison, not substituted. The 25 MHz clock itself is not timing-closed, and shared row buses across all layer groups remain architectural assumptions. Extra stalls, global buses, head transposition and contention can invalidate this throughput estimate. Workload assumption is about 368.5M encoder MAC/s (7.37M×50frames/s),86M decoder MAC/s (21.5M×4tokens/s), plus producer and other work to the 0.6G envelope.

### Area sensitivity: selection × memory × levers

All totals are mm² of blocks, before chip pads/halos/outer placement whitespace. All six selection scenarios use the same explicit 56.584 mm² digital-periphery allowance; this is deliberately conservative for SC-ROM, whose synthesis difference already includes local selection logic. These are area models, not additional completed EDA runs.

| Selection scenario | Memory | Levers off | Levers on |
|---|---|---:|---:|
| stdcell | sram_open_macro | 1373.45 | 1230.15 |
| stdcell | sram_4k_research | 1333.33 | 1216.80 |
| stdcell | sram_dense_custom | 891.84 | 793.20 |
| custom7 | sram_open_macro | 1324.89 | 1157.30 |
| custom7 | sram_4k_research | 1284.76 | 1143.94 |
| custom7 | sram_dense_custom | 843.27 | 720.35 |
| optimistic3_5 | sram_open_macro | 1185.69 | 948.51 |
| optimistic3_5 | sram_4k_research | 1145.57 | 935.15 |
| optimistic3_5 | sram_dense_custom | 704.07 | 511.56 |
| measured64 | sram_open_macro | 2762.33 | 3313.47 |
| measured64 | sram_4k_research | 2722.21 | 3300.11 |
| measured64 | sram_dense_custom | 2280.71 | 2876.52 |
| measured320 | sram_open_macro | 2003.46 | 2175.16 |
| measured320 | sram_4k_research | 1963.34 | 2161.81 |
| measured320 | sram_dense_custom | 1521.85 | 1738.21 |
| measured1280 | sram_open_macro | 1854.63 | 1951.92 |
| measured1280 | sram_4k_research | 1814.51 | 1938.56 |
| measured1280 | sram_dense_custom | 1373.01 | 1514.97 |

`stdcell`: (8.255466688−6.137030637) mm²/409,600 = **5.171963 µm²/selection** synthesized-cell differential, then /0.5 utilization. This paired-run difference is measured synthesis evidence, not an isolated selection macro or routed density. Mapping changes can affect the subtraction. `custom7` uses 7.04×1.25; `optimistic3_5` uses 3.5×1.25, both assumptions. Measured64/320/1280 use actual partial bounding boxes without another blanket periphery multiplier. Binary ROM uses the explicit 1.76 µm²/bit×1.25 assumption.

Levers on: frontend coefficients FP32→INT8 (2,074,560 B), books stored at selection density/4 per bit, and the actual compact self-attention `keys`/`values` arrays FP32→8-bit (168,960 B→42,240 B). Only those two measured KV arrays receive KV8 savings; committed history and arbitrary state do not. Frontend INT8 and KV8 **require model-accuracy re-validation**. Books-in-array retains numeric values but needs new read/access hardware. With today’s wide measured readout layout it increases book area, so the combined “on” case can be larger. No assumed accuracy or timing benefit is credited.

### Power and IO scope

Core voltage is 3.3 V, matching `gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30`. All listed watts are **ASSUMED**. W5 explicitly leaves full 320-lane read energy null; its new selected 16-active-column group includes 128 receiver channels and partial WL/PC drivers. At 40 ns the measured partial source sums are 51.344 pJ TT and 41.439 pJ SS, including finite-window charge-return effects; they are not full-row energies. Scaling that number to full-row energy would misrepresent the evidence. W2b workload power remains unannotated; its7.32749 W default/propagated estimate is recorded as an unqualified comparator and not silently used as speech power. Consequently this IR screen proves neither sub-watt operation nor worst-workload voltage margin.

Supply-pad pairs = ceil(2×P/(3.3 V×25 mA)), rounded up to a multiple of four; die B increases the 16 pair current-derived minimum to 32 pairs for IR. 25 mA and 2× current margin are assumptions. Actual GF180 `dvdd`, `dvss`, `bi_t`, corner and filler LEFs form abutting rings. Supply feeds use Metal2 to the Metal4/5 core ring; macro vertical Metal4 pins connect to the horizontal Metal5 grid. Core rings40 µm, straps400 µm pitch; all selected straps40 µm. Per-macro static current derives from its assigned power /3.3 V. Voltage sources are at transformed supply-pad terminals.

The technology LEF sheet/via resistances are screening values (Metal4 .09 Ω/square, Metal5 .06 Ω/square), not qualified extraction. Package/bond resistance, transient droop, EM and macro-internal resistance are absent. Supply connectivity is implemented; IO signal nets, configuration/tie controls, clock and recognizer signal routes are not. The artifact therefore has a connected **abstract supply pad ring**, not a demonstrated functional pad interface.

### Reproduction and provenance

[Input refresh audit](input_refresh_audit.json) verifies that newly snapshotted progress/timing updates do not change the actual areas, loads or engine footprint in the completed runs. See [MEASURED_COMMANDS.md](MEASURED_COMMANDS.md), [source hashes](results.json), [per-array allocation](memory_allocation.json), [blocks.json](blocks.json) and [machine results](results.json). All writes and active outputs remain inside this workspace. EDA runs use nice 10, at most4 threads, sequential execution, a22 GiB free-space guard and 600s/run guard. Original failures are retained. The earlier assumption-based report is preserved as [historical report](historical_pre_measured_RESULTS.md) and is superseded by this section.

Final sibling hash check: all frozen sources unchanged.
