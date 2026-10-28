# Encoder bank0/bank1 liveness analysis (W1 v3 Step 1)

**Conclusion: both 80 KiB FP32 banks are simultaneously future-live in the current F64 schedule. They cannot be aliased or one removed.** Their role is source/residual preservation alongside a transformed full-tensor workspace, with a predecessor-output-to-source copy between layers. They are not identical copies and not merely retry backups. This is an RTL enable/schedule proof corroborated by the existing v2 F64 checks, not a newly instrumented cycle-count measurement.

## Reading and scope

Read the repository `skills/taalas-fixed-weight-routing/SKILL.md`; complete `references/source-notes.md` (824 lines); `references/patent-atlas.md`; `references/architecture-and-numerics.md`; primary US20250123802A1 summary, relevant detailed description of mutable operands versus fixed matrix connectivity and claims 1–20 from `experiments/common-v9-start-handoff-source-20261004-v1/reading-basis-v2/US20250123802A1.txt`. Root `plan.md` is absent. No patent density or whole-chip feasibility claim is inferred here. Writable activations remain writable state.

All design files below occur in `onchip-all/commands-v2.json`; the original compiled sources and v2 host were read only. No RTL, host or v2 artifact was changed and no simulation was launched by this analysis worker.

## Exact compiled schedule and addressing

The physical module is `experiments/chip-integration-20261011-encoder-memory-integration-v2/rv_encoder_bank_consumer_edge_v1.sv`:

- Lines 28–31: `WORDS=FRAMES*40`, `bank0[WORDS]` and `bank1[WORDS]`, each 256 bits per entry. Region 0 and 1 select distinct arrays (lines 34–35).
- Lines 65–76: accepted writes commit at the original due edge; region selects the bank. One request is outstanding, so this is **simultaneously live data**, not two same-cycle physical accesses.
- Router `experiments/chip-integration-20261012-encoder-bank-reply-ownership-source-v1/rv_encoder_memory_router_v6.sv:140` passes `FRAMES` through to the bank.

The layer owner is `experiments/chip-integration-20261012-routevoice-remaining-widths-v1/rv_frames_taalas_encoder_residual_query_code_alias_layers_q8.sv` (abbreviated **layer owner** below). Its physical mapping is explicit at lines 99–105: endpoint region 0 maps to physical bank0; prefix regions 0/3 and FF regions 0/3 map to physical bank1; shared codes map to bank2. The bank1 reuse already performed is safe **within** bank1's non-overlapping logical epochs:

| Stage | bank0 | bank1 | Why bank0 is still needed |
| --- | --- | --- | --- |
| Fresh load | X | prior-layer final, until reload completes | X feeds prefix and later residual Add |
| Prefix normalization and global DQL | X | norm(X), then context workspace | X must survive for O residual |
| O projection/residual | X overwritten in place by S=RN(X+O) | dead context workspace after quantization | S needed by FF norm and final residual Add |
| FF normalization and global DQL | S | norm(S) | S needed by down-projection final Add |
| FF replay/down | unread S residual words | newly produced final Y | Y becomes next-layer source; S words are read for final Add |
| Next-layer fresh load | new X copied from bank1 | previous Y | bank1 overwritten only after full reload ACK barrier |
| After layer 5 | finalnorm output in bank0 | last layer Y | Y is finalnorm source; bank0 then stays leased for producer transfer |

This is more precise than calling it symmetric ping-pong. Array identities do not alternate each layer. Bank0 is X/S, bank1 is the norm/context/FFnorm/final workspace; the six-layer owner pays a bank1→bank0 reload.

## Full-bank simultaneous-liveness witness

There are two independent full-bank witnesses per encoder layer. The FF one is especially direct:

