# W5 tall-bank comparison

**The 320-row layout reduces the measured array/readout assembly from 22.3212 to 12.4401 mm² (44.3%).** Four striped banks replace twenty 64-row banks. The optional single 1,280-row bank measures 10.5022 mm². These are physical GDS bounding rectangles, including unused routing space, not receiver-count area estimates.

The table includes cells, physical precharge/keeper/inverter readouts and actual local joining/control/ground wires. **Global decoder/mux/control, physical WL/PC drivers, output latches and interbank PDN remain excluded.** A complete macro area and achieved ARRAY-PORT clock are not established.

| Rows/bank | Banks | Measured partial macro area, mm² | µm²/selection incl. local readout | Readouts | Worst sampled settling TT / SS, ns | Sampled energy TT / SS, pJ/read | Tested common reuse interval, ns | Conditional banks for 20 ns initiation |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 20 | 22.3211660 | 54.495034 | 25,600 | 2.976 / 4.390 | 77.709 / 62.275 | 20 | 1 |
| 320 | 4 | 12.4400808 | 30.371291 | 5,120 | not measured / 8.894 | not measured / not measured | not measured | not measured |
| 1280 | 1 | 10.5021553 | 25.640028 | 1,280 | not measured / not measured | not measured / not measured | not measured | not measured |

**Timing and energy scope:** TT is 3.30 V/25°C; SS is 2.97 V/125°C. Settling is measured after the WL command, and is the worst sample among passing retained protocols, not end-to-end macro latency. The 64-row baseline uses ideal drivers, extracted capacitance without distributed resistance, a 1.44 µm precharge device and 32 fully active lanes. New variants use the retained `pre2std4` 2.88 µm precharge receiver, extracted stock drivers, actual layout capacitance and geometry-derived resistance. Their energy is the sum of finite-window source energies for **16 active bit columns plus 128 readouts**, selected drivers and ideal aggressors. Complete 1,280-bit row energy remains **unknown for every row of this table**. The different test scopes prevent an apples-to-apples energy/speed ratio.

The conditional factor is `ceil(tested passing complete protocol interval / 20 ns)`. It includes the sampled precharge/read/recovery sequence; it is not computed from threshold delay. It is a sufficient factor for that sampled slice protocol, not a proven minimum or full-bank throughput result. Failed shorter protocols remain in the timing report. Four striped 320-row banks revisit each bank every 80 ns. A single 1,280-row bank provides no interleaving; any larger factor would require full-image replication or a new partition and a new area measurement.

## Physical verification

| Rows/bank | Assembly dimensions, µm | Selected full-assembly DRC markers | Independent bit readback | Full-bank LVS |
|---:|---:|---:|---|---|
| 64 | 4669.70 × 4780.00 | 0 | all 1,638,400 bits match | pass; 87,040 devices, tile0 |
| 320 | 4669.70 × 2664.00 | 0 | all 1,638,400 bits match | pass; 414,720 devices, bank3 |
| 1280 | 4669.70 × 2249.00 | 0 | all 1,638,400 bits match | not run |

The 320-row full-bank reference independently decodes the original packed K64 tensor and checks it against W2b RTL. Monolithic Netgen passes with no property errors, supported by exact device-graph/W/L comparison, ten passing partitions and a shared-net audit. A doubled-width negative control is rejected. DRC uses the reused official GF180 FEOL/BEOL/connectivity/off-grid rules; density and antenna are excluded. No foundry signoff claim is made. The optional 1,280-row variant has no full-bank LVS claim.

The final required 320-row timing group is bank3/group2, containing the worst ranked column among all 1,280 columns of the extracted bank3 by an explicit-capacitance/geometry-resistance proxy. That proxy and sampled sequences do not prove a global worst case over all four banks. The earlier group3 timing runs remain separately recorded. The optional 1,280-row sample is independently extracted from its actual programmed layout; its ranking and scope are in the timing report.

## Integration and evidence

