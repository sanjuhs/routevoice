# Floorplan PDN/IR re-screen with the measured engine (lead, 14 Oct 2026, ≈09:55 IST)

The lead ran this after the overnight window closed. It is local only and used no cloud spend.

## What changed

The input is `blocks_measured_engine.json`. It is `blocks_final.json` with only the `shared_product_engine` block replaced; scenario `measured_engine` is a copy of `final_pitch`.

| Block field | Before (assumed) | Now (measured) |
|---|---|---|
| Engine area | 12.27 mm² (synthesis area ÷ an assumed 50% utilization) | **16.27 mm²**: the W9 `buf-v4` placed die (6.43 mm² of cells at 40% utilization), before repair |
| Engine power | 0.15 W | **1.077 W** |

The 1.077 W comes from:
- **0.798 W measured** (`../power-bufv4/RESULTS.md`): 100%-annotated real-activation SAIF, pre-route, continuous 50 MHz;
- multiplied by an **assumed 1.35** clock-tree allowance.

Running the engine continuously is the IR worst case. Real-time speech needs only about 12% duty (0.6 of 4.92 GMAC/s).

All other loads keep W3's assumptions. Chip total: 2.01 W for one die; 1.59 W and 1.57 W for the two dies. Supply pairs were raised to the power-derived minimum: 52 for one die, 40 per die for two dies.

## Results (PASS needs worst VDD drop + worst VSS rise < 165 mV, i.e. 5% of 3.3 V)

| Case | Straps | VDD worst | VSS worst | Sum | Result | Shorts | Previous (0.15 W engine) |
|---|---|---|---|---|---|---|---|
| One die 25×31 mm, dense SRAM | 40 µm | 136 mV | 141 mV | 277 mV (8.4%) | **FAIL** | 0 | 36 + 36 mV, pass |
| One die 25×31 mm, dense SRAM | 80 µm | 122 mV | 126 mV | 248 mV (7.5%) | **FAIL** | 0 | — |
| Two dies, die A 25×29 mm, open SRAM | 40 µm | 183 mV | 175 mV | 358 mV (10.8%) | **FAIL** | 0 | 40 + 39 mV, pass |
| Two dies, die A, open SRAM | 80 µm | 184 mV | 162 mV | 346 mV | **FAIL** | 0 | — |
| Two dies, die B 25×29 mm, open SRAM | 40 µm | 178 mV | 171 mV | 349 mV (10.6%) | **FAIL** | 0 | 43 + 40 mV, pass |
| One die 29×31 mm, open bit cell | — | — | — | — | placement FAIL (as before) | — | — |

- All cases: VDD/VSS connectivity passes (`PSM-0040`), the average drop is only 12 mV, and there are 0 power/ground shorts.
- **The worst point is the engine's own terminals** (`shared_product_engine_0` at 3.164 V in the die centre). The engine is 2 tiles × 0.54 W, each 2.86 mm square.
- Doubling the global strap width barely helps, so this is a **local hot spot** (≈66 mW/mm²), not a global grid shortage.

## What this means

- **At full-rate continuous operation**, the measured engine breaks the 5% IR budget everywhere it sits.
- **At real-time duty with clock gating** (≈0.13 W average), the earlier 0.15 W screen, which passed, is the representative case. This is an inference, not a separate run.
- **Fix options** (not yet tried):
  1. a dense local power grid or more supply pins over the engine;
  2. placing the engine next to the supply pads instead of in the die centre;
  3. splitting it into more, smaller tiles;
  4. clock-gating it to its real-time duty.

Runs: `runs/measured_engine_*`, logs in `logs/measured_engine_*.log`.

## Re-screen at the achievable operating point (lead, 14 Oct, ≈20:20 IST)

The 1.077 W load above assumes the engine runs continuously at 50 MHz. The engine cannot do that: its measured critical path is ≈145 ns (≈7 MHz before repair), and it is now being routed at **150 ns**.

**Load used:** measured energy per projection × achievable rate, per `blocks_measured_engine_150ns.json`:
- 66.4 µJ ÷ (4,163 cycles × 150 ns) = 0.106 W;
- × 1.35 assumed clock-tree allowance = **0.144 W**.

At 150 ns the engine delivers 0.66 GMAC/s, just above the model's ≈0.6 GMAC/s real-time need, so this is also the real-time operating point. Other loads keep W3's assumptions. Supply pairs are back to W3's 48 / 32.

| Case | VDD worst | VSS worst | Sum | Result | Shorts |
|---|---|---|---|---|---|
| One die 25×31 mm, dense SRAM | 38.7 mV | 39.1 mV | 77.8 mV (2.4%) | **PASS** | 0 |
| Two dies, die A 25×29 mm, open SRAM | 47.0 mV | 43.1 mV | 90.1 mV (2.7%) | **PASS** | 0 |
| Two dies, die B 25×29 mm, open SRAM | 44.9 mV | 40.5 mV | 85.4 mV (2.6%) | **PASS** | 0 |

- VDD/VSS connectivity passes in all three (`PSM-0040`).
- The 29×31 mm open-bit-cell one-die case still fails placement, as before.
- Runs: `runs/measured_engine_150ns_*`.
- **Conclusion:** at the engine's real, achievable clock, the measured engine fits the existing power grid with margin. Only a 50 MHz engine (which would need pipelining first) would need a local grid.
- The routed power for this engine replaces the 0.106 W estimate when routing finishes (`../power-bufv4/`, lead-route-150ns).
