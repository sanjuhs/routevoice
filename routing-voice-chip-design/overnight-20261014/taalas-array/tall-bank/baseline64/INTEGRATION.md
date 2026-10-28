# W5 → W2b / W3 integration handoff

**The complete ARRAY-PORT-compatible hard macro is not qualified.** This directory contains measured real-mask arrays, physically joined analog readout, separately routed digital periphery, and a decoded-tile experiment. Do not use any partial GDS as a completed projection or substitute a cell-only number for total weight-fabric area. `results.json` is the machine-readable scope ledger; unknown complete-macro values are null.

## Exact data contract

The admitted tensor is encoder block 0 FF project-out, K64, logical shape 1280 inputs × 320 outputs. `identity.json` independently decodes the original rectangular block-major packed file, low nibble first, reconstructs weights, and compares every index with W2b's `rtl/index_fabric.sv`. The decoded byte-image SHA256 is `ba628b676d59721c268868d6720be1f58a4f8d4edfd9a26009403c9a8c4fce8e`.

For W2b's `array_row[10:0]`, `bank = array_row[10:6]` selects one of 20 physical 64-row tiles and `local_row = array_row[5:0]`. Valid rows are 0–1279. `frozen_index_bits[4*lane +: 4]` is the four-bit index for that row and lane; bit 0 is least significant. A programmed drain-to-bitline connection discharges the precharged bitline and makes the restored inverter output **one**. Missing mask connection represents zero. There are four access NMOS devices per selection in this stored-index embodiment.

This is the patent's stored-index readable-cell branch, followed by W2b's fixed codebook lookup and shared radix products. It is not the direct shared-product-wire selection embodiment. Four-bit index width does not imply four-bit activations or representatives. W2b retains UINT8 representatives, signed nine-bit centered activations, 17-bit products, 27-bit accumulators, zero-point corrections, scales and biases.

## Required electrical integration

The intended path is local row decode/drive → programmed access cells → precharge/keeper/restoring inverter → 20-way bank mux → transparent output latch → W2b codebook lookup → W2b representative capture. The 20-way selection uses ten 128-bit muxes. `bank_data[128*bank + bit]` in each mux corresponds to the same 128-bit lane slice from all 20 tiles. Ordinary CMOS receiver outputs cannot be shorted into a wired bus. This leaves 25,600 distinct tile-to-mux data connections to route.

The decoded-tile experiment segments the 64 wordlines into ten local 32-lane banks, with one physical row decoder per bank. Its decoder outputs must not be joined by the earlier readout tile's common wordline rails. Both revisions remain preserved. The 20-tile GDS in `timing/full-readout/` uses the earlier readout revision and does not contain the decoded tile, global bank mux, output latches, global PDN or common control routing.

`periphery/handoff-v2/` contains the routed row decoder, bank decoder and mux. `periphery/handoff-latch128/` contains the completed, separately qualified latch component documented in `latch-results.json`. These components have not been wired into a complete macro. Their LEFs and the partial readout LEF expose Metal4/Metal5 VDD/VSS ports; pin rectangles on the readout LEF were checked against actual GDS metal. This proves pin-metal existence, not router escape, supply integrity or full-chip PDN closure.

Precharge is active with PC low; evaluation requires PC high before a wordline rises. A physical nonoverlap controller must preserve this on address changes, reset and abort. Output latches must close while selected data is valid and before precharge corrupts that data. `periphery/PHASE-CONTROL-NEXT.md` records a proposed physical OR-tree feedback experiment and its unresolved distributed-delay hazards; it is not an implemented timing contract.

W2b's `index_latch` is declared and assigned but never read, and disappears from synthesis. Live state captures 320 mapped eight-bit representatives from a combinational codebook lookup. Thus raw index data must arrive early enough for **that lookup and its capture setup**, in addition to any new macro latch timing. See `periphery/LATCH-ERRATUM.md`; the incorrect earlier ownership claim is preserved there. The separate transparent latch requires no extra architectural cycle only if its open/close phases and W2b setup are actually proven.

