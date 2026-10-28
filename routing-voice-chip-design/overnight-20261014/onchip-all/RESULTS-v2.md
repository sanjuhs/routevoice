# W1 all-onchip v2: PASS

Completed 2026-10-14 04:09:10 IST, before the requested approximately 05:30 IST deadline. **V2 F64 passed in 3159.398 seconds, with exactly 312,578,649 common clocks.** Five tokens `[28176, 373, 278, 26068, 2]` include EOS; all **18 native output sizes and SHA256 hashes** match the frozen binding and therefore the verified v1 output. Renderer returned **Switch on the lights**.

All **63 non-progress console lines are identical to v1**, including every conservation count and final PASS line. The 16 frontend, six encoder and five decoder milestone clocks also match exactly (27/27). Only `PROGRESS` lines, which include wall-clock timing, were excluded from the full console comparison. Evidence: `v1-v2-log-comparison.json`, `progress-comparison-v2.json`, `comparison-result-v2.json` and `result-v2.json`.

## Closed model-constant boundary

New file `rv_allonchip_top_all_v2.sv` removes four inputs and binds the original top through localparams:

| Removed model input | Exact frozen localparam value | Evidence |
|---|---|---|
| `source_start_position_scale` | `32'h3c5729c6` = 1012345286 | Original host `pscale`, `producer/metadata.txt`, and `producer/real-domain-contract.json` agree. |
| `source_start_position_zero` | `8'h7b` = 123 | Same independent host/contract/metadata binding. |
| `source_start_position_offset` | `12'h000` = 0 | `SessionServices::start_source` always drives 0 in the qualified host. |
| `compact_setup_image_id` | `256'h85352d965e0eba2fa31e2162b31adaead328f60524e03fa6978b18584b35355f` | Host's eight little-endian uint32 words exactly match compiled RTL `MODEL_IMAGE_ID`. |

The image ID identifies the frozen model, **not a per-job session**. `rtl/taalas_compact_history_token_barrier_q1.sv:180` rejects IDs unequal to `MODEL_IMAGE_ID`; line 181 separately latches variable `setup_session`. Its compiled parent `experiments/chip-integration-20261012-routevoice-remaining-widths-v1/taalas_compact_history_layer_self_o_q1.sv` passes the same fixed model ID parameter. Thus the model identity is internalized while `compact_setup_session` remains a job input.

V1 top, host, scripts, commands and all 165 pinned direct build inputs remain unchanged. The new host copies are under `host-v2/`, with all removed-port writes and initializers absent. They retain the existing numerical/conservation assertions and explicitly check the frozen position domain and model identity. All other copied headers are byte-identical. Preparation and final audit assert the precise allowed wrapper diff: module rename, four input removals, four localparams and four bindings; nothing else in wrapper RTL changes. Every responder and ROM image remains unchanged.

The numerical ROM accounting is unchanged: **28,641,280 newly on-chip service bytes**, **37,784,320 native bytes including already-onboard tables**. V2 additionally internalizes 308 bits of parameter/identity constants; these are localparams, not a claimed measured storage area. Physical implementation may optimize constant comparisons and wiring.

## Every remaining input classified

V1 had 35 remaining inputs; four were model constants. V2 has **31 runtime inputs: 1 audio data, 13 control-handshake (including clock), 7 reset, 10 job metadata, and zero model constants**. The same full classification is appended to `RESULTS.md`. Both source and generated Verilator header input lists are checked by `audit_v2.py`.

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

## Qualification evidence

| Stage | Exit | Seconds | Evidence |
|---|---:|---:|---|
| lint-full | 0 | 35.756 | [log](logs-v2/20261014T030932-lint-full.log) |
| generate-full | 0 | 76.342 | [log](logs-v2/20261014T031046-generate-full.log) |
| compile | 0 | 74.987 | [log](logs-v2/20261014T031209-compile.log) |
| fixture | 0 | 1.331 | [log](logs-v2/20261014T031330-fixture.log) |
| positive | 0 | 3159.398 | [log](logs-v2/20261014T031357-positive.log) |
| compare | 0 | 0.039 | [log](logs-v2/20261014T040651-compare.log) |
| render | 0 | 0.182 | [log](logs-v2/20261014T040706-render.log) |

The fixture reports `COMMON_NUMERIC_FIXTURE_PASS frames=64 values=20480 native_final_flags=1 clocks=0`. All seven requested validation stages exited 0. The corrected initial preparation assertion is documented in `FAILURES-v2.md`; it was not a numerical pass or a Verilator failure. Existing v1 exhaustive responder tests remain applicable because responder sources and all 17 ROM images are unchanged and SHA256-verified; no new responder unit run is claimed for v2.

| Service | Observed RTL replies | Host replies | Mismatches |
|---|---:|---:|---:|
| decoder_body | 1,392,000 | 0 | 0 |
| decoder_self | 787,200 | 0 | 0 |
| encoder_QKV_O | 384,000 | 0 | 0 |
| encoder_immutable | 1,947,520 | 0 | 0 |
| frontend_immutable | 55,720,960 | 0 | 0 |
| producer_positions | 2,560 | 0 | 0 |
| Total | 60,234,240 | 0 | 0 |

## Exact commands, pins and rerun

Working directory: `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design`. `commands-v2.json` contains the full exact argument vectors, including the complete RTL list. Adjacent log JSON records each niced command, working directory, PID, exit code and elapsed time.

```sh
.venv/bin/python -B overnight-20261014/onchip-all/prepare_v2.py
.venv/bin/python -B overnight-20261014/onchip-all/audit_v2.py
.venv/bin/python -B overnight-20261014/onchip-all/run_stage_v2.py lint-full
.venv/bin/python -B overnight-20261014/onchip-all/run_stage_v2.py generate-full
.venv/bin/python -B overnight-20261014/onchip-all/run_stage_v2.py compile
.venv/bin/python -B overnight-20261014/onchip-all/run_stage_v2.py fixture
.venv/bin/python -B overnight-20261014/onchip-all/run_stage_v2.py positive
.venv/bin/python -B overnight-20261014/onchip-all/run_stage_v2.py compare
.venv/bin/python -B overnight-20261014/onchip-all/run_stage_v2.py render
.venv/bin/python -B overnight-20261014/onchip-all/audit_v2.py --verify-pins
```

Before another positive run, archive existing `actual` under the authorized runtime directory; the runner refuses to overwrite it. Runtime directory: `~/.local/state/routevoice-internal-runs/20261014/onchip-all/v2/`; binary: `obj/Vrv_allonchip_top_all_v2`. Its SHA256 is in `binary-pin-v2.json`. Direct v2 input pins: `build-input-pins-v2.json` (166 files). Constant evidence, source hashes and v1 pins: `input-audit-v2.json`. ROM hashes: retained `rom-manifest.json`.

The work stayed local, with `nice -n 10`, at most eight compile jobs, and a 23 GiB reserve guard protecting the requested 22 GiB floor. The guard did not trigger. Final disk space was about 25 GiB. After compile/fixture, **552,859,930 bytes** of this worker's generated intermediates were reclaimed before F64; see `reclaimed-build-intermediates-v2.json`. Binary, headers, source and logs remain. **Regenerate before rebuilding.** No external files or other workers' sources were modified, and no cloud use or git commit/push occurred.

## Remaining scope

No requested v2 qualification remains unfinished. This closes the model-constant input boundary and validates the qualified F64 run. It does not establish physical synthesis/area/power/timing or a broader utterance/negative-test campaign; the original `connected_negative_suite_required=1` limitation remains visible and unchanged.
