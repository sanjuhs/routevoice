# W6 independent verification

Actual complete 64-row and 1,280-row array + 1,280 pre2 receiver GDS extraction versus independent original K64 packed-tensor reference. No partition-only credit.

| Rows | Selections | GDS readback | Exact graph/W/L | Full Netgen | Width negative |
|---:|---:|---|---|---|---|
| 64 | 20,480 | 81,920 bits, 0 mismatches | PASS | PASS | PASS |
| 1280 | 409,600 | 1,638,400 bits, 0 mismatches | PASS | PASS | PASS |

The independent reference is decoded directly from the original K64 packed
tensor. Source identity also checks all 409,600 selections against W5 indices
and W2b frozen RTL. Each Netgen pass requires unique matching and no property
errors. Full 1,280-row Netgen prints 1,643,520 raw devices and 827,201 after its
reported parallel/series merging under the standard GF180 setup; independent
raw exact graph/W/L equality checks every device before that reduction.
The negative reports precharge width 2.88 µm versus 5.76 µm (66.7% delta,
1% cutoff), explicitly rejected despite the topology unique-match phrase.
Only a checked bijective hierarchical-prefix removal is permitted; devices
and node topology are unchanged. Each saved-GDS readback audits actual Via1
programming sites and each group array instantiated exactly once.

The full 1,280-row LVS path is the original completed `r1280-v2/` extraction.
A separate connectivity-only attempt was cancelled with recorded SIGTERM
after the original full-C extraction succeeded. It receives no pass/fail
verification credit, and its native receipt and cancellation reason remain.
The full-C extraction returned 0 after 3,122.505 seconds. Its transparently
logged owned-watchdog extensions preserve native exit status; the final
guard observed at least 24.7397 GiB free. Positive and negative full-bank
Netgen runs finished in 438.701 and 454.969 seconds, respectively.
The native full-bank .ext is losslessly archived as
`r1280-v2/W6_PITCH_BANK_FLAT.ext.gz`; native and independently decompressed
SHA-256 match. See `native-ext-compression.json` for bytes, hashes, two
no-reader checks and restoration instructions. The archived source still
supports reproduction of the official capacitance export.
The four completed full-bank SPICE netlists are likewise archived as
`*.spice.gz`; `spice-evidence-compression.json` records individual native,
gzip and independently decompressed hashes and restoration instructions.
The 64-row native extraction and four SPICE files are also losslessly
archived; `r64-v2/slice-evidence-compression.json` records their independent
roundtrip hashes, no-reader checks, and restoration commands.
Failures and intermediate evidence remain in their original directories.
The earlier r64-v1 DRC failure is reported by the parent; its independent
readback passed but receives no clean-layout credit.

See [results.json](results.json), [README.md](README.md), and
[source-reading.json](source-reading.json) for exact scope, methods and inputs.
