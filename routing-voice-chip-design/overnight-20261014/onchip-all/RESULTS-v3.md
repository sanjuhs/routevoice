# W1 v3 — A/B bank lifetime analysis

**STOP after Step 1: neither pair can lose a bank under the current schedule. Safe deletion saving: 0 B.** Both encoder banks hold different, future-live tensors simultaneously; both producer banks hold different, future-live cross-attention K/V tensors simultaneously. These are functional dependencies in successful inference, not spare recovery copies.

Analysis completed 14 October 2026, 04:18:15 IST, within the 60-minute analysis limit and before the 07:15 deadline. **No `rv_allonchip_top_all_v3` was created.** The verified v2 RTL, host, binaries, outputs and reports remain unchanged. The conditional implementation/full-F64 step was not entered, as instructed when both copies are needed.

## Storage result

Here “live” means a stored value has a future reader before its next overwrite. Initialized or retained dead payload does not count. “Word” below means a **256-bit packet**, not one FP32 scalar.

| Pair | Full simultaneous-live witness | Peak live words at F64 | Minimum payload for this schedule | Safe bank deletion |
| --- | --- | ---: | ---: | ---: |
| Encoder bank0 / bank1 | Full residual source S and full norm(S), before global quantizer scan; also X and norm(X) earlier | 5,120 | 163,840 B = 160 KiB | 0 B |
| Producer bankA / bankB | Complete K and complete V at generation DONE/RETAIN, before the first consumer read | 5,120 | 163,840 B = 160 KiB | 0 B |

For either pair, each bank has `40F` packets = `320F` FP32 values = `1280F` bytes. The pair needs **`80F` packets = `2560F` bytes** for the present materialized-tensor schedule without recomputation. F64 therefore needs two 80 KiB banks per pair. The two pairs' allocated payload totals 320 KiB; their individual peak witnesses do **not** establish that both pairs peak on the same cycle.

| Static frame count F | One bank | One pair |
| ---: | ---: | ---: |
| 64 | 81,920 B | 163,840 B |
| 500 | 640,000 B | 1,280,000 B |
| 508 | 650,240 B | 1,300,480 B |

The encoder bank and enclosing static encoder explicitly admit F=4..508, multiples of four. The producer's capacity formula is also `FRAMES*40`; its storage module does not itself impose a separate full-system geometry guard. These formulas do not qualify a variable-frame full recognizer: the retained all-onchip v2 run is **F64**. Code banks add `320F` bytes each; packet registers and other state are additional, unchanged allocations.

This is a lower bound for retaining the independently addressed tensors under the **existing schedule and interfaces**, not an information-theoretic lower bound for every possible algorithm. Compression, recomputation, a redesigned production/consumption order, or cross-stage backing reuse would require separate implementation and qualification. No savings from those alternatives are credited here.

## Encoder: source and workspace are both needed

The exact compiled physical bank is [rv_encoder_bank_consumer_edge_v1.sv](../../experiments/chip-integration-20261011-encoder-memory-integration-v2/rv_encoder_bank_consumer_edge_v1.sv), lines 28–35 and 65–76. Regions 0/1 address different arrays. The single outstanding request serializes physical accesses; it does **not** serialize the lifetimes of their contents.

The [layer owner](../../experiments/chip-integration-20261012-routevoice-remaining-widths-v1/rv_frames_taalas_encoder_residual_query_code_alias_layers_q8.sv), lines 99–105, maps source/residual storage to bank0 and normalization/context/final workspace to bank1. This is not symmetric layer-by-layer ping-pong: bank0 remains the X/S source, and the next layer reloads predecessor output from bank1 into bank0.

| Phase | bank0 | bank1 |
| --- | --- | --- |
| Prefix normalization/global DQL | X, still needed for the attention residual | norm(X), awaiting complete extrema scan and quantization replay |
| Attention residual | X replaced in place by S=RN(X+O) | Context workspace, retired before later reuse |
| FF normalization/global DQL | S, still needed by final residual addition | norm(S), awaiting complete extrema scan and quantization replay |
| FF down/output | Remaining S residual source | Final layer output Y |
| Next layer/final norm | Reloaded next-layer X, or final normalized encoded result | Prior layer Y until its complete source read/reload |

The decisive full-bank checkpoint is immediately before the first FF norm quantizer scan:

