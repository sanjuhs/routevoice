# Paper artifact index

Reviewed 28 October 2026. Read the [correction ledger](REVIEW-2026-10-28.md) alongside the [paper](RouteVoice-paper-draft.pdf). **Reports, RTL demonstrations, physical checks and prospective designs have different scopes.** Neither the paper nor these archives establish fabricated silicon or an integrated real-time recognizer.

## Small public evidence — no large download required

| Claim or result | Public source |
|---|---|
| Quality protocol, model hashes, 120 test conditions per model, WER and uncertainty | [K64 report](evidence/docs/TAALAS-K64-QUALITY-RESULT.md), [summary](evidence/reports/taalas-k64-quality-summary-v1.json), [scores](evidence/reports/taalas-k64-reserved-test-scores-v1.json) |
| Three complete recognizer RTL demonstrations | [W11 report](evidence/overnight-20261014/finish-1023/w11-taalas-e2e/RESULTS.md), [release clips/logs](../routing-voice-chip-design/release-v1/demo/) |
| Storage accounting | [W11 JSON](evidence/overnight-20261014/finish-1023/w11-taalas-e2e/results.json) |
| Projection numerical contract | [Contract](../routing-voice-chip-design/overnight-20261014/fabric-k64/CONTRACT.md) |
| Final engine implementation and closure | [Engine README](../routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/pipe2/README.md), [flow/generator/bench](../routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/pipe2/) |
| Final antenna-closed engine metrics, LVS, STA, power methodology | [Final evidence](../routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/pipe2/evidence-ant/), [activity evidence](../routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/pipe2/evidence/) |
| Full-recognizer composed synthesis | [W12 report](evidence/overnight-20261014/finish-1023/w12-synth/RESULTS.md) |
| Bank layout, readback and representative LVS | [W13 report](evidence/overnight-20261014/finish-1023/w13-arrays/RESULTS.md) |
| Driver/control qualification and capture limits | [W13 driver report](evidence/overnight-20261014/finish-1023/w13-arrays/DRIVERS-RESULTS.md) |
| Local READY leaves and unresolved density | [W14 report](evidence/overnight-20261014/finish-1023/w14-blocks/RESULTS.md), [supplemental audit](evidence/overnight-20261014/finish-1023/w14-blocks/physical-audit/RESULTS.md) |
| 160-SRAM protocol test, not neural arithmetic | [Bridge report](evidence/overnight-20261014/finish-1023/w14-blocks/bridge-sram/RESULTS.md), [JSON](evidence/overnight-20261014/finish-1023/w14-blocks/bridge-sram/results.json) |
| Partial two-die assembly and synthetic wiring | [W15 report](evidence/overnight-20261014/finish-1023/w15-chip/RESULTS.md), [connectivity contract](evidence/overnight-20261014/finish-1023/w15-chip/TOPLEVEL.md), [JSON](evidence/overnight-20261014/finish-1023/w15-chip/results.json) |
| Layout images, demo and result tables | [Release package](../routing-voice-chip-design/release-v1/) |

The 25 byte-preserved review sources are mirrored in the public [Hugging Face supplement](https://huggingface.co/datasets/sanjuhs/routevoice-v1-paper-evidence-20261028/tree/239114fc57b384999c2bd8576ab7f0a06706928f) at revision `239114fc57b384999c2bd8576ab7f0a06706928f`. Its [manifest](evidence/manifest.json) records the source paths, sizes and SHA-256 hashes. Reports retain historical internal links that may refer outside this selected bundle. The W14 supplemental audit summary covers its initial runs; the later six READY leaves and their density counts are enumerated in the W14 root report.

```sh
# Run from paper/evidence after cloning this repository.
shasum -a 256 -c SHA256SUMS
```

## Larger archives and fixed revisions

| Dataset | Pinned revision | Scope |
|---|---|---|
| [Final engine](https://huggingface.co/datasets/sanjuhs/routevoice-engine-fix2-20261024/tree/c5bbf9ea0998d27ce27dd4f96c6504378d1b20e9) | `c5bbf9ea0998d27ce27dd4f96c6504378d1b20e9` | About 97 GB **uncompressed**, about 19.7 GB compressed; fix 2 and antenna close-out, 24 October |
| [Cloud workspace](https://huggingface.co/datasets/sanjuhs/routevoice-pod-final-20261022/tree/c2cee6c32d3fc353e1eac52b2664bfd198475551) | `c2cee6c32d3fc353e1eac52b2664bfd198475551` | About 53 GB **uncompressed**; 105,826-file workspace snapshot, 22 October |

The cloud archive predates final engine timing/antenna closure. Its earlier failures are intentional historical evidence. The new supplement comes from the local research workspace and is identified by its own hashes; it is not assumed identical to that earlier cloud snapshot. Archive sizes are approximate storage planning figures, not model payload sizes.

### Restore the final engine

Requires `hf`, `zstd`, `tar`, adequate free disk space and the archived tool dependencies. These commands reproduce the archive's documented extraction layout; the review verified metadata/manifests and selected source files, not a new full download or flow rerun.

```sh
hf download sanjuhs/routevoice-engine-fix2-20261024 --repo-type dataset \
  --revision c5bbf9ea0998d27ce27dd4f96c6504378d1b20e9 --local-dir engine-download
cat engine-download/archives/pipe2-local/pipe2-local.tar.zst.part* | zstd -dc | tar -xf -
(cd pipe2-local && cat ../engine-download/archives/pipe2-ant/pipe2-ant.tar.zst.part* | zstd -dc | tar -xf -)
(cd pipe2-local && shasum -a 256 -c ../engine-download/manifest.sha256)
(cd pipe2-local && shasum -a 256 -c ../engine-download/manifest-pipe2-ant.sha256)
```

The final GDS is `pipe2-local/runs/pipe2-ant/final/gds/rv_k64_array_port.gds`; final metrics and other views are beside it under `final/`. The initial fix-2 run is `pipe2-local/runs/pipe2/`. Restore both because antenna close-out resumes from the first run's detailed-routing state. Original absolute run paths may need adjustment before rerunning the scripts.

### Restore the earlier cloud evidence

Download only required archive groups when possible:

```sh
hf download sanjuhs/routevoice-pod-final-20261022 --repo-type dataset \
  --revision c2cee6c32d3fc353e1eac52b2664bfd198475551 --local-dir pod-download
mkdir -p restored-workspace
# Example: W15. Repeat for other required groups listed below.
(cd pod-download/archives/w15-chip && shasum -a 256 -c w15-chip.parts.sha256)
cat pod-download/archives/w15-chip/w15-chip.tar.zst.part* | zstd -dc | tar -xf - -C restored-workspace
```

| Archive group | Restored path / purpose |
|---|---|
| `w15-chip` | `rv/overnight-20261014/finish-1023/w15-chip/`: assembly, batch-2, fill trials |
| `w12-synth` | `rv/overnight-20261014/finish-1023/w12-synth/`: per-unit synthesis |
| `misc` | W14 blocks, `fabric-k64`, buffered engine, tools/PDK and setup |
| `w10-rest` | Earlier W10 scripts, ECO, activity and reports |
| `w10-runs-full` | Earlier full route, not final 24 October engine |
| `w10-runs-C` | Earlier variant-C routing attempt |

After restoring **all** groups, run `shasum -a 256 -c ../pod-download/pod-manifest.sha256` from `restored-workspace`. A partial restore will report missing files for omitted groups. The curated GitHub repository is not a self-contained replay of every original workspace dependency. The quality evaluator has a reserved-test no-repeat guard; the public scores support inspection without re-exposing the test during model selection.
