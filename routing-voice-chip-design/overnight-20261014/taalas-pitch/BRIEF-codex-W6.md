# Codex brief W6: pitch-matched readout for the Taalas array (the biggest area lever)

AUTHORIZATION: the user lifted the 13 Oct pause on 14 Oct 2026 (recorded in `AGENTS.md`) and asked that the design "be like Taalas". The lead (Claude) re-checks everything. Never fabricate; preserve failures. Reading (≤10 min): `skills/taalas-fixed-weight-routing/SKILL.md`, then `overnight-20261014/taalas-array/RESULTS.md`, `results.json`, `INTEGRATION.md`, and `docs/TAALAS-TALL-BANK-BUDGET.md`.

## The problem the lead found
W5 built the real mask-programmed array for the 1280×320 K64 projection (409,600 four-bit selections, 1,638,400 bit cells), DRC/LVS clean.
- The cell array alone is **4.87 µm²/selection**: tile `base/tile0.gds`, 925.69 × 107.71 µm per 64 rows × 1,280 bit lines, so the bit-line pitch is ≈0.72 µm.
- The analog readout strip (`integrated/readout-tile0.gds`, 4,669.7 × 220 µm) puts 1,280 readouts side by side at ≈3.65 µm pitch, so **the array is stretched ≈5× horizontally to match the readout pitch**.
- Result: 64-row tiles 54.5 µm²/selection, 320-row banks 30.4, a 1,280-row bank 25.6. Most of that is pitch mismatch, not a fundamental cost.

## Goal
Build and measure a **pitch-matched** readout so the array keeps its native ≈0.72 µm bit-line pitch, using a 1,280-row bank (or the tallest bank W5's timing supports; check `taalas-array/` for the latest SS timing). Program it with the real indices of the projection (reuse W5's `indices.npy` / generators in `overnight-20261014/taalas-array/scripts/`).

Two options; pick the one you can make DRC/LVS-clean tonight, and report why:
- **(A) Stacked readout rows:** place the 1,280 readout circuits in ≈5 staggered rows under the array, so each readout gets ≈5 × 0.72 µm of width. Route bit lines down to their row on a free metal layer.
- **(B) Column multiplexing:** share one readout per k bit lines (k≈4–5) through access transmission gates, reading a row in k sub-phases. Report how many sub-phases fit in the cycle, given W5's measured 3–4.4 ns settling, or how many banks must interleave.

## Required measurements (same rigor as W5)
1. Selected GF180 KLayout DRC = 0 on the new bank (and on a 64-row test slice first).
2. LVS against an independently generated reference built from the indices, as W5 did (Netgen unique match). Include a negative control.
3. Layout-to-bits readback: all programmed bits match the real indices.
4. SPICE read on the extracted worst-case column (TT and SS 2.97 V 125 °C), reusing W5's decks/flow. Report settle time and energy per row read. If the simulator fails to converge, preserve that and say so.
5. **Area:** total bank area and **µm² per selection including readout**, versus W5's 25.6–54.5. Then extrapolate to the whole model (31,457,280 selections) with a clearly labelled formula, and compare with the October budget (≈154 mm² cells + ≈67 mm² periphery).

## Paths and rules
- Repo: `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design`. Workspace (write ONLY here): `overnight-20261014/taalas-pitch/`. W5 is still working in `taalas-array/`: read only, don't write there.
- Tools: KLayout/Magic/Netgen/ngspice via `source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh; NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run '<cmd>'`; Python `.venv/bin/python`.
- The Mac is busy: `nice`, ≤ 4 threads, keep ≥ 22 GiB free (`df -h /`). No git, no cloud.
- Print `W6-STATUS: <result>` after each step. Finish by about 05:45 IST with `RESULTS.md` + `results.json`, even if partial (say what's missing).
