# Source reading and scope

This same agent previously read the repository skill, complete supplied source-notes, patent atlas, architecture/numerics and implementation workflow, root `../plan.md`, and locally retained primary US20250123802A1 shared-product/readable-cell description and claims, US20260023566A1 stored-address descriptions/claims, and WO2025217724A1 shared-connection descriptions/claims. Prior reading receipt is `../../timing/READING.md`. The old pause is superseded by current explicit user authorization.

For this tall-bank task, refreshed the skill and read `docs/TAALAS-TALL-BANK-BUDGET.md` and `docs/TAALAS-MASK-INDEX-TALL.md` in full. Inspected existing `mask-index-tall/simulate_column_group.py`, `run_checks.py`, `generate_layout.py`, and W2b's CONTRACT, ARRAY-PORT top and engine schedule.

The reused circuit choices are pre2std4: 2.88 µm precharge PMOS, extracted stock buf_4 wordline and buf_20 precharge drivers. Existing synthetic-image timing is comparator evidence only. New runs must use actual real mask choices and new geometry/capacitance.

A four-bit selection uses four immutable one-transistor readable cells and selects a downstream shared product. It is not four-bit activation arithmetic or writable SRAM weight storage. Geometry-derived resistance and redistributed extracted capacitance are explicit models rather than automatic distributed RPEX. Sampled group simulations do not establish full-bank simultaneous current, integrated decoder-to-latch timing, mismatch tolerance or complete macro energy.
