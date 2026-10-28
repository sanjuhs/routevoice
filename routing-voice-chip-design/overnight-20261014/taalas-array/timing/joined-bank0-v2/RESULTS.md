# Physically joined bank0 timing — 14 October 2026

The parent revision2 `RV_JOINED_BANK_00_0` passes the selected DRC scope with zero markers. All 8,704 extracted devices match independent expected real-mask/receiver connectivity and W/L. Independent native Netgen LVS also reports circuits match uniquely; the doubled-device-width negative control is detected as a property mismatch. Actual layout routes connect the 64×32 array to 128 physical precharge/keeper/inverter receivers; their capacitance is included. This replaces the ideal array-to-receiver joins only for this measured bank.

Image: rows 0–63 and columns 0–31 of the actual K64 projection. It is distinct from the maximum-population slice (tile17/bank1), and is not a proof of full-array worst-case behavior. Incident bitline capacitance ranges 42.46403–108.14671 fF, maximum at IDX31_0.

| Corner | Period ns | Raw/restored errors out of 1,024 | Latest sampled settled point after evaluate ns | Mean pJ / 32-lane row | Max pJ / 32-lane row |
|---|---:|---:|---:|---:|---:|
| typical 3.3 V 25 °C | 25 | 0/0 | 2.976 | 77.717 | 85.087 |
| ss 2.97 V 125 °C | 25 | 0/0 | 4.378 | 62.375 | 68.155 |
| typical 3.3 V 25 °C | 20 | 0/0 | 2.976 | 77.709 | 85.077 |
| ss 2.97 V 125 °C | 20 | 0/0 | 4.390 | 62.275 | 68.019 |

Eight local rows [0,1,6,7,15,31,47,63] are exercised. Evaluate begins at 2.5 ns; capture is at 17.5 ns for the 25 ns protocol or 12.5 ns for 20 ns. Raw thresholds are 70/30% VDD and restored thresholds 90/10%. The latest sampled settled point is after the last violating observation up to capture, not a signed-off delay. Energy excludes startup row0 and averages seven subsequent reads; actual nets, physical receiver devices, ideal WL/PC/VDD source power and 10 fF output load are included.

Remaining limits: no distributed wire resistance, actual WL/PC drivers or decoder, full 320-lane row loading, tile/bank mux, capture latches or matched output load, PDN drop/noise, statistical variation, worst-bank/worst-transition proof, or full-recognizer schedule/power. The complete macro timing/energy fields remain null. W2b requires 1,280 index reads per projection; 4,160 is its integer engine cycle count. A pass at 20 ns for this ideal-driver bank is not an integrated 20 ns macro qualification.

The first joined layout failed 129 Via2 enclosure checks; that version is retained at `../joined-bank0-v1/`. Revision2 contains the parent Metal2 landing fix. Exact commands are in `../COMMANDS.md`; all corner decks/logs/traces remain adjacent.
