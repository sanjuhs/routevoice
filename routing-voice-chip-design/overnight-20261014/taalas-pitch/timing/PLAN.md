# W6 extracted pitch-matched readout characterization

Source reading completed: project routing skill, full supplied source notes, relevant P1/P2/P3 primary description and claims, root plan (14 October authorization supersedes its pause), W5 RESULTS/results.json/INTEGRATION and October tall-bank budget.

The primary target is the actual new Option A layout, not an area-only re-placement. Timing must re-extract receiver joining capacitance. Reusing W5 timing values after changing geometry is not valid.

Planned evidence:
1. Extract actual selected new bank/subbank with Magic `ext2spice cthresh 0`.
2. Independently compare access MOS topology/programming with original index image and all receiver MOS with the intended circuit. Normalize only bijective label prefixes.
3. Rank actual columns by total incident extracted metal capacitance, connected-drain population, and geometry resistance if layout joins are available. Report rank as a heuristic candidate, not a global transistor timing proof.
4. Test TT 3.30 V 25 C and SS 2.97 V 125 C with GF180 device models and repeated near/far/one/zero/simultaneous-switching row sequence. Preserve W5 90/10 output, 70/30 bitline, 95% precharge and phase thresholds.
5. Integrate actual source-current energy over the repeated sequence. A partial-column source-energy result is not measured full-row energy. Full-row energy stays null unless all 1280 columns and actual drive activity are simulated. Any scaled estimate is separately labeled with its exact formula.

Control/input/global supply endpoints and unspecified output load are explicit ideal boundaries. Distributed resistance is only added if derived from the actual new geometry and identified GF180 sheet/contact values; extracted-C-only results must say so. No full macro latency, achieved clock, mismatch/yield, or complete recognizer claims.

Resources: one thread, nice priority, no cloud/git, outputs only in this timing directory, minimum 22 GiB available internal disk. Failed decks/logs/traces remain preserved.
