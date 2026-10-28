# Lead guidance 3 for W3: the credible Taalas floorplan (pitch-matched array + memory scenarios)

Your measured 320-row/open-SRAM report is good and honest; keep it as the "as-built tonight" upper bound. Now produce the **credible design point**.

## New measured input
W6 (`overnight-20261014/taalas-pitch/`) built a **pitch-matched readout** (stacked readout rows; the array keeps its native ≈0.72 µm bit-line pitch) for the full approved projection:
- one 1,280-row bank, 1,004 × 2,258.81 µm = **2.2678 mm² per 409,600 selections = 5.537 µm²/selection including readout**;
- all 1,638,400 bits read back from GDS with 0 mismatches; the 64-row version is DRC 0;
- full-bank DRC/LVS/SPICE are in progress.

**Re-read `taalas-pitch/results.json` and `RESULTS.md` (with hashes) immediately before your final run**, and label the density "MEASURED, DRC/LVS status: <whatever W6 reports>".

Timing context, to state but not to invent: W5 measured 1,280-row SS settling ≈22.5–24.4 ns (W5's stretched-pitch bank; W6's may differ) and a 60 ns reuse pass. W2b's engine requests a new row about every 60 ns (3.25 cycles at 20 ns), so a single 1,280-row bank fits the engine's actual schedule; it does NOT support one row per 20 ns.

## Scenarios to run
Keep the frozen 144-array memory inventory and the other measured blocks. Replace the fabric/head/producer selection density with **5.537 µm²/selection**, and keep W5's separately measured decoder/phase/mux allowance (your `array_decoder_phase_mux_allowance`, recomputed per selection if appropriate).

Area table:

| Memory density | Levers off | Levers on |
|---|---|---|
| `sram_open_macro` (measured LEF) | | |
| `sram_4k_research` | | |
| `sram_dense_custom` (assumed 12 µm²/bit; a foundry SRAM compiler would replace this) | | |

Levers:
- `frontend_int8`: 2,074,560 coefficients as INT8; **needs accuracy re-validation**.
- `books_in_array`: K64 books stored in the same pitch-matched readable array at 5.537/4 µm² per bit; no numerical change.
- Optionally `codebook_dedup`: count only the 7,765,892 B actually used if you can justify it.

## Physical runs
Floorplan + PDN + IR screens (same PASS criteria as before) for:
1. the **smallest one-die** case among {dense SRAM, levers on} and {dense SRAM, levers off};
2. **two-die** for {open SRAM, levers on}, since that combination needs no custom SRAM and no accuracy change, which matters for a first tapeout;
3. the best case that needs **neither custom SRAM nor accuracy changes**, at one or two dies, whichever fits.

State for each whether it fits a 26 × 33 mm field (an assumed typical reticle limit).

## Deliverable
Add a section **"Credible Taalas design point"** to `RESULTS.md` / `results.json`:
- the area table above;
- the physical screen results with PNG + IR heatmap paths;
- a one-paragraph verdict naming which assumptions remain (custom SRAM, accuracy re-validation, complete array macro timing, real power).

Keep the earlier sections. Same rules: workspace only, `nice`, ≤ 4 threads, ≥ 22 GiB free, print `W3-STATUS:` lines. Finish by ≈05:30 IST.
