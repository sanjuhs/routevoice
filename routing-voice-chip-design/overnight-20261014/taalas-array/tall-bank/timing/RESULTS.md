# Actual tall-bank sampled timing

These are sampled transistor/RC results from real programmed joined array/readout layouts. They do not qualify a complete physical bank or ARRAY-PORT macro. Full-row time and energy are intentionally null in results.json.

| Rows | Corner | Protocol ns | Complete protocol | Worst settled ns after WL command | Partial net source energy pJ | Pattern |
|---:|---|---:|---|---:|---:|---|
| 320 | ss | 20 | FAIL {'output': 116, 'raw': 100, 'precharge': 0, 'phase': 0} | unqualified | 38.92331 | ranked near/far/activity, twice |
| 320 | ss | 40 | PASS | 8.9197 | 41.43861 | ranked near/far/activity, twice |
| 320 | ss | 60 | PASS | 8.8939 | 41.74036 | ranked near/far/activity, twice |
| 320 | typical | 20 | FAIL {'output': 14, 'raw': 8, 'precharge': 0, 'phase': 0} | unqualified | 50.19770 | ranked near/far/activity, twice |
| 320 | typical | 40 | PASS | 5.8165 | 51.34418 | ranked near/far/activity, twice |
| 320 | typical | 60 | PASS | 5.8216 | 51.37137 | ranked near/far/activity, twice |
| 1280 | ss | 60 | PASS | 22.5412 | 100.36585 | far1/far0, twice |
| 1280 | typical | 60 | PASS | 14.6765 | 126.93414 | far1/far0, twice |

Energy is the net sum of receiver supply, selected WL buffers/input sources, PC buffer/input source and ideal aggressor sources over the second repeated sequence. The separate source components remain in results.json. It covers 16 full-height active bit columns plus 128 physical receiver channels, not 1,280 columns or a full row. Omitted column-array currents, full supply return, decoder/controller/latch/mux and global broadcast energy are unmeasured. A negative aggressor contribution is signed source energy in this finite window, not an assertion of recovered production energy.

## Reuse and capture

320-row: minimum common TT/SS passing interval among tested protocol profiles = 40.0 ns; conditional sampled-slice interleave count at 20 ns initiation = 2. This is not the globally optimized minimum and does not qualify whole-bank throughput. Reduced optional 1280 sampling is identified in the table.
1280-row: minimum common TT/SS passing interval among tested protocol profiles = 60.0 ns; conditional sampled-slice interleave count at 20 ns initiation = 3. This is not the globally optimized minimum and does not qualify whole-bank throughput. Reduced optional 1280 sampling is identified in the table.

Four striped 320-row banks map logical row = bank + 4 × local row. They revisit a bank every 80 ns at hypothetical 20 ns initiation. W2b currently requests rows every three engine cycles (60 ns at a 20 ns clock), hence 240 ns between striped-bank reuses, but its INDEX capture aperture is still approximately one cycle. The projection has 1,280 row reads and 4,160 integer cycles, not 4,160 row reads. Read-command threshold latency alone is never used as reuse period. The stored +20 ns-after-WL data probes exclude phase launch, address decode, output mux, latch and setup time.

## Geometry, identity and candidate selection

The selected 320 bank3 G02 source is taken from the actual striped full assembly. All 41,472 extracted devices match the independent real-image reference, including every programmed access connection and 2.88 µm precharge receiver. The 1280 G07 case independently matches 164,352 devices and identity row mapping. These are graph checks; parent artifacts separately hold DRC/LVS/readback evidence.

Bank 3 has all 1,280 bitline capacitances extracted. Candidate ranking uses actual incident metal C × (join geometry R + half array R); it selects global IDX95_2/local126 in G02, 239.54883 fF in full-bank extraction. The isolated joined subbank yields 239.54782 fF. This is an RC screening heuristic, not a proof of worst transistor timing over all corners; the other three banks are not cap-extracted. Earlier G03 cases and population-based pilots remain separate. The optional 1280 G07 local peak 119 has 732.56619 fF and 714 connected drains; only its 128 local columns were ranked by extracted C.

## Model and limits

The harness reuses the pre2std4 circuit: 2.88 µm precharge PMOS, extracted stock buf4 WL and buf20 PC drivers, actual device geometry and Magic capacitances,32-section bitline/ground model, geometry resistance at 0.104 ohm/square with 0.00333/K temperature coefficient, and explicit join via resistance. TT is 3.3 V/25 °C and SS is 2.97 V/125 °C. Output load is assumed 10 fF. Capacitance is redistributed using actual joined and array extraction; this is not automatic distributed resistance extraction. The measured array-to-joined negative per-pair capacitance delta is recorded rather than silently added.

The primary harness has 128 selected-row access gate loads and 128 PC receiver loads. It does not include the full320-lane common WL/PC rail loading. Other 112 bitlines are ideal legal-state aggressors that also drive their physical receiver channels. Only one 2 µm ground strap is modeled with ideal endpoints; real VSS return and simultaneous all-column current are not qualified. Drivers and phase stimuli are simulation components, not physically placed implementation.

## Numerical failures and replay

Earlier 20/40 ns simulations aborted at the precharge-return breakpoint. Their incomplete traces, decks and logs remain under failed-* case directories and carry no electrical protocol or energy credit. A PULSE source with rounded fractional width created nearly coincident breakpoints with PWL aggressors; final profiles use explicit PWL PC times with unchanged intended phases. Isolated power observers were replaced by post-transient vector calculations. Gear2 and earlier trapezoidal source decks are retained. A completed protocol FAIL is distinct from these numerical failures.

Closed Magic extraction .ext files were losslessly gzip-compressed after extraction, reclaiming256.34MiB. closed-ext-compression.json records original byte counts, SHA256 decompression checks and exact restoration commands. Live SPICE/cap inputs remain available.

See results.json for authoritative paths/hashes and all check counts, COMMANDS.md for exact invocation patterns, and each case source/deck/command/build/log/trace artifact for exact reproduction.

## Additional 1280-row coverage

r1280-v1/ss-60ns-s32/result.json: ss full near/far/activity pattern, 60.0 ns, protocol pass=True, maximum sampled settling=24.350631 ns; +20 ns data-probe failures=22. This additional SS evidence has broader coverage than the matched compact TT/SS comparison above and must not be ignored when assessing the worst observed delay.

## Supplemental control-load sensitivity

r320-global-load-v1/ss-40ns-s32/result.json: ss at40.0ns, protocol pass=True, checks={'output': 0, 'raw': 0, 'precharge': 0, 'phase': 0}, sampled settling=9.075878666666663ns.

This sensitivity uses measured fullbank WL/PC incident capacitance, 10 distributed but unplaced stock drivers per control, 4.2 mm geometric control-rail resistance, and dummy loads for the other nine subbanks. All 10 PC and local WL phase terminals are checked, but only 16 actual data columns. Dummy transistor source/drain bias and grounded extra capacitance omit real Miller/coupling/current behavior. It is not a placed-driver or full-bank timing/energy qualification.