Physical 320-row placement is striped: `logical_row = bank + 4*local_row`. Use `bank = row[1:0]`, `local_row = row[10:2]`; keep W2b representative/codebook selection tied to the original logical row. Each bank has ten 32-lane subbanks, common long WL/PC rails, and one set of 1,280 readouts. Stock drivers in the timing harness are not placed in these GDS banks.

W2b requests 1,280 rows in 4,160 integer cycles (4,163 with FP32 drain), normally one request every three cycles. Its INDEX capture aperture is still one cycle, and its real representative register follows a combinational lookup. Bank interleaving does not remove this latency/setup requirement. Complete-row control loading, output selection, capture phases and the logical row tag require physical and protocol closure. Hard-macro placement beside W2b remains skipped; there is no complete qualified hard macro to place.

The unchanged retained cell-only specimen remains **4.8684604443 µm²/selection**. Taller layouts retain the wide horizontal readout strip and joining geometry, so much of each rectangle is unused width. Their areas are measured implementations, not optimal lower bounds.

* [320-row GDS](tall-bank/r320/assembly.gds), [geometry](tall-bank/r320/geometry.json), [DRC](tall-bank/r320/assembly-drc.json).
* [1,280-row GDS](tall-bank/r1280/assembly.gds), [geometry](tall-bank/r1280/geometry.json), [DRC](tall-bank/r1280/assembly-drc.json).
* [Independent verification](tall-bank/verification/RESULTS.md), [machine evidence](tall-bank/verification/results.json).
* [Timing and preserved failures](tall-bank/timing/RESULTS.md), [machine evidence](tall-bank/timing/results.json).
* [Integration contract](tall-bank/INTEGRATION.md), [exact commands](tall-bank/COMMANDS.md), [comparison JSON](tall-bank/results.json).

---

# W5 measured GF180 readable-cell array — bounded handoff

**The real mask-programmed storage and several physical readout/periphery blocks are built and verified. The requested complete ARRAY-PORT-compatible macro is not finished or timing-qualified.** Complete-macro area, row-read latency, row energy and complete-projection area remain null in [results.json](results.json). The retained failures and missing integration are concrete; no small bank is reported as a complete recognizer.

The selected mechanism is the Taalas stored-index readable-cell branch: four mask-programmed access NMOS devices store each four-bit selection; precharge, keeper and restoring inverter recover each bit. Fixed identity is physical connectivity. W2b retains fixed representative lookup and shared digital products. This does not claim the area of a one-access-transistor **direct product selection** embodiment for a four-bit stored index.

## Real image and measured geometry

All **409,600 selections / 1,638,400 bits** were independently decoded from the original rectangular K64 packed tensor and compared against W2b's frozen RTL image. Both full GDS assemblies were reopened and their programmed Via1 positions read back: **zero mismatches**. [identity.json](identity.json) records the image, source and reconstruction hashes. Rows 0–63 in the tile are the real first projection rows.

| Retained physical scope | Dimensions, µm | Area, µm² | µm² per selection | Qualification |
|---|---:|---:|---:|---|
| 64×320 cell-only tile | 925.69 × 107.71 | 99,706.0699 | **4.8684604443** | DRC0; 81,920-device LVS pass |
| 20-tile cell-only assembly | 3763.69 × 619.71 | 2,332,396.3299 | 5.6943269773 | DRC0; all bits match; includes placement gaps, no intertile wiring |
| 64×320 array plus physical analog readout | 4669.7 × 220 | 1,027,334 | **50.16279296875** | DRC0; 87,040-device LVS pass |
| 20 distinct array/readout tiles | 4669.7 × 4780 | 22,321,166 | **54.4950341796875** | Hierarchical DRC0; all bits match; global periphery absent |
| Complete macro with all periphery | — | **unknown** | **unknown** | Not qualified |

The cell-only number uses the bounding rectangle of a physical tile with local cell wiring; it excludes all read periphery. The sum of 20 cell-only tile rectangles is 1.994121398 mm². The larger readout tile contains ten 64×32 subbanks, 1,280 physical precharge/keeper/inverter channels and their actual Metal2/3/4 joins. Its straightforward fanout geometry is expensive; this is a measured specimen, not an optimized lower bound. Do not add cell-only area again to the readout tile.

