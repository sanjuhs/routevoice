# Routed, activity-annotated power: 1280×320 engine (lead, 22 Oct 2026, run locally on the Mac)

The pod-side power step failed with `STA-0169 SAIF syntax error` at line 7,207,294. The cause was two Verilator-traced, cell-internal UDP instance blocks named `$unnamedudp1`, which OpenSTA's SAIF parser rejects. The pod was deleted on 22 Oct ≈18:35 IST, so the lead restored the inputs from the checksum-verified Hugging Face backup (`sanjuhs/routevoice-pod-final-20261022`), removed those 2 blocks (4 lines; `clean_saif.py`, no other change), and re-ran.

## Inputs
SHA-256 verified against the pod manifest (`inputs-verified.sha256`):
- the final routed ODB of `w10-route/runs/full`;
- its signoff SDC (150 ns);
- the **nominal extracted SPEF** (RCX);
- `gate-output/activity-150ns.saif`: the mapped-netlist gate simulation of one real speech projection, 4,163 cycles, time base 150 ns.

The library is GF180 7-track TT 25 °C 3.3 V. The script is `power.tcl` and the full log is `power.log`.

## Results (TT, extracted parasitics)

| Quantity | Value |
|---|---|
| Pins annotated from the SAIF | **1,364,228 annotated, 32,552 unannotated (97.7%)** |
| Power at the 150 ns SDC clock | **0.158 W**: sequential 25.3 mW, combinational 114 mW, clock tree 18.8 mW, leakage 0.043 mW |
| Default-activity power (bound only) | 0.101 W |
| **Energy per projection** (P × 4,163 × 150 ns) | **≈98.7 µJ** |
| **Energy per MAC** (÷ 409,600) | **≈241 pJ** |
| At the achieved TT clock (setup-limited, 223 ns ≈ 4.48 MHz) | ≈0.106 W; the same ≈98.7 µJ/projection, because leakage is negligible |
| Post-route STA in this run | setup WNS −72.94 ns, hold WNS +0.541 ns (matches the flow's 16-stapostpnr) |

## Comparison
- Pre-route placed estimate (W9 buf-v4, no clock tree, placement RC): ≈162 pJ/MAC.
- Routed with a real clock tree and extracted wire capacitance: **≈241 pJ/MAC**.
- At the model's ≈0.6 GMAC/s real-time load, matrix compute is ≈0.145 W.

## Limits
- The activity is zero-delay, so glitches are not modelled.
- The unannotated 2.3% are most likely CTS/repair/antenna cells absent from the mapped-netlist simulation.
- The engine does not meet 150 ns setup (antenna violations open, see `../RESULTS.md`). Energy per projection is the robust figure.
