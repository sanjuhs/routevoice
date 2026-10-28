# W1 all-service merge: PASS

`rv_allonchip_top_all_v1` integrates all six fixed-weight services with the retained recognizer top unchanged. **F64 positive passed in 3143.925 seconds (52 minutes 23.925 seconds), exactly 312,578,649 common clocks**, matching baseline. Five tokens `[28176, 373, 278, 26068, 2]` include EOS. All **18 output sizes and SHA256 hashes** match the frozen binding; renderer output is **Switch on the lights**.

All six ONCHIP lines report `host_replies=0 mismatches=0`. Their sum is **60,234,240 observed RTL replies**. There are **no fixed-weight response data inputs**: all 59 former service inputs are output-only debug ports. The generated Verilator header independently confirms their output direction. The 35 remaining inputs are PCM, control, configuration and reset signals.

| Service | Native ROM bytes | Observed RTL replies | Host replies | Mismatches |
|---|---:|---:|---:|---:|
| decoder_body | 8,908,800 | 1,392,000 | 0 | 0 |
| decoder_self | 2,519,040 | 787,200 | 0 | 0 |
| encoder_QKV_O | 2,457,600 | 384,000 | 0 | 0 |
| encoder_immutable | 5,146,880 | 1,947,520 | 0 | 0 |
| frontend_immutable | 8,298,240 | 55,720,960 | 0 | 0 |
| producer_positions | 1,310,720 | 2,560 | 0 | 0 |
| Total newly moved | 28,641,280 | 60,234,240 | 0 | 0 |

Encoder QKV/O combines 368,640 head replies and 15,360 O replies. Both individual original conservation counters remain checked. The 16 frontend chunk clocks, six encoder acceptance clocks and five decoder completion clocks all match the verified group (a) run: **27/27 milestones**, recorded in `progress-comparison.json`.

## ROM accounting and implementation

The 17 new ROM hex images were regenerated from the original frozen binaries and independently round-tripped. Each generated image also matches its worker image SHA256. `rom-manifest.json` records every consumed input and output hash. The seven responder modules are copied from W1, W1b and W1c, with only ROM paths relocated. `prepare_merge.py` records the reproducible merge; worker sources were read-only.

Already onboard tables account for another **9,143,040 native bytes**, counting tied embedding/head images once: **37,784,320 native bytes total**. The corresponding logical stored image total is **37,488,640 bytes**: existing source coefficients use 614,400 bytes of pointers plus 307,200 bytes of books instead of 1,228,800 resolved bytes; producer metadata is padded from 19,200 native bytes to 30,720 ROM bytes. See `rom-accounting.json` and its pinned authoritative ledger. These are logical payload sizes, not measured physical macro area.

The shared frontend/encoder bus is fully internal. Request selection and one-outstanding-transaction gating connect the two ROM services; held responses are multiplexed with gated acknowledgement. The host keeps the workers' independent binary payload, full identity, cycle schedule and conservation checks. It never drives a moved response bus. `port-audit.json`, `generated-port-audit.json` and `audit_merge.py` document that audit. The original top and worker source hashes were rechecked unchanged after F64.

## Validation evidence

All requested stages exited 0; no merged verification failure occurred. Exhaustive tests covered **2,804,360 valid ROM packets / 28,641,280 bytes** across all seven responders, including all 163,840 position words against the frozen binary. They also checked held responses, warm reset and representative invalid requests. The separate four-state position control test passed six pinned reads, 11 invalid offers and 18 held cycles. This is exhaustive valid-address payload coverage, not exhaustive combinations of faults and resets.