The newer decoded-tile experiment is reported separately in `timing/decoded-tile/` and the root JSON. It adds ten local row decoders and physically segmented wordlines to tile0, occupying **4669.7 × 240.8 µm = 1,124,463.76 µm²** (54.90545703125 µm²/selection). Its full-tile DRC and all 81,920 programmed-bit readbacks pass. Its **compositional LVS passes across all 111,460 transistors**: each of ten banks matches its distinct independent reference with zero property errors, and an exact partition/shared-net audit proves full-tile coverage. The monolithic comparison was stopped at 600.44 seconds and is preserved as incomplete; it is not claimed as a pass. This decoded tile is **not** what the 20-tile partial assembly contains, and still excludes phase control, bank mux and output-latch integration.

## Verification and deliverable layouts

* Cell array: [base/array-core.gds](base/array-core.gds), [tile0.gds](base/tile0.gds), [verification.json](base/verification.json).
* Array/readout tile: [integrated/readout-tile0.gds](integrated/readout-tile0.gds), [LEF](integrated/readout-tile0.lef), [LVS result](integrated/lvs-result.json). LEF is 4670×220 µm with 1,347 pins. VDD/VSS have Metal4/Metal5 access; all exported pin rectangles were checked against actual GDS metal. It is a **partial tile abstract**, without complete-macro timing Liberty.
* Decoded tile0: [GDS](timing/decoded-tile/v1/decoded-tile.gds), [compositional LVS and DRC results](timing/decoded-tile/results.json). No decoded-tile timing or complete-macro claim.
* Twenty real-programmed readout tiles: [partial-full-readout.gds](timing/full-readout/partial-full-readout.gds), [results](timing/full-readout/results.json). No top-level independent LVS, common intertile wiring or full-macro LEF is claimed.
* Digital components: [periphery/handoff-v2/](periphery/handoff-v2/) and [handoff-latch128/](periphery/handoff-latch128/), each containing GDS/LEF/DEF/netlist/SPICE.

Every KLayout zero count here is scoped to the reused official GF180 FEOL/BEOL/connectivity/off-grid checks, with density and antenna excluded. Full readout-assembly DRC used hierarchical mode and completed locally in 109.43 seconds. These are open-flow results, not foundry signoff or PDN IR/EM qualification.

Cell-only and joined-readout LVS compare independently constructed device connectivity and W/L against flattened extraction. Magic's hierarchical label prefixes initially prevented top-pin matching. A recorded, checked **bijection of existing node names** fixes the naming view without changing devices or merging nodes. Final Netgen comparisons match uniquely with no property errors. A deliberately doubled transistor width is rejected as a property error even though Netgen also prints its topology-match phrase; the checker requires both conditions.

## Read timing and energy

The most representative completed analog experiment is the **physically joined 64×32 bank0**, with actual join capacitance and 8 sampled rows × 128 bits per case. Each of the following cases has zero raw 70/30-threshold and restored 90/10-threshold failures across 1,024 bit samples:

| Corner | Test period | Maximum sampled settling after ideal WL assertion | Mean net source energy per 32-lane read |
|---|---:|---:|---:|
| TT 3.30 V, 25°C | 20 ns | 2.975848 ns | 77.708518 pJ |
| SS 2.97 V, 125°C | 20 ns | 4.390495 ns | 62.274525 pJ |
| TT 3.30 V, 25°C | 25 ns | 2.975846 ns | 77.716824 pJ |
| SS 2.97 V, 125°C | 25 ns | 4.377625 ns | 62.375218 pJ |