1. The O endpoint completes all `40F` residual writes to bank0 before FF starts. Layer owner `ORUN`, `OACCEPT`, `PRELEASE`, `FSTART` transitions require `rseal`, `ers==RV_WORDS`, retirement of the context codes and retained endpoint ownership (lines 162–175).
2. `rv_frames_taalas_encoder_feed_forward_presummed.sv:40–49` starts `rv_frames_taalas_encoder_norm_sealed_q32` with true residual bypass; it feeds S as the source. Its local norm region 0 is routed to physical bank1 by the layer owner, while its region 8 source requests use the retained endpoint bank0.
3. `rv_frames_taalas_encoder_norm_sealed_q32.sv:48–64` streams the normalized FP32 result into `taalas_dql_sealed_source_q32` and withholds `producer_idle` until all rows finish. Its `WAIT_ROW`/`QUANT_WAIT` checks (lines 100–111) require `40F` completed source writes.
4. `rtl/taalas_dql_sealed_source_q32.sv:135–139` enters `SEAL` only after the last normalized-source write ACK. Lines 163–167 then enter `SCAN_SETUP` only when drained, before issuing the first extrema-scan read. The later scan and quantization each read all `40F` bank1 packets (lines 141–153, 173 onward).
5. At this boundary, **every bank1 word still has future scan/quantization reads**. **Every bank0 S word still has a future residual read**: FF replay has not started, and `rv_frames_taalas_encoder_ff_presummed_down_q8.sv:122–141,259–273` reads region 5 (`FEATURE_REQ` → bank0 through the parent) and computes exact RN(S+down) for every final packet.

Thus this is not an argument based on “initialized” words, full allocation, or stale post-use payload. At the witnessed boundary all entries in **both** arrays have concrete future readers before their next overwrite. Prefix global normalization supplies a second witness: complete norm(X) in bank1 must be scanned/replayed while complete X in bank0 still awaits O residual addition.

### Storage bound

For the current schedule without recomputation, the pair needs `2*40F` 256-bit words = `640F` FP32 scalars = **2560F bytes**.

| Static F | Each bank | Pair minimum/current allocation |
| ---: | ---: | ---: |
| 64, qualified full top | 2,560 packets / 81,920 B | 5,120 packets / 163,840 B = 160 KiB |
| 500, historical encoder default | 20,000 packets / 640,000 B | 40,000 packets / 1,280,000 B |
| 508, module bound | 20,320 packets / 650,240 B | 40,640 packets / 1,300,480 B |

The static encoder/bank geometry permits F=4..508 in multiples of 4; the all-onchip v2 full top is F64, not a claim of qualified full-top variable geometry. Some upper encoder modules default to 500, while the physical bank defaults to 64; actual specialization controls allocation. Bank2 codes (320F bytes), pipeline packets, arithmetic registers and other arrays are additional and not included in the pair count.

No exact count of cycles with both banks live was measured. The full `80F`-packet peak is a proved schedule checkpoint. The lower bound is for the present no-recompute schedule/interface, not an information-theoretic proof over all possible model algorithms. Multi-pass norm recomputation or redesigned global-domain accumulation could change the schedule, numerical obligations, traffic, energy, and fault semantics; none is implemented or qualified here.

## Existing F64 simulation evidence

`onchip-all/host-v2/encoder_services.hpp` independently checks every accepted mutable read and write against frozen/reference numeric tensors, including all lanes (lines 161–180). `check_layer()` (lines 121–130) requires, for each of six layers:

- bank1 normalized logical images 0 and 11: `40F` write ACKs and `80F` reads each (one complete extrema scan and one quantization replay);
- bank0 X image19: `40F` writes and `80F` reads (prefix plus residual O);
- bank0 S image22: `40F` writes and `80F` reads (FF norm plus down residual);
- all final bank1 values match gold image14; S in bank0 still matches gold image22;
- actual complete reload and predecessor identities before bank1 overwrite, plus code-retirement barriers (lines 165–177).

Saved v2 log `logs-v2/20261014T031357-positive.log` lines 82,85,88,91,94,96 shows all six `LAYER_ACCEPT` events. These print only after `check_layer()` returns. Their common clocks are 248832320,258012141,266942167,275879422,285054621,294183520. Line132 reports:

