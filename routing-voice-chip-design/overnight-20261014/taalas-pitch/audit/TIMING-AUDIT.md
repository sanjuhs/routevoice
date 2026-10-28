# Bounded timing source/data audit

One reporting correction is actionable: rename **“Worst-column receiver MOS supply”** to **“Receiver MOS supply energy of the timing candidate (global bit 273)”**, or give the separately observed energy maximum as well. In the retained SS 60 ns case, bit 273 is the load-proxy candidate and observed slowest timing column, with 5.328008728 pJ/read receiver MOS supply energy. It is not the highest-energy selected column: global bit 282 (local 26) measures 7.903973011 pJ/read. The existing detailed scope prevents whole-column or full-row energy confusion, but the abbreviated heading can still be misread as an energy maximum.

No blocking mapping, unit, power-sign or corner error was found in this bounded audit of `timing/simulate.py`, `protocols.py`, `rank_caps.py`, `normalize.py`, `verification/rank_caps.py`, and the retained SS deck/build/result/trace. TT's deck uses `typical`, 3.3 V and 25 °C; SS uses `ss`, 2.97 V and 125 °C. The TT completed result and full-bank ranking were not yet available at this audit snapshot and receive no independent result pass here.

An independent gztrace/header-based recomputation, without importing the analyzer, confirms all 320 capture checks pass; 12 of 160 bit checks fail at 20 ns after WL command; and the maximum recorded settling sample is 23.376321 ns at cycle 5, row 0, global bit 273. These are 20 ns aperture failures inside a 60 ns repetition protocol, not a separately simulated 20 ns repetition case. Captures use restored 90/10 and raw 70/30 thresholds. The trace's maximum time step is 0.2 ns; rounding displayed timing to approximately 23.38 ns avoids implying six-decimal timing precision.

Independent source-energy integration over 300–600 ns, divided by five reads, reproduces pr/pw/pp/pa = 89.417014206 / 1.120349169 / 7.847541389 / 0.131935008 pJ/read, totaling 98.516839771 pJ/read for the explicitly partial circuit. The inserted zero-volt meters correctly use positive rdd-to-column current and energy `V(rdd) × I(Vcolumn)`. Receiver MOS VDD/source/well connections go through the meters; explicit extracted VDD coupling capacitors remain on rdd, as documented. The per-column quantity is already a subset of pr and must not be added again.

`timing-trace-audit.json` preserves the independent SS check counts, failing samples, and maximum settling observation. No EDA or simulation was run; all writes remain in `audit/`.

W6-STATUS: timing source/SS-trace audit complete; one ambiguous energy heading to correct, no blocking calculation error found in the audited scope.
