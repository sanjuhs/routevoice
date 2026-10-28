# Lead guidance 1 for W5: tall-bank variant

Excellent work. The tile is DRC/LVS clean, all 1,638,400 bits match, and the cell is 4.87 µm²/selection; the lead re-measured the GDS and checked how your LVS reference is built. Your 20-tile assembly is 22.3 mm², about 90% readout. Each 64-row tile carries its own 1,280 readouts, so they are replicated 20 times.

Next, measure the area-versus-speed trade-off with real layout.

1. Read `docs/TAALAS-TALL-BANK-BUDGET.md` and `docs/TAALAS-MASK-INDEX-TALL.md`. The project already qualified 256-, 320- and 1,280-row banks in circuit simulation (`pre2std4` receivers). Reuse those circuit choices.
2. Build a **320-row bank** variant of the projection array: 4 banks × 320 rows = 1,280 rows, each bank with ONE set of 1,280 readouts. Program it with the real indices and run the same checks: selected DRC, bit readback, LVS on at least one full bank against the index-derived reference, and sampled TT/SS read timing on the extracted worst-case column. If the 320-row read time is too slow for one row per 20 ns, report the measured read time and how many banks must be interleaved to sustain one 1,280-bit row per cycle.
3. If time allows, also do a 1,280-row single bank: area plus read time.
4. Report a comparison table in `RESULTS.md` / `results.json`. Rows are bank heights 64, 320 and (if done) 1,280. Columns: total macro area, µm²/selection including periphery, readout count, worst read time per corner, energy per row read, and banks needed for one row per 20 ns. Keep the global decoder/mux/control exclusion explicit, or add them if you have time.

Same rules as your brief: workspace only, `nice`, ≤ 4 threads, ≥ 22 GiB free, and print `W5-STATUS:` lines.
