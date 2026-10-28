# Lead guidance 2 for W3: re-run the whole-chip floorplan with MEASURED inputs

The pad ring, PDN and IR flow work. Now replace the assumptions with tonight's measurements and produce the definitive one-die vs two-die answer. Re-read sibling outputs (with hashes) before you start, because they keep improving.

## Measured inputs (use these; cite the files)

1. **Mutable memory, measured.** `overnight-20261014/storage-inventory/INVENTORY.md` + `inventory.json` come from Verilator elaboration of the merged all-on-chip top (30,542 instances).
   - Mutable arrays total 1,062,727 B across 144 declarations; ordinary registers 29,690 B.
   - Use the per-array list to size SRAM macros: biggest are compact history 139 KB, decoder self K/V 84 KB each, feature bank / encoder banks / producer banks 82 KB each.
   - This REPLACES both reserves. Keep a "conservative" row only if you can justify it.
2. **ROM content, measured.** 28,641,280 B moved on-chip tonight (`$readmemh`) plus 8,852,630 B of already-on-chip tables, both in native format (inventory file).
   - In Taalas form, the fixed weights are 31,457,280 four-bit selections plus codebooks. Do NOT count native bytes as SRAM.
   - The frontend's 2,074,560 FP32 coefficients (8.3 MB) remain a separate binary ROM (or INT8 lever).
3. **Taalas selection density, measured** (`overnight-20261014/taalas-array/RESULTS.md` / `results.json`; W5 is still adding 320- and 1,280-row bank results, so take the latest):
   - cell-only 4.87 µm²/selection (lead-verified);
   - 64-row tiles with analog readout ≈ 54.5 µm²/selection;
   - 320-row banks with readout ≈ 30.4 µm²/selection (12.44 mm² per 409,600);
   - 1,280-row banks: use W5's number if it lands.
   - Report scenarios for each bank height; the tallest bank that meets timing is the likely choice.
   - Compare with the October tall-bank study `docs/TAALAS-TALL-BANK-BUDGET.md` (≈154 mm² cells + ≈67 mm² periphery whole-model), and explain any discrepancy you can see in W5's readout area.
4. **Shared-product engine, measured.** A 320-lane engine is 5.28 mm² cells (W2 V2, `fabric/`) to 6.14 mm² (W2b ARRAY-PORT incl. books + FP32 out, `fabric-k64/`). Use the routed footprint / utilization from W2b's ARRAY-PORT physical run if available (`fabric-k64/results.json`, and the pod mirror copied into `fabric-k64/pod-*` if present); otherwise cells ÷ 0.5 utilization, labelled.
5. **Engine count from throughput:**
   - Model work is ≈0.6 G multiply-accumulates/s: encoder ≈7.37 M MAC per frame × 50 frames/s, plus ≈21.5 M MAC per decoded token at ~4 tokens/s, plus producer K/V.
   - One engine does 409,600 MAC in 4,163 cycles ≈ 98 MAC/cycle.
   - State the clock you assume (the 50 MHz target is not yet met in the std-cell runs; use 25 MHz as a conservative case). Compute engines needed with 2× margin, and include them.
   - Architectural assumption to label: the arrays for each layer group share engines through a row bus.
6. **Frontend:** FP32 coefficients as binary ROM at the measured Taalas cell-only density × periphery, or keep your 1.76 µm²/bit assumption, labelled. The frontend lever (INT8) stays a lever.

## Deliverable
Update `RESULTS.md` / `results.json` with a new **"Measured-input floorplan"** section:
- A block-area table, every number tagged MEASURED / ASSUMED with its source.
- Smallest one-die and two-die outlines that place with PDN connected and IR within 5%, using per-block power from measured W5 read energy and W2b power if available (else your current assumption, labelled).
- PNG renders and IR heatmaps for the chosen one-die and two-die cases.
- A one-paragraph honest verdict: does the whole recognizer fit one GF180 die below about 26 × 33 mm (a typical maximum reticle field — say it's an assumption) and, if not, what does.

Same rules as before: workspace only, `nice`, ≤ 4 threads, ≥ 22 GiB free, print `W3-STATUS:` lines.
