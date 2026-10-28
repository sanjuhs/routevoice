# W15 batch 2 — partial chip integration

**Full-chip signoff is incomplete.** All twelve encoder/decoder fabric blocks are represented by 48 real array banks. Four signed-off W14 leaf macros are placed. Arrays still exclude control decoders, WL/PC drivers, latches and output escape; these remain `drivers=pending`. Remaining macro interiors are stubs.

| Die | Real banks / logic | Stubs | Driver reserves | Real / synthetic nets | Routed / unrouted | Router violations | Pre-fill top wiring | Merged main / antenna | Density before |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| A | 19 / 1 | 60 | 19 | 3 / 646 | 649 / 0 | 0 | 0 | incomplete / incomplete | 8 |
| B | 29 / 3 | 59 | 29 | 11 / 722 | 733 / 0 | 0 | 0 | incomplete / incomplete | 8 |

| Die | Native density before / after fill | M1–M5 post-fill coverage upper bounds (%) | Local fill spacing |
|---|---|---|---|
| A | 8 / incomplete | 12.88, 12.63, 10.90, 28.32, 24.31 | incomplete |
| B | 8 / incomplete | 13.03, 13.12, 10.90, 28.51, 23.59 | incomplete |

Pod die A: running; monitor status `monitoring`.

Pod die B: queued; monitor status `monitoring`.

Coverage bounds add exact dummy-square area to measured pre-fill union area. Unverified overlaps can only lower the union area. Bounds below 30% prove that minimum metal density remains unmet; they are not native post-fill DRC counts.

The 14 real scalar nets have direct source traces; database audit status is recorded per die in results.json. Package pad locations remain provisional. No functional data handshake between the selected leaves is claimed. The sequencer's gated clock and local resets without proven source bindings remain unconnected. One placed quantizer leaf does not implement the 176 quantizer instances in the recognizer hierarchy. See [connectivity](batch-2/connectivity/README.md) and [TOPLEVEL.md](TOPLEVEL.md).

Placement uses integer database units, with 60 µm gaps and no macro overlaps. The 48 driver placeholders debit 33.1546875 mm² pro-rata by installed rows from the existing driver allowance; the unused allowance remains reserved. See [geometry](batch-2/GEOMETRY.md).

Chip-channel metal fill protects every real macro/pad boundary and every unfinished stub/driver reservation. The full-layout fill trial timed out; its failure remains recorded. The native density deck measures global density, not sliding windows. Filled density/spacing evidence and derived area estimates are in [fill](batch-2/fill/README.md). Any incomplete native report remains null; derived estimates are not DRC passes.

Main and antenna checks run on the authorized existing pod under a shared three-CPU lock, with a three-hour aggregate bound per die. The main deck includes dummy checks with the required missing vendor constant explicitly initialized. Scoped pre-fill top-wiring zero applies to routed wires and abstract pins; it does not qualify added fill or imply merged full-chip DRC zero. See [pod results](batch-2/pod/reports/) and [preserved failures](batch-2/FAILURES.md).

| Die | PG VDD/VSS | Assumed-load IR drop/rise (V) | Full-chip LVS | Top STA / worst slack | Final-chip IR |
|---|---|---|---|---|---|
| A | PASS/PASS | FAIL: [0.869, 0.866] | Not run | Not run / null | null |
| B | PASS/PASS | FAIL: [1.44, 1.35] | Not run | Not run / null | null |

IR uses inherited floorplan load assumptions, not qualified final-chip activity or measured powers for every new macro. Fill changes coupling; post-fill extracted timing and analog-array behavior are unqualified. LVS and STA cannot certify the incomplete functional physical hierarchy. Original input hashes, routing receipts, PNGs and final artifact paths are in [machine-readable results](results.json). Large completed GDS files are checksum-verified in the authorized W15 SSD archive; active computation stays on the internal disk.

Artifacts: [A PNG](batch-2/A/layout.png), [B PNG](batch-2/B/layout.png), [A GDS](batch-2/A/die_A_FILLED.gds), [B GDS](batch-2/B/die_B_FILLED.gds).

W15-STATUS: batch-2 integrated 48 real array banks and 4 logic macros; drivers pending; full-chip signoff incomplete. Stopped for the lead’s next batch.
