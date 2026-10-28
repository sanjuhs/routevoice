# Codex brief W11: Taalas end-to-end. The full recognizer reads every weight as index + codebook, and "Switch on the lights" still passes

AUTHORIZATION: the user resumed RouteVoice on 21 Oct 2026 for a release on **Friday 23 Oct**. They want the whole end-to-end simulation in a very good state, with all of the wiring proven. The lead (Claude) re-checks everything. Never fabricate results, and keep failures on record.

Read first (≤15 min):
- `onchip-all/RESULTS-v2.md`, `commands-v2.json`, `run_stage_v2.py`, `rom-manifest.json`
- `onchip-all/RESULTS-v3.md` (A/B banks are both live)
- `storage-inventory/INVENTORY.md`
- `accuracy-int8/RESULTS.md` (lossless affine-INT8 frontend: 2,090,240 B, bit-exact)

## Where it stands
v2 (`rv_allonchip_top_all_v2.sv`) holds all six weight services on-chip: 28,641,280 B as **byte ROMs** (`$readmemh` of UINT8 coefficient images plus metadata). Its F64 "Switch on the lights" run passes:
- tokens [28176, 373, 278, 26068, 2];
- 18/18 output hashes;
- 312,578,649 clocks;
- about 53 min of simulation.

Every decoder/encoder weight image uses exactly 16 distinct UINT8 values per (64 inputs × 1 output) group. So a **4-bit index per weight + a 16-entry UINT8 codebook per group** is exact. That is the Taalas fixed-selection storage the physical array implements (`taalas-pitch/`, `taalas-array/`).

## Goal (by Thu 22 Oct 18:00 IST)
**v4** of the full recognizer, in which every byte-coefficient ROM is replaced by **index ROM (4 bits/weight) + codebook ROM (16 × UINT8 per 64×1 group)**, with an RTL lookup that rebuilds the byte. The frontend uses the lossless affine-INT8 form where that is exact. F64 must pass **bit-identically**: same tokens, 18/18 hashes, the same clocks (or explain any delta).

## Steps
1. **Generate the images.** Write a generator that turns each coefficient ROM image into index + codebook images.
   - Prove the round trip is exact for EVERY byte of every ROM (count mismatches = 0).
   - Report the bytes before and after: index bits + codebook bytes + metadata, per service and in total.
2. **Write the v4 RTL.** Implement it as a copy (keep v1–v3 unchanged).
   - Each ROM responder reads `index[addr]` and `book[group(addr)][index]`.
   - Keep it pipeline-equivalent: the same read latency as the byte ROM, so the clocks stay identical.
   - Add unit tests per responder: exhaustive or random readback against the byte ROM.
3. **Run F64** (positive + compare + render) with v4. Before the positive run, archive the existing `actual/`; the runner refuses to overwrite it.
4. **More clips, if time allows.** Run 2 more original-audio corpus clips that passed earlier (see `../STATUS.md`, v49 tally), to show the result generalizes. Report pass/fail per clip.
5. Write `RESULTS.md` + `results.json`, including exact commands and pins.

## Rules
- Write ONLY in `finish-1023/w11-taalas-e2e/`. Runtime state may go under `~/.local/state/routevoice-internal-runs/20261021/w11/`.
- Local Mac only, using ≤6 cores. Other jobs are running.
- Keep ≥22 GiB free on the Mac. No git. No RunPod.
- Print `W11-STATUS: <result>` after each step.
- Write a partial `RESULTS.md` by Thu 18:00 even if not finished.
