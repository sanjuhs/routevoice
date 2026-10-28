---
license: apache-2.0
pretty_name: RouteVoice engine fix-2 run (GF180, 24 Oct 2026)
---
# RouteVoice 1280×320 projection engine, "fix 2": full LibreLane run

This is the complete LibreLane run directory for the RouteVoice engine, from synthesis through signoff, in the open GF180MCU-D PDK. The flow finished on 24 Oct 2026.

**Results** (from `runs/pipe2/final/metrics.json`):
- 150 ns met in all 9 corners (worst setup +8.34 ns at max SS);
- routing DRC 0, Magic DRC 0, KLayout DRC 0, GDS XOR 0;
- Netgen LVS: unique match;
- antenna: 11 nets open;
- routed power with real switching data: 0.188 W, 287 pJ/MAC.

`power/` holds the activity file and the power run. `engine_local_pipe2.sv` is the generated engine RTL.

Archives are tar + zstd, split into 8 GB parts under `archives/pipe2-local/`. `manifest.sha256` has the SHA-256 of every file before packing.

To restore:

    hf download sanjuhs/routevoice-engine-fix2-20261024 --repo-type dataset --local-dir dl
    cat dl/archives/pipe2-local/pipe2-local.tar.zst.part* | zstd -dc | tar -xf -
    (cd pipe2-local && shasum -a 256 -c ../dl/manifest.sha256)

Source code and documentation are in the RouteVoice repository, at `routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/pipe2/`.
