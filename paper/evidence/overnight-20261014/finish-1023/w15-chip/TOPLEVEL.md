# W15 top-level integration contract

This workspace contains two distinct artifacts. `functional/` preserves the exact recognizer-derived eight-child wrapper, all ports and glue. `smoke/{A,B}/` exercises routing on the requested 25 × 29 mm outlines with the original area tiles and real GF180 IO pads. The smoke circuit is an eight-bit chain through synthetic blackboxes; it is not recognizer wiring, a die-link implementation or a functional partition.

The saved floorplan has 68 A and 69 B tiles, including one link allowance per die. Its A/B assignment is a greedy area balance. Logical resources can span several tiles and both dies. Two engine tiles on each die represent one complete engine allowance, not two engines. Whole-engine W10 GDS cannot be split across those two squares without a new legal placement.

The byte-identical `rv_allonchip_top_all_v2` wrapper exposes 699 ports / 23,219 bits (312 input, 22,907 output), including extensive observability. Its real eight children are `original`, `decoder_body`, `decoder_self`, `encoder_head`, `encoder_O`, `positions`, `encoder_memory`, and `frontend_rom`. `functional/interface-audit.json` records exact interfaces and compiler-resolved connections. All service ready/valid, identity and arbitration equations remain intact. Dynamic attention and writable state remain inside the opaque original hierarchy; neither has been removed.

## Required integration handoff

W14 must deliver exhaustive hierarchical instance and memory ownership, exact macro module/port/parameter views, mapped glue, per-die assignment and crossing edges. W13 must provide actual bank pin views plus decoder/driver/latch ownership; its analog banks alone do not replace a recognizer service. Macro GDS, LEF, timing, netlist and DRC/LVS receipts must agree on names, pins, size, supplies and source hash. W10's complete engine needs a single legal rectangle per die or a qualified physical subdivision.

The final package interface needs implemented serialization/control for PCM, setup, start and completion transactions; token output; clocks/reset; test/debug; and backpressure. The die link requires an implemented protocol, link endpoints, ownership, bandwidth and reset/drain proof. Sixteen old illustrative signal-pad names do not specify these circuits. No protocol is silently invented by this smoke test.

## Smoke implementation

`prepare.py` restores the archived baseline Tcl/abstract LEFs into W15, hashes source manifests, adds eight DI and eight DO pins per tile, opens a four-micron signal-access strip in the Metal1–3 obstruction, and connects a spatially ordered chain through every tile. Die A has 552 bus nets and B has 560. All 16 real `bi_t` pads are used as eight inputs/eight outputs. Bond BTerms coincide with actual PAD shapes and are marked special: the package contact needs no extra on-die router segment. The first DRT attempt failed on bond PAD access before this correction; its log is retained.

Pad IE/OE and unused controls are connected logically to supply nets. The first PDN check proved these mode pins were not physically connected by ordinary PDN generation. `pad-repair/` now adds explicit exterior M2/M3 feeds and vias to the existing same-net ring; both VDD/VSS connectivity checks pass. The first attempted `add_sroute_connect` repair crashed and its receipt is retained separately. Six original signal via landings require same-net M2 minimum-area patches; the final revision appends these to regular wires while asserting every old wire opcode/data prefix unchanged. Check exact DRC/IR receipts for the selected revision.

PG geometry and assumed loads initially retain the final floorplan baseline (including 0.15 W engine allowance). This is NOT W10 routed power or a new 150 ns measured-load screen. Macro timing is absent, so no fabricated Liberty or zero-slack STA result is generated.

## Signoff gates

An assembled smoke GDS may contain real pad geometry and routed top metal but still lacks every recognizer macro interior. Its KLayout result is scoped to that assembly. Full-chip LVS requires extracted physical connectivity, a matching complete source netlist, and verified macro blackboxes with their own LVS receipts. Netlist self-comparison is not LVS. Full-chip STA requires characterized views, clock/reset constraints and actual link/package timing. Full-chip IR must use the final connected grid and qualified loads. `results.json` uses null for unavailable measurements.

All writes are under W15; active inputs and runs are internal. Native tools use one thread per job and the runner enforces 22 GiB free space plus finite run time. No pod is launched. Reading basis: repository Taalas skill and complete supplied notes; patent atlas, numerics/workflow and die-count requirements; relevant preserved P1/P2/P3 descriptions and claims; parent `../plan.md` because root `plan.md` is absent. The older parent pause is superseded by the user's 21 October authorization.

## Batch 1 update (21 October)

See `batch-1/RESULTS.md` and root `RESULTS.md` for the current assembly. Encoder L0/L2/L4 real banks are on A; L1/L3/L5 on B. The signed-off W14 position-control leaf is on A. Driver strips remain pending, and retained stubs preserve unresolved ownership. The frozen `batch-1/partition-snapshot.json` still has no complete pin-level inter-block netlist. All608routed test nets per die are synthetic; zero real recognizer signal nets are credited. Array raw WL/PC/OUT interfaces cannot be substituted for a qualified digital service endpoint without the missing periphery. The real macro pins have explicit supply feeds and pass PG connectivity, but inherited-load IR fails; old stub IR is superseded for this batch.


## Batch 2 connectivity update (21 October)

`batch-2/build.py` now assigns 14 source-matched scalar nets: die A has 3 real plus 646 synthetic nets (649 total), and die B has 11 real plus 722 synthetic nets (733 total). These are generated connectivity counts, not routing or signoff results. `batch-2/connectivity/nets.json` preserves source hashes and exact direct-alias paths through W12's specialized hierarchy. `check_odb.py` checks final database membership, every expected endpoint, extra endpoints, pad modes and intentional clock/reset exclusions; its per-die `actual-*.json` receipts establish the executed scope.

The A real nets carry raw clock, active-high common reset and the separate producer power-on reset to position control. The B real nets carry raw clock to phase control; common reset to phase control and the token sequencer; begin, compact-setup and source-start inputs to phase control; both phase-enable outputs; and token EOS, sequence-done-valid/EOS and recovery-required outputs from the sequencer. There is no claimed direct data handshake between these four selected leaf macros. The package assignment is provisional: the historical `reset_n` pad instance is renamed active-high `reset`, without inserting an inverter. Each die's odd remaining pad is disabled. Remaining paired pads serve six A and two B synthetic chains; other test lanes form synthetic rings. All real pins are excluded from synthetic traffic.

The sequencer's source clock is `producer_phase_clk = clk && prod_en`; the external gate is not included in the published phase-control macro. It remains unconnected in this partial assembly, rather than being tied to raw clock. Unbound logic clock/reset-family pins are also excluded from test traffic. Quantizer resets have local source logic and cannot be assigned by pin name. Phase control samples its enable state at the falling edge; its qualified reset contract requires a falling clock edge before use.

W12 contains 176 `taalas_dql_value` instances. Placing one reusable quantizer leaf supplies one instance, not all 176 or the full producer partition. The position-control macro still has external immutable-payload address/data ports; it does not complete the positions service. Raw W13 array WL/PC/OUT pins still require pending decoder, drivers, latches and output escape. Source correspondence and macro placement do not establish a complete recognizer, die link, full-chip LVS or STA. Macro timing qualifications assume nearby buffered receivers; the new top routes need separate electrical and timing validation.

The batch-2 lead authorization permits main and antenna DRC on the existing pod with at most three CPUs and a three-hour bound per die. This supersedes the earlier scaffold's local-only execution note for those checks; individual receipts report actual execution.
