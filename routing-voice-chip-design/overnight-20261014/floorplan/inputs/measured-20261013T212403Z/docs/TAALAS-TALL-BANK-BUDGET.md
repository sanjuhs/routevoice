# Larger fixed-index banks: revised component budget

The sampled 256-, 320- and 1,280-row banks now qualify for the same
component search. All five selected `pre2std4` circuit cases pass the stated
read, raw-margin, precharge and phase checks. These are immutable mask indices,
with shared products selected downstream. Mutable speech state is accounted
separately.

The [circuit report](TAALAS-MASK-INDEX-TALL.md) includes geometry-derived wire
resistance, extracted capacitance and stock wordline/precharge drivers. The
1,280-row slow-corner precharge result has only **1.54 mV** of margin above the
declared threshold. It does not establish mismatch tolerance or production
yield. Decoder-to-latch timing, simultaneous full-bank current, actual latch
loads and complete physical integration remain open.

The new [allocation search](../reports/taalas-tall-bank-die-budget.json)
chooses a qualified bank height separately for every matrix, including padding,
bank-local receivers and the measured digital selector hierarchy. The selected
whole-model component sums are:

| Component | Footprint sum, mm² |
| --- | ---: |
| Fixed-index base arrays | 153.833 |
| Local receiver strips | 11.004 |
| Decoder cells | 25.002 |
| Wordline-driver cells | 30.369 |
| Precharge-driver cells | 0.269 |
| Bank-selector cells | 0.944 |

Custom-layout bounding boxes and summed standard-cell footprints are different
measurements; their sum is not a placed macro. The calculation retains a
declared **30% logic utilization** for the digital terms. This is an assumption,
not whole-chip placement evidence.

For query microbatch B8 with central adapter memory, the best largest per-die
accounted subtotal is:

| Dies | Largest accounted subtotal, mm² |
| --- | ---: |
| 1 | **933.697** |
| 2 | **545.307** |
| 3 | **476.712** |

The one-die case still includes **580.248 mm²** of available 512-byte SRAM
macros for 1,418,520 named mutable-state/scratch bytes. Compact mutable-memory
alternatives are being measured separately. Fixed weights are never priced as
writable SRAM in this construction.

The script runs 18 combinations of B8/B16/B32, two memory-ownership policies
and one/two/three dies. Each die-count search checks 1, 98 or 2,352 allocations,
respectively. All 31,457,280 selection positions are accounted for in every
partition. Source reports are copied into timestamped snapshot directories;
the earlier result that excluded the then-pending 1,280-row bank is preserved.

These are **partial component budgets**. Complete compute engines, frontend,
head access, dynamic operations, actual parallel buffers/ports, physical
integration, pads, links and system power are still missing. The canonical
tied-table orientation does not demonstrate its transposed head access.
Neither this table nor the older 64-row construction proves a die count or a
universal lower bound. No maximum die dimensions have been selected.

Reproduce with `scripts/analyze_taalas_tall_die_budget.py`. Full-fit and minimum
die-count fields deliberately remain unproved in the machine-readable result.


## K64 trace and corrected W144 state ledger

A separate [K64 search](../reports/taalas-tall-bank-die-budget-k64.json) pins
the candidate that passed the reserved pilot test and checks all98matrix
shapes against its manifest. Its observed encoder window is144frames; the
F500/T67/Q67 bounds remain proposed envelopes, not jointly proven continuous
controller maxima. No earlierW140result is silently relabeled.

With B8central memory, the revised largest per-die partial component sums are
**941.026 / 550.542 / 481.947mm²** for1/2/3dies. One-die named mutable state
and scratch total1,436,216bytes, occupying587.577mm² in the available small
macros. Fixed-array components are unchanged because matrix dimensions are
unchanged. All18searches independently conserve the31,457,280positions, every
component sum and whole-macro ceiling.

K64has491,520localbooks and7,765,892representative bytes. The fixed-book
lookup/distribution cost belongs to the still-incomplete compute ledger; these
bytes are not free, and they are not silently priced as SRAM weights. A small
projection's hardwired books cannot be shared across every matrix without a
real selection/access implementation. Complete-chip fit remains unproved.


## Source-default W500 envelope supersedes the observed-window assumption

The [controller source audit](TAALAS-NATIVE-STATE-BOUNDS.md) now derives
W500/F500/T67/Q67 for the default path. W144 remains only the observed trace
scenario above; its smaller scratch capacity is not a default guarantee.

The separate [source-bound search](../reports/taalas-tall-bank-die-budget-k64-source-bounds.json)
repeats all 18 searches with the larger encoder window. B8 central-memory
largest per-die component subtotals are **1,585.141 / 1,008.291 / 939.696 mm²**
for one/two/three dies. The one-die named state and scratch are **3,011,160 bytes**,
occupying **1,231.692 mm²** in the existing 512-byte macros. B16/B32 named totals
are 3,153,400 / 3,437,880 bytes. All index sites, per-component partition sums,
state sums and whole-macro ceilings were independently checked for all 18 cases.

These remain incomplete construction budgets. The compact mutable-array study
has no completed macro density yet, so it receives no area credit. A smaller
scheduled encoder window requires an explicit new service contract and
numerical/quality validation; it cannot be adopted merely to make a die fit.

Reproduce using `study_taalas_k64_live_buffers.py --source-bounds`, then
`analyze_taalas_tall_die_budget.py --k64-native-ledger --source-bounds`.