```
ONBOARD_MEMORY_CONSERVED mutable_requests=348160 mutable_replies=348160 mutable_response_packets=348160 mutable_response_checks=2785280 alias_requests=2560 alias_replies=2560 alias_serialized_values=20480 bank_idle=1 bank_fault=0 router_fault=0
```

The log's per-layer `mutable=379200` is the historical `child_requests` label and includes immutable transactions; it must not be reported as bank-only accesses. Actual bank-only total is 348160.

Fixture provenance for independent distinct-value evidence: `encoder/inputs.txt` contains six layer groups, each with weights; images 7,15,16,17,18,21,20; images19,8,9,10,14; eight domains; four hashes. The host derives norm(X)=image0 and norm(S)=image11 using the pinned `block` dylib and verifies hashes. `encoder/residuals.txt` holds the separate pinned `sum_row` library then six S bins. The host explicitly verifies S=RN(X+O), preserving rounding. This avoids confusing observed normalized values with a guessed floating reference.

## Reset, stalls, overlap and publication

Removing a bank breaks positive inference before a retry is involved: writing norm(X) over X destroys the later O skip source; writing norm(S) over S destroys the final FF residual source. It also breaks the independently checked source/read payloads.

The bank is not a recovery checkpoint engine. Warm reset fences new requests and response acceptance but accepted writes still commit at their due edge; held replies remain until the parent drains them. POR resets metadata/control, not payload (bank lines1–11,48–52,65–79). No rollback/copy restoration occurs. A bank alias must not turn a pending write to one logical region into corruption of another retained region, even while reset is asserted. Backpressure extends these lifetimes; it does not make their overlap disappear.

The six-layer owner (`rv_frames_taalas_encoder_query_six_layers_f500.sv:89–102,127–158`) serializes layer release, predecessor reload, finalnorm and final publication. All-layer final bank0 is retained for the tagged producer transfer; the owner admits no new job until matching release and quiet services. There is already a **read-only transfer alias** to bank0 (client3/owner2/region0) in the bank's legality predicate. That alias is not bank0/bank1 equivalence.

## Relevant existing negative/fault tests (identified, not re-run)

- Exact consumer-edge bank protocol source: `experiments/chip-integration-20261011-encoder-memory-integration-v2/consumer_edge_protocol.cpp`, via FRAMES4 probe. It exercises terminal words, full held reply payload, accepted due write across warm reset then metadata POR/readback, lease-gated real transfer, backpressure, wrong/matching release. Historical evidence `experiments/chip-integration-20261011-encoder-memory-control-v1/edge-protocol/native.txt`: `CONSUMER_EDGE_PROTOCOL_PASS checks=12783 clocks=4062 actual_alias_packets=160 neural_engines=0 physical_credit=0`; result.json exit0. This is a small protocol proof, not a v3 numerical pass.
- Same source directory `router_protocol.cpp` exercises backend selection/ownership and response routing. Current compiled router is the later ownership-hardened v6; do not call its older control result complete current-router coverage.
- `experiments/runtime-encoder-native-reset-admission-source-20261012-v1/encoder_runtime_numerical.cpp`: modes `early`, `old-layer`, `wrong-image`, `reset-admission`. `early` injects wrong source tag/word, memory/head/O reply identities and two pending-write resets; `old-layer` checks predecessor bank1 survives partial next-layer bank0 overwrite and rejects stale ACK without dropping the genuine request. This uses a distinct runtime encoder harness; source tests explicitly distinguish preparation from execution.
- `experiments/runtime-encoder-six-layer-real-source-20261012-v3/runtime_six_layer_real_trace.cpp` has wrong source/reply and first accepted fresh-write reset tests. Its source-tests.json is source-only and supplies no new execution credit.

Recommendation: stop the encoder reduction at Step 1. Bank0/bank1 are both required by the current schedule; no v3 RTL change is justified by this analysis.
