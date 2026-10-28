# Lead guidance 1 for W3 (01:30 IST)

Good progress: the pad ring and PDN flow work. Stop sweeping die sizes on today's inputs. Most of the area is your own assumptions, so the sweep isn't telling us anything yet. Change course as follows.

1. **Fix the PDN connectivity first.** Your abstract macro power pins are disconnected. Give each macro LEF VDD/VSS pins on a metal layer that `pdngen` actually strapped (for example horizontal stripes on Metal4 and vertical on Metal5 within the macro, or `add_pdn_connect` to the macro pin layer), and use `-grid` per-instance macro grids if needed. `check_power_grid -net VDD/VSS` must pass, then run `analyze_power_grid` and report worst IR drop.
2. **Remove `KV_retention_reserve` (983,040 B) and `private_state_reserve` (524,288 B) from the baseline.** They are not measured. Keep them only in a separately labelled "conservative" scenario. The lead is running a full-top Yosys memory inventory on a cloud machine. When `overnight-20261014/synth/stat_mem.txt` appears (the lead will copy it there), replace the reserves with the real `$mem` bit counts.
3. **Memory density is the dominant variable, so make it a scenario axis:**
   - `sram_open_macro`: today's 512×8 open macro, about 51 µm²/bit, label MEASURED-LEF.
   - `sram_4k_research`: the project's 4 KiB research bank, 0.9479839488 mm² per 4,096 B (about 28.9 µm²/bit); source `docs/TAALAS-DIE-SIZE-AND-SYSTEM-COSTS-2026-10-02.md`.
   - `sram_dense_custom`: about 12 µm²/bit effective, ASSUMED. That is a 180 nm 6T cell plus about 40% periphery; label it as an assumption needing a compiled macro.
4. **Add design-lever scenarios, each clearly labelled "requires model-accuracy re-validation" where it changes numerics:**
   - `frontend_int8`: store the 2,074,560 frontend coefficients as INT8 (4× fewer bytes) instead of FP32. This is a numerical change.
   - `books_in_array`: put the codebooks in the same dense readable-cell array as the indices (selection density per bit) instead of binary ROM at 1.76 µm²/bit ×1.25.
   - `kv8`: if KV retention is needed at all, 8-bit instead of FP32.
5. **Use measured numbers as soon as they exist.** W2b's 1280×320 SC-ROM and ARRAY-PORT LibreLane runs will write `overnight-20261014/fabric-k64/results.json`; W2's 320×320 writes `overnight-20261014/fabric/results.json`. Take the measured datapath/periphery area per output lane and per projection from ARRAY-PORT, and the standard-cell selection density from SC-ROM.
6. **Final deliverable:** a table of total area for {selection density: std-cell measured, custom 7.04, optimistic 3.5} × {memory density: open, 4k research, dense custom} × {levers off, levers on}. Then report the smallest die that places with PDN connected and IR drop under 5%, for the most credible combination (say which you think that is and why), and the two-die split for the same combination. Render PNGs for the best one-die and the two-die cases. Put it in `RESULTS.md` / `results.json`.
