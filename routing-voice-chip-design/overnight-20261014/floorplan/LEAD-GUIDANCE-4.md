# Lead guidance 4 for W3: two last measured inputs, then final floorplans

Two new lead-verified facts change the credible design point.

1. **The frontend "INT8" lever is now lossless (lead-verified).** The model's own affine INT8 codes + FP32 scale/offset reconstruct all 2,074,560 FP32 ROM coefficients bit-for-bit (`overnight-20261014/accuracy-int8/existing-affine-int8-exact/`, RESULTS.md § "Exact existing INT8 representation").
   - Storage: **2,090,240 B** (2,073,600 INT8 + 12,800 scales/offsets + 3,840 biases) instead of 8,298,240 B, with **zero numerical change**.
   - Rename the lever `frontend_native_int8_lossless`, use 2,090,240 B, and add a small decode allowance (one FP32 multiply-add per fetch: count 1 FP32 FMA unit; reuse the frontend logic allowance if you already have one). It no longer "requires accuracy re-validation".
   - Symmetric re-quantized INT8 FAILED the gates (W7). Say so, and say it is not used.
2. **Measured SRAM bit cell.** The open GF180 SRAM macros (`pdks/gf180mcuD/libs.ref/gf180mcu_fd_ip_sram/gds/*512x8*`) use cell `018SRAM_cell1_512x8m81`, 3.68 × 5.18 µm, and pair cell `…cell1_2x…`, 3.68 × 9.68 µm, giving an **≈17.8 µm²/bit array pitch** (plus strap cells).
   - Add a memory scenario `sram_bitcell_large_macro` = **17.8 µm²/bit bit cell ÷ 0.70 array efficiency ≈ 25.4 µm²/bit**. That is what larger macros built from the same open bit cell would plausibly reach (label: bit cell MEASURED, efficiency ASSUMED).
   - Keep `sram_dense_custom` (12) but relabel it "requires a smaller foundry bit cell than the open GF180 one".
3. Re-run, with W6's measured array density and books in the array:
   - (a) one die with `sram_bitcell_large_macro` + lossless frontend. Report the smallest outline and whether it fits 26 × 33 mm.
   - (b) the same with `sram_dense_custom`.
   - (c) two dies with `sram_open_macro` + lossless frontend (this is now the "no custom memory, no numerical change" option).
   Do PDN + IR screens as before. Also report **how many KB of mutable state** would have to be removed for (a) to fit, and list the largest arrays that are duplicated A/B buffers (from `storage-inventory/inventory.json`). That is design guidance, not a claim.
4. Update `RESULTS.md` with a section **"Final design point (lossless frontend, measured bit cell)"** and results.json. Print `W3-STATUS:` lines. Finish by ≈06:15 IST. Same rules.
