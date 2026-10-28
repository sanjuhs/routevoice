---
license: apache-2.0
pretty_name: RouteVoice v1 paper evidence — 28 October 2026
tags:
- speech-recognition
- hardware
- gf180
- reproducibility
---
# RouteVoice v1 paper evidence

A compact, byte-preserved evidence supplement for [RouteVoice](https://github.com/sanjuhs/routevoice) and its [paper](https://github.com/sanjuhs/routevoice/blob/main/paper/RouteVoice-paper-draft.pdf). Published on 28 October 2026 during an evidence review. It contains reports and evaluation ledgers, not a newly run experiment or fabricated-silicon measurement.

## Contents

- `docs/TAALAS-K64-QUALITY-RESULT.md`: quantization selection, reserved-test quality and limits.
- `reports/`: frozen K64 quality summary, test protocol, scores, decisions, export audit and requirements.
- `scripts/` and `tests/`: original evaluation/recount sources and bootstrap fixture, preserved with their original hashes. These are source snapshots; imports and model/input dependencies remain in the original research workspace. Do not rerun the reserved candidate test to select a more favorable outcome.
- `overnight-20261014/finish-1023/`: W11 storage, W12 synthesis, W13 arrays/periphery, W14 macro/density and SRAM protocol evidence, and W15 partial integration reports.
- `manifest.json` and `SHA256SUMS`: exact byte counts and hashes of the 25 preserved source files.

Paths are relative to the original `routing-voice-chip-design` subtree. Internal links and absolute paths inside preserved reports retain their historical meaning and may reference files outside this supplement. They are not promises that every intermediate file is included. Use the [artifact index](https://github.com/sanjuhs/routevoice/blob/main/paper/ARTIFACTS.md) for the public entry points and archive restoration instructions.

## What the evidence supports

The complete recognizer matches frozen K64 software on three RTL demonstrations. A separate projection engine closes setup/hold in nine corners and passes the recorded geometric/equivalence/antenna checks; electrical violations remain. The engine has not been fabricated. The K64 quality test is a small, reserved candidate test with limited noisy-speech margin. W14 READY labels defer density, whose checks still fail; W15 remains mostly synthetic wiring and stubs. The 160-SRAM result is a deterministic memory protocol test, not a complete recognizer execution.

## Verify

After downloading this dataset, run from its root:

```sh
shasum -a 256 -c SHA256SUMS
```

The frozen quality summary SHA-256 is `5489f74b2c11a06acf4ecebb4f8bfc8e02916c0d3aa60dbc639b518edd62948b`. Every artifact hash listed within that summary was matched before publication.

## Larger archives

- [Final engine, 24 October](https://huggingface.co/datasets/sanjuhs/routevoice-engine-fix2-20261024): about 97 GB uncompressed, including antenna close-out.
- [Cloud workspace, 22 October](https://huggingface.co/datasets/sanjuhs/routevoice-pod-final-20261022): about 53 GB uncompressed; predates final engine closure.

This supplement was copied from the local research workspace. It is not asserted to be byte-identical to the earlier cloud archive; its own manifest identifies the published snapshot. Raw audio, model binaries, private credentials and entire SSD contents are not included. Evaluation transcripts are from the documented LibriSpeech-derived test. Project code and reports follow RouteVoice's Apache-2.0 license; third-party data and tools retain their original terms.
