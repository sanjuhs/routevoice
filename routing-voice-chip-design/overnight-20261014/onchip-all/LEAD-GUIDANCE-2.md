# Lead guidance 2 for W1: close the last model-constant inputs

Lead-verified: the merged all-six F64 passes. Excellent.

One boundary remains. The top still takes three model constants as runtime inputs: `source_start_position_scale` [31:0], `source_start_position_zero` [7:0] and `source_start_position_offset` [11:0]. They belong to the frozen model (position quantization), so they should be built into the chip.

1. Create `rv_allonchip_top_all_v2` (new file; keep v1 unchanged). It ties these three to localparams equal to the exact values the host currently drives for F64. Take the values from the host code / `producer/real-domain-contract.json` (`position_scale_bits` 1012345286, `position_zero` 123 — verify; and the offset from the host). Remove them from the port list.
   - Also audit every remaining input and classify it in `RESULTS.md` as audio data / control-handshake / reset / job metadata (tags, session, frame count) / model constant.
   - If any other model constant is still an input (e.g. `compact_setup_image_id`), decide with evidence whether it is a model constant or a per-job identifier. Tie it to a constant only if it is a model constant.
2. Update the host copy so it no longer drives those ports, and asserts nothing else changed.
3. Run lint → generate → compile → fixture → positive → compare → render. Expect identical clocks (312,578,649), 18 hashes, and "Switch on the lights".
4. Write `onchip-all/RESULTS-v2.md`. Print `W1-STATUS:` lines. Same disk/CPU rules: ≥ 22 GiB free, `nice`, ≤ 8 jobs.

Finish by ≈05:30 IST. If it is not finished by then, report the state honestly.
