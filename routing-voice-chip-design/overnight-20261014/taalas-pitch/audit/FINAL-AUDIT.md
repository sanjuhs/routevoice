# W6 final independent audit

The independent audit found no blocking geometry, area arithmetic, extraction-provenance, or primary timing-result calculation error in the reviewed artifacts. **The 60 ns full-control loading sensitivity fails precharge and phase checks; its guarded SS 120 ns follow-up passes the sampled protocol. The guarded TT 120 ns companion was stopped by the disk guard and remains incomplete.** Passing primary subbank simulations therefore do not qualify 60 ns full-bank service. Complete simultaneous row energy remains unknown.

The audit used the required repository skill, complete supplied source notes, relevant supplied primary patent descriptions/claims, root plan (pause superseded), W5 reports, and October budget. Its source-reading confirmation remains in `RESULTS.md`. All audit writes stayed in `audit/`; no simulator, DRC, LVS, cloud, or git operation was run by this auditor.

## Geometry, physical proof and area

Both reopened W6 GDS revisions pass 13,070 explicit geometry checks each, covering all bitline M2/M3/M4 joins and Via2/Via3 sites, receiver input endpoints, 1,280 output metal label landings, and receiver PC/VDD/VSS spine connections. This geometric audit complements, rather than replaces, the independent extraction/LVS work. Reviewed final full-bank receipts report 1,643,520 exactly matching devices, bijective node normalization, Netgen unique match without property errors, and rejection of the doubled-precharge-width negative. The negative correctly remains rejected despite Netgen's topology-match phrase. DRC remains selected open-flow checks excluding density/antenna, not foundry signoff.

Independent GDS dimensions confirm **1004 × 2258.81 µm = 2.26784524 mm²**, or **5.53673154296875 µm² per selection**. This includes actual array, analog readout and joining/common metal, with output escape and major physical periphery excluded. Uniform multiplication by 31,457,280 selections gives **174.170514432 mm²**; it does not allocate the 98 actual tensor shapes, ports, padding, timing-driven bank replication, or tied-head transpose access.

The 78.4% area improvement is against W5's stretched 1,280-row physical rectangle. The October array/receiver subtotal was 164.837 mm², 9.333514432 mm² below W6's uniform extrapolation. Adding the older nonreceiver component terms produces 230.754514432 mm² with mixed allocation/utilization scopes, not a complete macro or die-fit result.

## Capacitance evidence

Read-only source/receipt review confirms the official full-bank capacitance export preserved all 1,643,520 MOS lines byte-for-byte versus the original LVS export. Its producer-stream and independently decompressed hashes match; the source native `.ext` remained unchanged. The ranking source counts every signed capacitor record and enforces bijective bitline/control names. The receipts report 6,205,260 capacitor records, including 823,970 zeros and no numerically negative capacitance.

This auditor independently checked the receipt hash chain, all 1,280 unique ranked IDs, every reported RC-score unit calculation and sorted order. Highest extracted incident metal C and highest C/geometry-R proxy both select **global bit 1153**, **680.09041 fF**. Maximum connected-drain count is separately 714 and is not the same criterion. Exact Decimal recomputation confirms that candidate 1153's **2,632 incident pair sums** match the extracted subbank crop with zero changed pairs and zero total delta.

This is a source/receipt audit: the auditor did **not** independently reread the 1.124 GB capacitor stream. Candidate-pair equality does not prove equality for every other selected column, native distributed-R equivalence, control timing, or simultaneous full-bank current.

## Independent G09 trace analysis

`recheck_timing.py` reads saved compressed traces using their own column headers and independently recomputes output/raw/precharge/phase thresholds, last-violation settling, 20 ns capture aperture failures, and signed source-energy integration. It imports no timing-worker analyzer. All recomputed fields agree with the retained results.

| Case | Output/raw/precharge/phase failures | Maximum sampled settle, ns | Failed 20 ns checks | Partial net source energy, pJ/commanded read |
| --- | --- | ---: | ---: | ---: |
| Primary G09 TT, 60 ns | 0 / 0 / 0 / 0 | 15.415282 | 0 / 160 | 105.762760544 |
| Primary G09 SS, 60 ns | 0 / 0 / 0 / 0 | 23.443325 | 18 / 160 | 84.441125435 |
| G09 full-control sensitivity SS, 60 ns | 0 / 0 / 63 / 10 | 32.353378 | 80 / 160 | 322.286158842 |
| G09 guarded full-control sensitivity SS, 120 ns | 0 / 0 / 0 / 0 | 31.6883824 | 80 / 160 | 149.860012638 |

The full-control 60 ns row is **diagnostic evidence from a failed protocol**, not qualified read timing or read energy. All 320 final data capture checks pass even in that row, demonstrating why data values alone are insufficient for protocol acceptance. The authorized guarded SS follow-up passes the sampled 120 ns protocol. An independent deck comparison confirms that all MOS/R/C/model/temperature/supply/options/column-meter lines are byte-identical between the failed SS 60 ns and passing SS 120 ns cases; only commanded phases, observation times and transient duration change.

The guarded TT 120 ns companion was stopped by the authorized disk guard at 22.132843 GiB free, before the 22 GiB floor, after its log reached approximately 869.810 ns of the requested 1,200 ns transient. The watchdog receipt preserves the original-process extension and subsequent owned-process termination. There is no final trace or timing/energy pass to audit; this is resource-incomplete, not demonstrated convergence failure or an electrical protocol failure. The completed primary TT 60 ns slice result remains valid within its smaller loading scope. Independent deck checks confirm the guarded TT MOS/C, resistor connectivity, solver options and phases match the guarded SS companion; TT intentionally uses the typical model, 3.3 V, 25 °C and the corresponding 0.104 Ω/square geometry-resistance coefficient rather than SS's 0.138632 Ω/square.

Primary timing still includes only 16 actual full-height columns, 112 ideal bitline aggressors, 128 real receivers and selected unplaced stock drivers, with modeled geometry resistance and ideal supply boundaries. The full-control sensitivity adds other-bank gate loads and full-bank control metal capacitance through an explicitly approximate distributed model; it does not simulate all 1,280 actual array currents. Phase checks inspect every modeled control terminal. Neither model is a placed decoder/phase/latch/PDN implementation.

The zero-volt column meters correctly observe receiver MOS supply/well current. Explicit extracted VDD coupling capacitors bypass those meters as documented. Meter energy is already included in the main receiver-source total. The prior ambiguous “worst-column energy” heading was corrected to timing-candidate energy; it is not an energy maximum. Signed negative ideal-aggressor source work is preserved rather than clipped. Recorded timestep resolution is approximately 0.2 ns; six-decimal timing values are trace-derived diagnostics, not corresponding measurement precision.

## Receipts and boundaries

`final-audit.json` indexes the machine-readable audit receipts. `geometry-audit.json` records direct GDS geometry/area checks; `final-cap-receipt-audit.json` records the capacitance receipt/score/pair checks; `final-timing-trace-audit.json` records independent final trace recomputation; `guarded-physical-deck-audit.json` records the exact unchanged SS physical circuit comparison. `TIMING-AUDIT.md` and `timing-trace-audit.json` retain the earlier G02 audit rather than silently replacing its coverage.

No full-row energy, complete ARRAY-PORT timing, output escape, full macro integration, production yield, die fit, or sub-watt proof follows from this audit.

W6-STATUS: independent final audit complete. Reviewed geometry, capacitance receipts and all four completed G09 traces agree; full-control 60 ns failure and guarded TT 120 ns resource-incomplete status are preserved. Guarded SS 120 ns passes only the stated sampled sensitivity.
