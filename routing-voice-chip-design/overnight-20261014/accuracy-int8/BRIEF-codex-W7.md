# Codex brief W7: does an INT8 frontend keep recognition accuracy? (removes a one-die assumption)

AUTHORIZATION: the user lifted the 13 Oct pause on 14 Oct 2026 (`AGENTS.md`) and extended tonight's run to ≈08:10 IST. The lead (Claude) re-checks results. Never fabricate; preserve failures. Reading (≤10 min): `skills/taalas-fixed-weight-routing/references/accuracy-validation-and-recovery.md`, and how earlier validations were run (`reports/codebook-4bit-optimal-rectangular-k64*.json`, `reports/stt-baseline-pilot-v1.json`, `reports/stt-requirements.json`, `scripts/evaluate_stt.py`, `scripts/evaluate_reserved_k64_test.py`).

## Question
Tonight's floorplan shows a one-die (25 × 31 mm) GF180 RouteVoice chip is possible if, among other things, the frontend's 2,074,560 FP32 coefficients (the conv/linear frontend weights, 8.3 MB) are stored as **INT8** instead of FP32. Does that keep word error rate?

## Task
1. Start from the selected frozen candidate `models/candidates/codebook-4bit-optimal-rectangular-k64` (the model the chip implements). Identify the frontend coefficient tensors: the same tensors the chip's frontend ROM holds. Cross-check against `~/.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3/frontend/shared/*.bin` and the ledger `experiments/chip-integration-20261012-current-learned-fulltables-service-ledger-v2/ledger.json` (service "frontend immutable"). Record names, shapes and hashes.
2. Make an **INT8 variant**: symmetric per-output-channel INT8 weights with FP32 scales, dequantized for inference, so only weight storage precision changes. Keep everything else bit-identical. Also make a per-tensor INT8 variant as a second data point.
3. Evaluate on the **same frozen validation split and scorer** the project used for the K64 point gates: clean / other (harder) / 10 dB noise. Use the existing evaluation script, unmodified if possible; if you must wrap it, keep the wrapper minimal and documented. Do NOT use the reserved test split. Compare WER against the unmodified K64 candidate run in the same session. If the run is long, a subset is acceptable only if both models use the identical subset, and you say so.
4. Report WER per condition for FP32 baseline vs INT8 per-channel vs INT8 per-tensor, with deltas and number of utterances/words, plus the project's acceptance limits from `reports/stt-requirements.json` (the ≤2-point degradation rule). State clearly whether INT8 passes the point gates.

## Paths and rules
- Repo: `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design`. Workspace (write ONLY here): `overnight-20261014/accuracy-int8/`. Never modify the original candidate files; write variants into your workspace.
- Python: `.venv/bin/python` (onnxruntime should be there; check). Speech data: `data/librispeech` (local; no downloads).
- CPU is shared: ≤ 4 threads (set `OMP_NUM_THREADS`/onnxruntime intra-op threads), `nice`, keep ≥ 22 GiB free. No git, no cloud.
- Print `W7-STATUS: <result>` after each step. Finish by ≈07:30 IST with `RESULTS.md` + `results.json`.