1. All `40F` residual S writes to bank0 have completed before FF starts.
2. [rv_frames_taalas_encoder_norm_sealed_q32.sv](../../experiments/chip-integration-20261012-routevoice-remaining-widths-v1/rv_frames_taalas_encoder_norm_sealed_q32.sv), lines 48–64 and 100–111, writes every normalized FP32 packet to bank1 and withholds producer-idle until the final row finishes.
3. [taalas_dql_sealed_source_q32.sv](../../rtl/taalas_dql_sealed_source_q32.sv), lines 135–139 and 163–173, waits for the last source-write ACK and drain before `SEAL → SCAN_SETUP`. Both complete bank1 scans are still ahead.
4. FF replay has not started. [rv_frames_taalas_encoder_ff_presummed_down_q8.sv](../../experiments/common-v9-ffdown-and-generic-comparison-width-source-20261011-v1/rv_frames_taalas_encoder_ff_presummed_down_q8.sv), lines 122–141 and 259–273, will later read every S packet for the final residual addition. Thus every bank0 word remains live too.

Aliasing bank1 with bank0 replaces S with norm(S), changing the residual operand. For layer 0, scalar 0 would change from **`0x3f7744ce` to `0x3f79ad67`**. The independent evidence audit reconstructed both normalization stages using the pinned native row library and matched all frozen hashes. **All 2,560 packets differ in each of the six layers**, for both X/norm(X) and S/norm(S); S/norm(S) differ in all 20,480 scalar positions per layer.

The existing [v2 encoder observer](host-v2/encoder_services.hpp), `check_layer()` at lines 121–130, requires each normalized image's `40F` writes/ACKs and `80F` reads, both residual-source passes, retirement barriers, exact final output, and preserved S. It checks actual RTL response payloads against accepted-write mirrors. All six layer acceptances passed in the retained F64 run. See [encoder-bank-analysis.md](encoder-bank-analysis.md) for the detailed source chain, ownership and historical fault-test references.

## Producer: encoded→K and adapter→V reuse already exists

The exact compiled [rv_producer_mutable_storage_v1.sv](../../experiments/chip-integration-20261012-producer-mutable-storage-source-v4/rv_producer_mutable_storage_v1.sv), lines 31–33 and 77–86, allocates bankA/bankB and routes physical regions 0/1 independently.

The [cross-session owner](../../experiments/chip-integration-20261012-routevoice-remaining-widths-v1/rv_frames_taalas_adapter_cross_session_f500.sv) already reuses both arrays after source retirement:

| Phase | bankA, region 0 | bankB, region 1 | Relevant control |
| --- | --- | --- | --- |
| FILL / adapter setup | Fresh encoded input | Position-adapted source | Full fresh write/ACK barrier; setup uses both regions |
| RETIRE / CODES_READY | Old source payload becomes dead | Old adapter payload becomes dead | Lines 190–191 wait for both source locks to retire; `alias_transferred` permits destructive reuse |
| KRUN | Complete K being produced | Dead prior payload | Role 0 writes map to region 0 |
| VRUN | **Complete K retained for future consumption** | V being produced | Role 1 writes map to region 1; no K consumer can run yet |
| DONE / RETAIN | **Complete K** | **Complete V** | Both ACK totals must equal `40F`; consumer enabled only in RETAIN |
| Generation release | Reusable K backing | Reusable V backing | Matching release and physical quiet before next generation |

The decisive enables are lines 110–114 (`choose_consumer=state==RETAIN`, region mapping), 130–138 (result/consumer/release gating), and 193–203 (`KRUN → VSTART → VRUN → DONE → RETAIN`). K must finish before V begins. The state machine requires **all K and V writes before publication**, so all `80F` packets are future-live at the boundary.

The [compact-token parent](../../experiments/chip-integration-20261012-routevoice-remaining-widths-v1/rv_frames_taalas_adapter_session_compact_token_release_v1.sv), lines 770–780, selects K then V for each head and forms the frame-major physical address. Lines 878–899 require all `640F` scalar transfers / `80F` packets before release. The existing [producer observer](host-v2/taalas_adapter_session_compact_token_services_f500_v1.hpp), lines 137–148, checks both write-ACK totals before generation publication and saves actual observed K/V banks for token 0. It validates every consumed scalar against the frozen oracle for all five tokens.

If A/B share addresses, V writes destroy K **before any K consumer read is permitted**. Actual saved layer-0 physical scalar 0 would change from K **`0x3fc184c0`** to V **`0xbe6fabb5`**. Every one of the 20,480 values and 2,560 packets differs for each saved layer. This counterexample uses actual v2 RTL output dumps, converted from their head-major file layout to physical frame-major bank order.

## Reset, backpressure and overlap consequences

