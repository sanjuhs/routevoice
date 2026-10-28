# W6 independent design and reporting audit

The audited revision has no identified geometry or area-accounting blocker within this audit's scope. This is an independent read-only audit, not DRC, LVS, extraction, or electrical qualification. All audit writes are confined to this directory. No git/cloud operations or heavy EDA jobs were run.

## Source reading

Read the repository `skills/taalas-fixed-weight-routing/SKILL.md` and complete `references/source-notes.md`; consulted the patent atlas, architecture/numerics and implementation workflow. Read the relevant supplied primary descriptions/claims for US20250123802A1 (shared products, access-transistor/read circuit, Figure 4–6 mechanism), US20260023566A1 (stored-address and connectivity branches, serial signaling and programmable representatives), and WO2025217724A1 (mask-defined shared connections, physical limitations and serial product transport). Read current root `../plan.md` with its pause explicitly superseded by the user's 14 October authorization, W5 `RESULTS.md` and `INTEGRATION.md`, and `docs/TAALAS-TALL-BANK-BUDGET.md`.

The implemented layout is the four-access-NMOS stored-index branch followed by separate lookup/shared arithmetic, not the direct one-access-transistor product-selection embodiment. Nothing in these readings establishes a shipped Taalas netlist or measured GF180 whole-chip area/power.

## Independent geometry checks

`geometry_audit.py` reopens both retained GDS files and independently reconstructs the expected bitline centers/receiver correspondence rather than consuming the build's route list. Each layout passes 13,070 explicit geometry checks: every M2/M3/M4 bitline joining segment, its Via2/Via3 locations, every receiver input endpoint, all 1,280 output-label metal landings, and the receiver supply/PC spines' eight-row via connections. The construction's shared top-level horizontal rails meet these receiver spines; source inspection also shows physical array-ground joins at both strap ends.

| Revision | GDS dimensions µm | Rectangle µm² | µm²/selection |
| --- | ---: | ---: | ---: |
| `r64-v2` | 1004 × 234.17 | 235,106.68 | 11.479818359375 |
| `r1280-v2` | 1004 × 2258.81 | 2,267,845.24 | 5.53673154296875 |

Hashes and machine-readable checks are in `geometry-audit.json`. Full electrical connectivity is delegated to extraction/LVS, which is stronger evidence than these geometric spot-class checks. Inspection of the existing 64-row verification flow confirms that hierarchical name normalization is bijective; it does not merge similarly named disconnected nodes. Its exact device/W/L comparison passes for 87,040 devices, its Netgen comparison reports unique match without property errors, and the doubled-width negative control is rejected. The negative also prints the topology-match phrase: the verifier correctly rejects it because property errors exist.

The local bitline pitch is 0.66 µm, with a 1 µm corridor every 16 bitlines. Its average is `11.56/16 = 0.7225 µm`, consistent with the brief's approximate 0.72 µm. The full bank's width per line is `1004/1280 = 0.784375 µm`, including group/edge allowance. Eight staggered receiver rows are a defensible reuse of the already characterized legal receiver geometry; the brief's approximately five rows is not a mandatory count.

## Area accounting

The headline reduction versus W5's physical 1,280-row rectangle is valid for the common partial scope: `1 - 5.53673154296875/25.640028 = 78.4059%`. It is not a complete-projection saving.

The uniform model formula is correct:

`31,457,280 selections × 5.53673154296875 µm²/selection / 1,000,000 = 174.170514432 mm²`.

This applies a single 1,280-row rectangle density to every selection. It does not allocate the 98 actual tensor shapes, padding, required ports, bank heights, replication, lookup books, or transposed tied-head access. If shorter timing-qualified banks or replication are required by the final service contract, this extrapolation must be replaced by that allocation.

October's arrays plus receiver strips are `153.833 + 11.004 = 164.837 mm²`. Its remaining listed decoder/WL-driver/PC-driver/bank-selector terms sum to `56.584 mm²`. Thus the mixed estimate `174.170514432 + 56.584 = 230.754514432 mm²` is arithmetically correct and avoids double-counting old receivers. It exceeds October's `221.421 mm²` subtotal by `9.333514432 mm²`; W6 should not be described as an improvement over the older October component budget. That budget mixed custom rectangles with digital cell-footprint/utilization assumptions, so the mixed estimate remains an engineering comparison, not a placed macro or lower bound.

## Required qualifications to retain

1. State that selected GF180 DRC excludes density and antenna, rather than calling it foundry signoff. Final report must incorporate the final full-bank DRC and independent LVS receipts; those checks were not rerun by this auditor.
2. Output labels are on real metal, but output escape, downstream codebook/latch access, physical decoder/WL/PC drivers, phase controller, and global power integrity remain unimplemented/unqualified. Narrow spines and physical ground continuity do not establish simultaneous full-bank IR/EM performance.
3. The timing worker's 16 actual active columns plus 112 ideal aggressors and 128 receivers is a sampled slice. Source energy for that circuit is not a 1,280-bit row measurement. Preserve `complete_row_energy_pj: null`. Scaling the whole slice energy by 10 or 80 would miscount shared controls, ideal aggressor sources, receivers, and unmodeled simultaneous supply loading.
4. If any optional estimated full-row energy is later supplied, separate active column/receiver energy from shared control energy, use real programmed-population and receiver-class weighting, include full physical fanout loading once, and clearly mark exclusions. No such estimate is needed to report the present measured slice honestly.
5. Proxy ranking by programmed drain population and geometry resistance followed by extracted capacitance within a selected subbank is a heuristic sampled worst-case search, not an exhaustive worst-case proof across all PVT, address transitions, coupling and supply patterns.
6. A passing sampled read/precharge protocol is not address-to-representative capture timing. W5's tall-bank SS result was substantially slower than the 64-row 3–4.4 ns figures cited in the brief. Use the newly measured W6 tall-bank protocol and do not transfer the short-slice timing.

W6-STATUS: independent geometry/area audit PASS within stated scope; no identified blocker; final physical/timing qualification belongs to the independent workers' receipts.