| Stage | Exit | Seconds | Evidence |
|---|---:|---:|---|
| lint-full | 0 | 36.46 | [log](logs/20261014T020603-lint-full.log) |
| generate-full | 0 | 79.56 | [log](logs/20261014T020706-generate-full.log) |
| compile | 0 | 96.06 | [log](logs/20261014T020905-compile.log) |
| fixture | 0 | 2.08 | [log](logs/20261014T021118-fixture.log) |
| unit-body-build | 0 | 2.24 | [log](logs/20261014T021132-unit-body-build.log) |
| unit-body-run | 0 | 1.00 | [log](logs/20261014T021134-unit-body-run.log) |
| unit-self-build | 0 | 2.17 | [log](logs/20261014T021135-unit-self-build.log) |
| unit-self-run | 0 | 0.57 | [log](logs/20261014T021137-unit-self-run.log) |
| test-head-build | 0 | 1.98 | [log](logs/20261014T021138-test-head-build.log) |
| test-head | 0 | 0.57 | [log](logs/20261014T021140-test-head.log) |
| test-O-build | 0 | 1.91 | [log](logs/20261014T021140-test-O-build.log) |
| test-O | 0 | 0.51 | [log](logs/20261014T021142-test-O.log) |
| test-memory-build | 0 | 1.97 | [log](logs/20261014T021143-test-memory-build.log) |
| test-memory | 0 | 0.89 | [log](logs/20261014T021145-test-memory.log) |
| unit-front-build | 0 | 1.60 | [log](logs/20261014T021146-unit-front-build.log) |
| unit-front | 0 | 1.32 | [log](logs/20261014T021147-unit-front.log) |
| unit-position-build | 0 | 0.08 | [log](logs/20261014T021149-unit-position-build.log) |
| unit-position | 0 | 0.08 | [log](logs/20261014T021149-unit-position.log) |
| unit-position-exhaustive-build | 0 | 2.02 | [log](logs/20261014T021149-unit-position-exhaustive-build.log) |
| unit-position-exhaustive | 0 | 0.56 | [log](logs/20261014T021151-unit-position-exhaustive.log) |
| positive | 0 | 3143.93 | [log](logs/20261014T021221-positive.log) |
| compare | 0 | 0.04 | [log](logs/20261014T030513-compare.log) |
| render | 0 | 0.08 | [log](logs/20261014T030520-render.log) |

Lint emitted only TIMESCALEMOD warnings, retained in the log. Fixture evidence is `COMMON_NUMERIC_FIXTURE_PASS frames=64 values=20480 native_final_flags=1 clocks=0`. `comparison-result.json` records all 18 actual output hashes. `result.json` records service counts, stage durations and log hashes. `worker-evidence.json` separately confirms all three worker positives exited 0 and independently rechecks their 18 hashes.

## Exact commands and rerun

Working directory: `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design`. Every full argv, including the full RTL list, is in `commands.json`. Each stage's adjacent log JSON records the exact niced invocation, working directory, PID, elapsed time and exit code. Reproduce with:

```sh
.venv/bin/python -B overnight-20261014/onchip-all/prepare_merge.py
.venv/bin/python -B overnight-20261014/onchip-all/audit_merge.py
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py lint-full
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py generate-full
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py compile
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py fixture
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-body-build
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-body-run
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-self-build
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-self-run
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py test-head-build
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py test-head
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py test-O-build
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py test-O
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py test-memory-build
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py test-memory
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-front-build
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-front
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-position-build
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-position
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-position-exhaustive-build
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py unit-position-exhaustive
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py positive
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py compare
.venv/bin/python -B overnight-20261014/onchip-all/run_stage.py render
.venv/bin/python -B overnight-20261014/onchip-all/audit_merge.py --verify-pins
```

Before a new positive run, archive the existing `actual` directory within the authorized runtime directory; the runner refuses to overwrite it. Runtime path: `~/.local/state/routevoice-internal-runs/20261014/onchip-all/`. The executable is `obj/Vrv_allonchip_top_all_v1`, pinned in `binary-pin.json`; sources/commands are pinned in `build-input-pins.json`, worker/original sources in `source-provenance.json`, and unit test sources in `unit-test-source-pins.json`.

Builds and simulation used `nice -n 10`, at most eight compile jobs, and local internal storage only. The runner checked disk before builds and monitored a 22 GiB reserve to protect the required 20 GiB floor. It was never triggered in the merged run. Final free disk was about 26 GiB. Concurrent worker positives were permitted by lead guidance; this run used its own lock.

After successful compilation and unit tests, **556,118,468 bytes** of this worker's generated C++/object/archive/dependency intermediates were reclaimed to preserve disk space. Exact deleted file sizes/hashes are in `reclaimed-build-intermediates.json`. Executable, headers, original source, ROMs, commands and logs remain. **Regenerate before rebuilding.** Other workers' source files and the retained design were not modified; no cloud computation was used and no git commit/push was made.

## Remaining scope

No requested merge qualification remains unfinished. This establishes functional ROM integration for the qualified F64 case and preserves its cycle schedule. Physical ROM mapping, complete-chip synthesis/area/power/timing, other utterances and the broader connected negative suite are separate qualifications. The original host's `connected_negative_suite_required=1` limitation remains visible in the final log.

