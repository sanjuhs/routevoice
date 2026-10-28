# W9 additional flow findings

The accepted synthesis correction is proved on the mapped JSON and the placed OpenDB: maximum non-clock input-pin fanout 16, no non-clock nets above 16, ten distinct row bit-6 registers. Modified RTL passed 54 vectors / 17,280 outputs. Synthesis cell area is 6.434583 mm²; this is not routed area.

The requested-settings post-placement timing step completed after about 23 minutes. It propagates the **pre-CTS** clock directly to 11,784 register loads. Its `min.rpt` shows 52.318390 pF clock load, roughly 297–300 ns slew and 191.140198 ns insertion delay. This creates a −177.616547 ns input-to-register hold slack. These are not post-CTS or signoff results. The original mid-PNR report and flow are preserved.

`buf-v4-physical` continues all original settings from the same placed checkpoint while the read-only timing report ran independently. Its checkpoint/database hashes are recorded in `evidence/physical-continuation.json`. The original flow was stopped only after that STA step completed, to avoid duplicating later physical work.

A separate **diagnostic** run, `buf-v4-idealprects`, changes only the saved pre-CTS SDC from `set_propagated_clock` to `unset_propagated_clock`. It preserves the 20 ns period, numeric constraints, repair, CTS, routing and signoff settings. The pinned CTS script explicitly invokes `set_propagated_clock [all_clocks]` after clock tree construction (line 91). This diagnostic is a declared deviation from the brief's unchanged STA behavior, not a silent replacement for the requested-settings run. Its exact SDC hashes are recorded in `evidence/ideal-prects-deviation.json`.

The original serial mapped replay remains running. An eight-process replay covers all 54 vectors with disjoint ranges; its starting LFSR seeds reproduce the reference serial stall sequence. The aggregator requires all outputs, every vector, exact reference per-vector cycle counts, normal finish, and four abort tests in each process before releasing activity simulation.

## Clock hypothesis ruled out for repair
Source inspection subsequently confirmed `repair_design.tcl` explicitly calls `unset_propagated_clock [all_clocks]` immediately after reading the database. `DESIGN_REPAIR_REMOVE_BUFFERS` is false. Thus the separate ideal-SDC diagnostic is redundant for repair and was stopped; it receives no completion credit. The original pre-CTS STA clock artifact is real, but it does not explain the repair delay. See `evidence/ideal-prects-stopped.json`. The original requested-settings repair remains running.
