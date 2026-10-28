---
license: apache-2.0
pretty_name: RouteVoice pod final snapshot (22 Oct 2026)
---

# RouteVoice: final RunPod workspace snapshot, 22 October 2026

This is a complete copy of `/workspace` from the RunPod CPU pod `rv-overnight-pnr2`, saved before the pod was deleted.
RouteVoice is a GF180 speech-to-text chip project built around a Taalas-style fixed-weight array. The speech model is Moonshine Tiny Streaming English (MIT).

## What's inside (`archives/`)

| Archive | Pod path | Contents |
|---|---|---|
| `w10-runs-full` | `rv/overnight-20261014/finish-1023/w10-route/runs/full` | The 1280×320 engine fully routed in LibreLane: ODB, DEF, SPEF, GDS/MAG, STA, Magic/KLayout DRC, Netgen LVS |
| `w10-runs-C` | `.../w10-route/runs/C` | The variant-C run, from floorplan through global routing |
| `w10-rest` | `.../w10-route` minus the two runs above | Synthesis, the ECO run, gate-level output (SAIF), post-layout files, recovery logs, scripts, results |
| `w15-chip` | `.../finish-1023/w15-chip` | Two-die top-level assembly (batch-2) and filled GDS |
| `w12-synth` | `.../finish-1023/w12-synth` | Whole-recognizer Yosys synthesis per unit: generic, GF180 and ECP5 |
| `misc` | `w14-blocks`, `engine-buffered`, `fabric-k64` (including the GF180 PDK copy), `runpod`, `rv/tools`, `setup.log` | Inputs and tools |

Each archive is a zstd-compressed tar stream split into 8 GiB parts. Each archive has two companion files:
- `<name>.parts.sha256`: the checksum of every part;
- `<name>.filecount`: the number of files in the tar.

`pod-manifest.sha256` lists the SHA-256 of every one of the 105,826 files under `rv/`, as it stood on the pod.

## Restore

```bash
hf download sanjuhs/routevoice-pod-final-20261022 --repo-type dataset --local-dir rv-pod
cd rv-pod/archives/w10-runs-full && sha256sum -c w10-runs-full.parts.sha256
cat w10-runs-full.tar.zst.part* | zstd -dc | tar -xf - -C /path/to/workspace
```

Tar paths are relative to the pod's `/workspace`, starting with `rv/...` or `setup.log`. To check a restored tree, run `sha256sum -c pod-manifest.sha256` from that workspace root.

## Status at snapshot time

- The engine is routed: routing DRC 0, Magic and KLayout DRC 0, LVS matches uniquely.
- Antenna fails: 151 pin / 130 net violations.
- Setup timing fails at 150 ns: it reaches ≈4.5 MHz at TT and ≈2.5 MHz at SS. Hold passes.
- Routed power was not measured, because OpenROAD's power step errored.
- See `w10-route/RESULTS.md` and `results.json` inside `w10-rest`.
