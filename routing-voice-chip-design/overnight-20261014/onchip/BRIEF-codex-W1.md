# Codex brief W1 — move all model weights on-chip (overnight, 14 Oct 2026)

AUTHORIZATION: the 13 October pause in `AGENTS.md` was lifted by the user on 14 October 2026 (in chat with the lead, Claude); `AGENTS.md` now records this. Compilation and simulation are authorized for this run. Keep the AGENTS.md reading requirement to ~15 minutes (skill + relevant notes), then execute.

You are a worker on the RouteVoice 180 nm speech-recognition chip. The lead (Claude) re-runs and checks everything; report honestly, show logs on failure, never fabricate a pass.

## Background
The full recognizer RTL (PCM audio → frontend → 6-layer encoder → producer → greedy decoder → tokens/EOS) is bit-exact against the frozen 4-bit model in Verilator. BUT six fixed-weight services are still answered by the C++ test harness through top-level ports, i.e. the weights are NOT on the chip:

| Service | Bytes | C++ source |
|---|---:|---|
| decoder body cross/FF fixed service | 8,908,800 | `producer_services.hpp` (prod::Harness, roles 4..7) |
| compact decoder fixed self service | 2,519,040 | `taalas_decoder_token_compact_services.hpp` / `taalas_adapter_session_compact_token_services_f500_v1.hpp` |
| encoder QKV head / O fixed rows | 2,457,600 | `encoder_services.hpp` (head/O providers) |
| encoder immutable memory regions 4..12 | 5,146,880 | `encoder_services.hpp` |
| frontend immutable scalar regions 0,1,4,5,8 | 8,298,240 | `frontend_services.hpp` |
| producer fixed positions | 1,310,720 | `producer_services.hpp`; an RTL ROM already exists: `experiments/runtime-source-position-immutable-rom-source-20261013-v1/` |

Authoritative ledger: `experiments/chip-integration-20261012-current-learned-fulltables-service-ledger-v2/ledger.json` (per-service request counts, response widths, schedules).

## Paths
- Repo root for this work: `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design`
- Current top RTL + C++ host: `experiments/chip-integration-20261012-frontend-learned-norm-connected-source-v3/` (top `rv_pcm_encoder_greedy_frontend_history_producer_metadata_KV_tables_onboard_v1.sv`, host `four_stage.cpp`, service headers `*.hpp`).
- Exact Verilator lint/generate commands with the full file list: `experiments/chip-integration-20261012-Q8-learned-fulltables-lint-generation-control-v2/commands.json` (keys `lint-full`, `generate-full`). Compile: `experiments/chip-integration-20261012-Q8-learned-fulltables-compile-v3/commands.json` (+ `no-pch.mk`). You may use more make jobs (-j8).
- Qualified F64 run commands ("Switch on the lights", 5 tokens incl. EOS, all 18 output comparisons): `experiments/chip-integration-20261012-Q8-learned-fulltables-numerical-run-v2/commands.json` (stages `fixture`, `positive`, `render`). The `positive` stage previously took ~55 min of simulation.
- Weight images (read-only inputs): `~/.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3/` (`cross/`, `self/`, `ff/`, `head/`, `frontend/shared/`, `blobs/`, `decoder/`, `encoder/`, `producer/paths.txt`).
- Your workspace (write ONLY here): `overnight-20261014/onchip/`. Put generated objects/binaries under `~/.local/state/routevoice-internal-runs/20261014/onchip/`.
- Python with numpy: `.venv/bin/python`.

## Method (required)
1. For each service, write a synthesizable SystemVerilog responder module (`rv_onchip_<service>_v1.sv`) that answers the SAME request/response protocol the C++ service implements, with the weight data held in on-chip ROM. For simulation the ROM contents load with `$readmemh` from hex files you generate from the SAME .bin images the C++ service reads (write a Python generator; record sha256 of inputs/outputs). Make the reply schedule cycle-identical to the C++ service if at all possible (the ledger documents schedules such as "held N+3"); if not identical, it must still obey valid/ready/tag/held semantics.
2. Create a new top wrapper `rv_allonchip_top_v1` (in your workspace) that instantiates the existing top unchanged plus the responders, wiring each service's request/response ports internally. Re-export the internal request/response signals as debug outputs so the host can still observe them.
3. Copy `four_stage.cpp` (and any .hpp you must change) into your workspace. In the copy, for each service moved on-chip: the C++ service must STOP driving responses and instead CHECK — every RTL-generated response must equal what the C++ service would have sent for that request (data, tag, row, layer). Keep all existing conservation counters/asserts meaningful (count observed RTL replies instead of host replies). Add a final line printing, per service, `ONCHIP service=<name> rtl_replies=<n> host_replies=0 mismatches=0`.
4. Order of work (do them one at a time, re-running the F64 positive after each group, so partial progress is still a valid result):
   a. decoder body cross/FF + compact decoder self (largest decoder weights),
   b. encoder QKV/O + encoder immutable,
   c. positions (reuse the existing ROM source),
   d. frontend immutable.
   Before the long F64 run, do quick checks: lint, generate, compile, and the `fixture` stage.
5. Success for each group = F64 `positive` passes exactly as before (same 5 tokens through EOS, all 18 output comparisons, render "Switch on the lights") with host_replies=0 for the moved services.

## Constraints
- Do NOT modify any existing file outside `overnight-20261014/onchip/` (copy instead). Do not git commit/push. No cloud.
- Disk: check `df -h /` before builds; keep ≥ 20 GiB free. Delete your own stale object dirs if needed.
- CPU: another worker is running place-and-route; use `nice` and at most 8 compile jobs. Only ONE long F64 simulation at a time.
- Prefer a smaller verified result (e.g. group a fully passing) over many unverified changes.
- After each major step print `W1-STATUS: <what just finished / result>`.
- At the end write `overnight-20261014/onchip/RESULTS.md` with: services moved, ROM bytes now on-chip, exact commands, pass/fail evidence (paths to logs), simulation time, and anything not finished.