## V2 boundary audit (14 October 2026)

Four of v1's 35 remaining inputs are frozen model constants. V2 removes them; its remaining 31 inputs contain no model constants. This refines the earlier general description of the configuration inputs. The v1 top, host and recorded build inputs remain unchanged.

| V1 input | Classification | V2 treatment | Evidence / role |
|---|---|---|---|
| `frontend_por_reset` | reset | retained | Reset/POR control; contains no trained values. |
| `table_por_reset` | reset | retained | Reset/POR control; contains no trained values. |
| `producer_por_reset` | reset | retained | Reset/POR control; contains no trained values. |
| `history_por_reset` | reset | retained | Reset/POR control; contains no trained values. |
| `up_start_valid` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `up_start_tag` | job metadata | retained | Frontend/encoder job tag. |
| `up_done_ready` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `up_pcm_producer_idle` | control-handshake | retained | Producer quiescence handshake. |
| `up_pcm_valid` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `up_pcm_tag` | job metadata | retained | Audio packet/job identity. |
| `up_pcm_index` | job metadata | retained | Sample ordering metadata within the audio packet. |
| `up_pcm_value` | audio data | retained | Signed PCM16 sample payload. |
| `row_transfer_enable` | control-handshake | retained | Enables row transfer/transport. |
| `compact_setup_valid` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `compact_setup_session` | job metadata | retained | Per-job session; host increments session_counter, RTL latches setup_session separately from model ID. |
| `compact_setup_image_id` | model constant | internal localparam; removed from ports | Fixed model compatibility identity; RTL equality-checks MODEL_IMAGE_ID. It is not the separately latched session ID. |
| `source_start_valid` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `source_start_tag` | job metadata | retained | Source session/job identity. |
| `source_start_position_scale` | model constant | internal localparam; removed from ports | Frozen position quantization FP32 bits: 1012345286 / 0x3c5729c6; contract and metadata agree. |
| `source_start_position_zero` | model constant | internal localparam; removed from ports | Frozen position quantization zero point: 123 / 0x7b. |
| `source_start_position_offset` | model constant | internal localparam; removed from ports | Frozen qualified position offset: 0; SessionServices::start_source source-start assignment. |
| `source_error_ready` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `clk` | control-handshake | retained | Clock timing input; grouped with control. |
| `reset` | reset | retained | Reset/POR control; contains no trained values. |
| `step_enable` | control-handshake | retained | Clock/step progression control. |
| `learned_por_reset` | reset | retained | Reset/POR control; contains no trained values. |
| `begin_valid` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `begin_job_tag` | job metadata | retained | Job identity. |
| `begin_session` | job metadata | retained | Current compact session identity. |
| `begin_source_tag` | job metadata | retained | Published source identity. |
| `begin_token_tag_base` | job metadata | retained | Token sequence tag namespace. |
| `begin_frames` | job metadata | retained | Job frame count; qualified fixture is F64. This describes input extent, not trained model data. |
| `token_ready` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `job_done_ready` | control-handshake | retained | Valid/ready admission, acknowledgement or backpressure control. |
| `bank_por_reset` | reset | retained | Reset/POR control; contains no trained values. |

`compact_setup_image_id` is tied to `256'h85352d965e0eba2fa31e2162b31adaead328f60524e03fa6978b18584b35355f`. Evidence: `producer_services.hpp:197` supplies the same eight little-endian uint32 words; compiled `rtl/taalas_compact_history_token_barrier_q1.sv:180` rejects unequal model IDs, while line 181 separately latches the variable `setup_session`. Position scale/zero are bound by `producer/real-domain-contract.json`, `producer/metadata.txt`, and `SessionServices::load_fixture`; offset 0 is set in `SessionServices::start_source`. See `input-audit-v2.json` for source SHA256 pins, and `RESULTS-v2.md` for v2 verification.

V2 qualification completed 2026-10-14 04:09:10 IST: all four model inputs internalized; 31 runtime inputs, zero model-constant inputs. Lint/generate/compile/fixture/positive/compare/render passed. F64 retained 312,578,649 clocks, all 18 hashes, five tokens through EOS and “Switch on the lights”. All 63 non-progress log lines match v1. Full evidence: [RESULTS-v2.md](RESULTS-v2.md).
