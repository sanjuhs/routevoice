# Codex brief W2b — the approved complete GF180 projection (1280×320 encoder FF out, K64)

The user approved `docs/ROUTEVOICE-PROPOSED-PHYSICAL-GOAL-2026-10-13.md` on 14 October 2026 (in chat with the lead, Claude); `AGENTS.md` records it. The pause is lifted for this run. Read that proposal fully — it is your contract. The lead re-runs and checks your results; never fabricate a pass, show failures with logs.

Reading requirement from AGENTS.md: read `skills/taalas-fixed-weight-routing/SKILL.md` and skim `references/source-notes.md` + the relevant patent sections for shared products / readable cells — but keep it to ~15 minutes; this is an execution night.

## Paths
- Repo: `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design`. Your workspace (write ONLY here): `overnight-20261014/fabric-k64/`.
- Existing evidence to reuse: `reports/taalas-serial-word-nibble-k64-1280x320.json` (numerical contract: 4-bit index, UINT8 representative, signed 9-bit activation, 13-bit shared partials, 17-bit product, 27-bit accumulator; 20 row groups, 6,400 local books; 4,160-cycle schedule), `reports/taalas-projection-nibble-k64-affine.json`, existing RTL `build/taalas-serial/word-nibble-k64-1280x320/taalas_serial_tile.sv` + `tb.sv` + `inputs.hex`/`expected.hex` + `map_engine.ys` (prior Yosys mapping of `taalas_serial_engine`). Packed indices: `models/candidates/codebook-4bit-optimal-rectangular-k64/packed/encoder.ort-095.indices.bin` (and its manifest in that candidate dir). Graph node `node_MatMul_86_quant`, weight `val_89_quantized`, bias `blocks.0.ff.project_out.bias`.
- Python: `.venv/bin/python`. Tools: verilator, iverilog, yosys on PATH; full LibreLane 3.0.11 via `scripts/run_physical.sh <config.json>` (Nix; PDK gf180mcuD in `pdks/`).
- A sibling worker (W2) is doing a 320×320 version in `overnight-20261014/fabric/` — you may read its configs/scripts for LibreLane settings that worked, but don't write there.

## Task
1. Verify identities (hashes) of the selected tensor/indices/books against the candidate manifest and the report.
2. Build the COMPLETE projection per the proposal step 3: fixed selections (all 409,600 4-bit indices) and all books/representatives ON-CHIP, shared product generation, selection, recombination, accumulation, zero-point correction (activation sum × zero point), output buffering/read port, reset and control. No host-supplied weights. Testbench supplies activations only and checks outputs.
   - Variant **SC-ROM** (required): indices + books as standard-cell constant logic (labelled "standard-cell comparator" per the proposal).
   - Variant **ARRAY-PORT** (required): the same engine with the index array cut out behind a row-read port, so the custom readable-cell array can be costed separately from datapath/periphery.
3. Verify each variant bit-exactly against an independent numpy reference from the original `val_89_quantized` bytes and zero points (plus the existing `expected.hex` vectors), including reset-mid-vector and stall tests. Report counts.
4. Physical: full LibreLane flow for both variants (synthesis, floorplan, PDN power grid, placement, CTS, routing, RC extraction, multi-corner STA, DRC Magic+KLayout, LVS Netgen, antenna). Start at CLOCK_PERIOD 20 ns. Produce activity-based power (annotate VCD/SAIF from a real-activation simulation where possible; else default activity, labelled). Use `nice` and ≤ 6 threads locally.
   - If SC-ROM synthesis/P&R looks like it will exceed ~2.5 h locally, STOP that run, keep ARRAY-PORT going, and write `overnight-20261014/fabric-k64/CLOUD-REQUEST.md` with the exact config, file list and commands so the lead can run it on a cloud CPU machine. Do not use cloud yourself.
5. Deliver `RESULTS.md` + `results.json` in your workspace with the "Required result" table from the proposal: identity/correctness, area (routed mm², fabric vs arithmetic vs periphery vs routing), timing per corner + achievable MHz + cycles and µs per projection, power (dynamic/leakage mW, activity source, energy per projection), DRC/LVS/antenna, exact commands and tool/PDK revisions. Include a PNG layout render.

## Rules
- Write only inside your workspace; do not git commit/push; no cloud. Keep ≥ 20 GiB free on `/` (check `df -h /`).
- Print `W2b-STATUS: <step result>` after each major step.
- Prefer a verified, honestly bounded result over an unverified bigger one.