The reduction fails in ordinary successful inference; it does not depend on retry behavior.

- **Encoder:** warm reset fences new requests/ACKs, while accepted writes still commit at their due edge and their captured replies remain held. POR resets control, not SRAM payload. No rollback copy is restored. Backpressure extends the source/workspace overlap. Next-layer reload and the final producer-transfer lease must remain protected.
- **Producer:** storage writes commit on request acceptance. Its two-cycle countdown advances through warm reset, while warm reset fences acceptance/ACK; the held response persists. POR clears queue/control without clearing payload. The cross-session owner explicitly invalidates a session on common reset/fault and drains it, without RAM rollback. Source ownership was retired before K/V overwrite; a new source session requires a fresh load.
- **Both:** one physical request port does not make two live logical tensors aliases. Stalling cannot resolve this dependency. For example, holding off V to protect K deadlocks the current producer contract because K cannot be consumed until V is complete. Changing that contract would be a new schedule, with new numerical, ownership and fault obligations.

## Evidence, commands and validation scope

New read-only analysis command, from the repo root:

```sh
df -h /
nice -n 10 .venv/bin/python -B overnight-20261014/onchip-all/analyze_banks_v3.py > overnight-20261014/onchip-all/bank-analysis-v3.log 2>&1
```

**Exit 0.** [bank-analysis-v3.log](bank-analysis-v3.log) records all counterexamples and the audit result. [bank-analysis-v3-evidence.json](bank-analysis-v3-evidence.json) contains numerical witnesses, sizes and retained-run metadata; [bank-analysis-v3-input-pins.json](bank-analysis-v3-input-pins.json) records input SHA256/byte counts. The audit verified:

- All **166 v2 direct compiler inputs** still match their frozen SHA256 pins.
- All **18 actual v2 output files** still match the authoritative expected hashes.
- All six encoder layer acceptances; **30 producer generations and 30 releases**.
- **614,400 K + 614,400 V scalar checks**, **153,600 K/V writes** in the existing run.
- Producer bank totals: 363,840 requests/replies, 199,680 initialized reads and 159,360 initialized write ACKs. Encoder bank totals: 348,160 requests/replies, plus 2,560 transfer-alias reads.
- Original five token IDs `[28176, 373, 278, 26068, 2]` and saved render **“Switch on the lights”**.

The existing run is [20261014T031357-positive.log](logs-v2/20261014T031357-positive.log); its [command/exit/timing record](logs-v2/20261014T031357-positive.json) records **3159.3976 seconds** and **312,578,649 common clocks**. [Compare](logs-v2/20261014T040651-compare.log) and [render](logs-v2/20261014T040706-render.log) are retained evidence, not new runs. Full v2 commands remain in [commands-v2.json](commands-v2.json).

**No new F64 simulation, lint, generation, compilation or negative suite was run.** The permitted RTL-enable analysis plus existing F64 evidence establishes the overlapping live ranges, so Step 2 was stopped. Exact cycles with both banks live were **not measured**; the `5,120`-word peak is an analytical checkpoint forced by the exercised state machine. There is no v3 clock delta to report because there is no v3 implementation.

Relevant existing tests were identified for any future redesign: encoder `consumer_edge_protocol.cpp` (due write, warm reset, POR readback, held replies and transfer lease), producer `producer_storage_fourstate_tb.sv` (nine malformed/unknown-control cases and warm-held replies), `producer_provider_comparison.cpp` (original-provider comparison/held responses), and `producer_route_tb.sv` (route ownership). Producer tests and proposed commands reside in `experiments/chip-integration-20261012-producer-mutable-storage-source-v4/`. None is claimed as newly passing v3 coverage.

Disk free at the analysis audit was **23.95 GiB**, above the 22 GiB floor. No objects or binaries were generated; only analysis script/log/JSON/Markdown files were added in `onchip-all/`. Original source and frozen model images were read only. No cloud, commit or push.

## Decision for the floorplan lead

Do **not** subtract the proposed two 80 KiB banks from the current inventory. The requested ≈161 KiB reduction is not available by deleting these copies. The existing allocation still needs the denser-memory option (or a separately proved architectural/storage change) under the floorplan's stated assumptions. This analysis neither demonstrates one-die fit nor rules out other one-die designs.

Reading basis: repository Taalas skill, complete supplied source notes, patent atlas, architecture/numerics reference and relevant primary US20250123802A1 description/claims; current storage inventory and final-design-point floorplan. Root `plan.md` is absent. Patent fixed-weight connectivity does not eliminate these input-dependent activation tensors.