These are extracted-capacitance slice results with ideal WL/PC/supply drivers and assumed 10 fF output loads. They exclude distributed wire resistance, real phase/decoder delay, bank mux, latches, global wiring and W2b's representative lookup. Bank0 is not a proven worst-case bank, and the eight-row sequence is not exhaustive. A separate maximum-connected-drain slice exercises a load proxy; it does not prove worst-case complete-tile timing. Do not scale these energies by ten or twenty and label the result measured full-row energy. See [timing/joined-bank0-v2/results.json](timing/joined-bank0-v2/results.json) and retained decks/waveforms.

W2b makes **1,280 INDEX reads in 4,160 integer cycles**, followed by FP32 drain for 4,163 cycles. At a hypothetical qualified 20 ns clock that is 83.20/83.26 µs; at 25 ns it is 104.00/104.075 µs. The sampled analog data alone does not qualify either complete-projection schedule. Full row-read latency, complete row energy and achieved real-time performance are unknown.

## Digital periphery and observed limits

The isolated row decoder (120×120 µm), 20-way mux128 (450×450 µm), bank decoder (120×120 µm), and latch128 (450×80 µm) each pass selected KLayout DRC, Magic DRC and Netgen LVS with zero reported errors. Routed-netlist functional tests pass; the latch specifically passes 1,411 transparent/hold checks. Ten latch outlines total 0.36 mm², excluding integration routes.

The row decoder's worst extracted setup slack is **−0.806 ns** with 11 slew violations. The mux's worst is **−10.582 ns**, with 303 slew and 2 capacitance violations. These use a 20 ns virtual period, 4 ns input/output delays and the specified isolated output loads. The bank decoder and latch pass their standalone constraints. Latch STA assumes a 20 ns, 50%-duty gate and allows borrowing; it does not prove a valid analog capture waveform. Digital SS uses 3.00 V Liberty, distinct from analog SS 2.97 V SPICE.

The proposed 200 decoders + ten muxes + bank decoder have an isolated outline sum of 4.9194 mm². This is a component ledger, not extra area to blindly add to a tile that already contains decoders, or a composed macro bound. [Periphery results](periphery/RESULTS.md) and [latch results](periphery/LATCH-RESULTS.md) preserve the exact constraints, failure counts and physical artifacts.

W2b's declared `index_latch` is dead state and is removed by synthesis. Its real registers capture mapped eight-bit representatives after a combinational lookup. Consequently the macro must meet the lookup-plus-register setup requirement; the new physical transparent latch has not yet been wired or phase-qualified. A prior incorrect capture-ownership statement is explicitly preserved and corrected in [LATCH-ERRATUM.md](periphery/LATCH-ERRATUM.md).

## Integration disposition

[INTEGRATION.md](INTEGRATION.md) specifies bit ordering, bank addressing, phase hazards, W2b stall/abort obligations, power pins and area accounting. `results.json` snapshots W2b's own routed-footprint field. The complete total is **W2b ARRAY-PORT routed footprint + complete macro footprint + external routing allowance**, with no numerical total until all terms exist. Synthesis cell area and intermediate placement are not substituted for routed area.

Remaining work is physical phase control; 25,600 tile-to-mux data connections and output-latch routing; complete top-level LVS/LEF/Liberty; distributed-RC read/setup/hold/abort/stall validation; and real load/PVT timing and power closure. The row decoder and mux timing failures are already evidence against declaring the current 20 ns implementation closed. Hard-macro placement beside W2b was a stretch goal and was skipped because the complete qualified hard macro is absent. Full hierarchical partial-array DRC completed locally. [CLOUD-REQUEST.md](CLOUD-REQUEST.md) supplies optional lead-run commands for a further monolithic decoded-tile LVS comparison; more compute does not supply the missing complete-macro design.

All writes are confined to this workspace. Original source generators/model artifacts, failed geometry revisions, failed pin-name comparisons, stopped long transient runs, initial mux placement failure and latch fanout-capacitance failure are retained. Exact commands and source evidence are indexed in [COMMANDS.md](COMMANDS.md). The root skill, complete source notes, primary patent mechanisms, characterization documents and current root plan were read; both delegated workers confirmed the same source-reading obligation. No git or cloud operation was used.
