# W7: INT8 frontend validation

Full frozen development validation: 32 distinct utterances from 16 speakers; 16 clean, 16 other, and the same 16 clean clips with frozen 10 dB noise. 144 fresh native processes completed. Reserved test was not used.

| Condition | Utterances / words | K64 FP32 ROM baseline | INT8 per-output-channel | Δ pp | INT8 per-tensor | Δ pp |
|---|---:|---:|---:|---:|---:|---:|
| clean | 16 / 330 | 6.6667% (22/330) | 9.0909% (30/330) | +2.4242 | 100.0000% (330/330) | +93.3333 |
| other | 16 / 325 | 18.1538% (59/325) | 22.7692% (74/325) | +4.6154 | 100.0000% (325/325) | +81.8462 |
| white_noise_10db | 16 / 330 | 19.3939% (64/330) | 20.0000% (66/330) | +0.6061 | 100.0000% (330/330) | +80.6061 |

Frozen limits: clean WER ≤15%, other ≤35%, noise ≤40%, and degradation ≤2 percentage points in **each** condition. W7 compares each INT8 arm against the unmodified K64 run in this same session.

- **int8_per_channel: FAIL** W7 point gates. Historical original-relative gates: FAIL (historical reference, not a same-session original run).
- **int8_per_tensor: FAIL** W7 point gates. Historical original-relative gates: FAIL (historical reference, not a same-session original run).

The same-session baseline has 0 normalized transcript differences from the earlier isolated K64 validation; details are preserved in results.json.

## What was stored and changed

All five frontend ROM hashes match K64. The 2,074,560 FP32 ROM coefficients comprise 2,073,600 weights plus 960 biases. Only the three weight tensors were requantized; biases retain their exact FP32 bytes. Tensor names, shapes, hashes and ROM mapping are in frontend-inventory.json.

Symmetric quantization uses FP32 absmax/127 scales, nearest-even rounding and clipping to [-127,127], with zero offset. Output axes are linear axis 1, Conv1 axis 0 and Conv2 axis 0. Per-tensor uses one scale for each of the three tensors. Saved INT8 blobs plus FP32 scales independently decode to the exact inference weights. No fitting or calibration was used.

| Storage | Original ROM bytes | New INT8 weights + scales + FP32 biases |
|---|---:|---:|
| int8_per_channel | 8,298,240 | 2,082,560 = 2,073,600 + 5,120 + 3,840 |
| int8_per_tensor | 8,298,240 | 2,077,452 = 2,073,600 + 12 + 3,840 |

The source model already stores these weights as INT8 codes with FP32 multiplicative scales and additive offsets; Conv2 scales are along input channels. The chip fixture stores their expanded FP32 values. Preserving that source representation is a separate possible exact-storage design; W7 measures the specifically requested symmetric re-quantization.

## Execution and proof scope

The wrapper reuses evaluate_stt_isolated.run_case, stt_metrics and the exact rational gate. Its only runner adaptations redirect outputs to this workspace and launch a local copy of isolate_native_worker.py with its single-thread environment assertion changed. All original scripts are untouched. OMP/BLAS/native ORT are set to one thread, one child at a time, under nice. The full saved worker and effective runner are provided.

Only frontend.weights.ort is replaced for each variant, with a loader returning the saved dequantized constants under the identical output names/shapes. Its graph serialization changes; every other runtime file, including frontend.model.ort, encoder, decoder, affine metadata, tokenizer and streaming configuration, is byte-identical to K64. CPU ORT output equality is checked. Same-session baseline uses unmodified K64 files. Input hashes and saved NPY hashes match all 48 frozen validation inputs; returned PCM crops match across arms.

All predictions, close markers, failures if any, input/model hashes and timings are preserved. No candidate was tuned or chosen using this run. These are additional development-validation exposures, not a fresh held-out test. Small read-speech/synthetic-noise point gates do not prove population retention, one-die fit, sub-watt power, timing, or an implemented INT8 hardware dequantizer.

Root plan.md was absent. The skill, supplied notes, accuracy workflow, relevant local patent excerpts and named evaluator/requirement reports were consulted; no new circuit assumptions are made.

Reproduction: `env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/accuracy-int8/prepare.py`, then the same command with `run.py`. Scripts intentionally refuse to overwrite this completed run; use a separate authorized workspace for a future repetition.

## Exact existing INT8 representation: separate finding

The independent post-run audit exported the source INT8 arrays and their original FP32 scales and additive offsets, then reconstructed **all 2,074,560 ROM coefficients bit-for-bit**, including the retained biases. This is the existing K64 encoding, not a newly fitted candidate or a favorable rerun. Payload is **2,090,240 bytes**: 2,073,600 INT8 bytes + 12,800 scale/offset bytes + 3,840 bias bytes. Files and hashes are in `existing-affine-int8-exact/manifest.json`.

Thus the requested symmetric INT8 schemes fail, while an exact compact source representation already exists at almost the same storage size. Using it on-chip requires original channel axes (Conv2 input-channel axis 1), additive offsets, and separate FP32 multiply/add rounding. That hardware path has not been implemented or timed here, so this is numerical evidence for a storage option, not proof of one-die fit.

The final audit recomputed all 144 scores, checked unique complete case coverage and unchanged model/protocol pins, and independently confirmed all gates with integer comparisons. All 48 per-tensor hypotheses contain zero normalized words; 100% WER is an observed failure, with successful native process exits, not a missing-result placeholder. Audit: `audit.json`.