`array_read_enable = INDEX && step_enable` is not a completion handshake. A late reassertion of `step_enable` can start analog evaluation immediately before W2b captures. Require a documented minimum read-enable setup and stable address interval, or adapt W2b with request/ready and a stallable read completion. Do not infer correctness from the combinational ROM testbench. No W2b files were changed by W5.

## Area accounting for W3

Use this equation only after the missing terms are measured:

`projection physical area = ARRAY-PORT routed footprint + complete macro footprint + external integration routing allowance`

The complete macro footprint must include cells, analog readout, decoder/wordline drivers, phase control, bank mux, latches, internal wiring, and supply access. Internal routing already in that footprint must not be added twice. Separately routed component outline sums are placement ledgers, not composed dimensions or lower bounds: local decoders can occupy existing empty space. Cell area from synthesis is not the ARRAY-PORT routed footprint.

Measured cell-only tile area is 99,706.0699 µm² for 20,480 selections: **4.8684604443 µm²/selection**. The actual array+readout tile occupies 1,027,334 µm²: **50.16279296875 µm²/selection**, with major periphery still excluded. Its 20-tile partial assembly is 22.321166 mm² including gaps: **54.4950341796875 µm²/selection**. These are measurements of the retained layouts, not optimized architecture limits. The original 7.04 µm² assumption is therefore replaced only for the precisely identified cell-only scope; there is no qualified complete-periphery replacement yet.

Root `results.json` snapshots W2b's own reported routed-area field and its evidence hash. If it is null, the total remains null. W2b may continue changing after this handoff; re-read its final results before combining numbers. No default-activity power or placed intermediate timing is promoted to a completed projection result.

## Timing and schedule

The physically joined 64×32 bank has actual routed join capacitance, but ideal wordline/precharge/supply sources, no distributed wire resistance and assumed 10 fF output loads. Eight selected rows pass at TT 3.3 V 25°C and SS 2.97 V 125°C at both 20 and 25 ns periods. Maximum sampled settling after wordline assertion is approximately 2.976 ns TT and 4.390 ns SS at the 20 ns test period. This is not full row-read latency from address/read-enable, and bank 0 is not a proven worst bank. A separate maximum-drain-population slice is a loading comparator only.

The row decoder and bank mux have preserved slow-corner setup and electrical violations under their isolated 20 ns STA constraints. Those digital corners use SS 3.00 V Liberty, not the analog 2.97 V SPICE corner. It is invalid to combine the sampled analog settling time and isolated STA slacks into an achieved clock rate.

W2b performs **1,280 INDEX reads during 4,160 integer cycles**, or 4,163 cycles through FP32 output. At a hypothetical verified 20 ns clock, these take 83.20/83.26 µs; at 25 ns, 104.00/104.075 µs. If literally scheduling 4,160 separate reads, the arithmetic is also 83.20 or 104.00 µs at those assumed periods. Neither is a measured complete-macro or whole-recognizer real-time result. Full macro read time, energy and achieved projection time remain null.

## Remaining closure and stretch goal

Finish physical phase generation, mux/latch integration and 25,600 data wires; verify top-level connectivity and all real mask bits; extract distributed control/data/power parasitics; close address-to-representative setup, all hold/abort/stall cases, PVT and output loads; then emit a complete macro LEF/Liberty and run the ARRAY-PORT hard-macro placement. The LibreLane whole-projection placement stretch goal was skipped because a qualified complete hard macro does not yet exist. This is a design/integration gap, not evidence that a larger cloud machine alone will solve it.

The measured analog layout uses 128 receivers in one horizontal strip for each 32-lane bank and an explicit fanout channel. A later folded/distributed receiver floorplan could change that cost, but it must be laid out, routed, checked and extracted before assigning an area or timing improvement. The present footprint does not establish an architectural minimum or reject the existing Moonshine topology.
