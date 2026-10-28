# Lead guidance 3 for W1: can the duplicated A/B state buffers go? (one-die enabler)

v2 is lead-verified. Thank you.

Context: the whole-chip floorplan (`overnight-20261014/floorplan/RESULTS.md` § "Final design point") shows ONE GF180 die fits a 26 × 33 mm reticle using memory built from the open GF180 SRAM bit cell, **if mutable state shrinks by ≈161 KiB**. The storage inventory (`overnight-20261014/storage-inventory/INVENTORY.md`) lists two A/B pairs:
- `rv_encoder_bank_consumer_edge_v1` (encoder bank0/bank1, 80 KiB each);
- `rv_producer_mutable_storage_v1` (producer bankA/bankB, 80 KiB each).

## Step 1: analysis (required; ≤60 min)
For each pair, determine from the RTL and the F64 simulation **whether both copies are ever live at the same time**:
- a ping-pong across layers, i.e. read A while writing B;
- a copy kept for retry/reset recovery;
- an alias.

Evidence counts, not guesses: add read-only observation in a COPY of the host (count cycles where both banks hold live data, max simultaneous live words), and/or analyse the RTL's write/read enables. Report the minimum storage each pair actually needs for F64 and the general frame bound, and what would break (warm-reset retry, stall, overlap) if one copy were removed.

## Step 2: only if Step 1 shows a safe reduction
Implement `rv_allonchip_top_all_v3` with the reduced storage. Keep v2 unchanged. Run the full F64 (positive + compare + render) plus the existing negative/fault tests that exercise these banks, if present. Expect identical tokens/hashes; clocks may change, so report the delta.

If Step 1 shows the copies are both needed (true double buffering), STOP after writing the analysis. That is a valid, useful result: it says one die needs denser memory instead.

Write `onchip-all/RESULTS-v3.md`. Print `W1-STATUS:` lines. Finish by ≈07:15 IST. Same disk/CPU rules.
