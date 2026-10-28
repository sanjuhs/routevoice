---
license: apache-2.0
pretty_name: RouteVoice engine fix-2 runs (GF180, 24 Oct 2026)
---
# RouteVoice 1280×320 projection engine, "fix 2": LibreLane runs

This dataset holds LibreLane run directories for the RouteVoice engine in the open GF180MCU-D PDK. There are two archives.

## `archives/pipe2-ant/`: antenna close-out (final signoff, 24 Oct 2026, evening)
This run restarts the fix-2 run from detailed routing. The only change is up to 10 post-route antenna repair rounds instead of the default 3. It then runs full signoff.

Results (from `runs/pipe2-ant/final/metrics.json`):
- 150 ns met in all 9 corners (worst setup +8.10 ns at max SS, worst hold +0.32 ns);
- routing DRC 0, Magic DRC 0, KLayout DRC 0, GDS XOR 0;
- Netgen LVS: unique match;
- antenna: **0 nets, 0 pins**.

Contents: `runs/pipe2-ant/`, `inputs/full-pipe2-ant-local.json` and `flow-ant.log`. It starts from `runs/pipe2/46-openroad-detailedrouting/state_in.json` in the archive below, so restore both archives into the same directory.

    hf download sanjuhs/routevoice-engine-fix2-20261024 --repo-type dataset --local-dir dl
    cat dl/archives/pipe2-local/pipe2-local.tar.zst.part* | zstd -dc | tar -xf -
    (cd pipe2-local && cat ../dl/archives/pipe2-ant/pipe2-ant.tar.zst.part* | zstd -dc | tar -xf -)
    (cd pipe2-local && shasum -a 256 -c ../dl/manifest.sha256 && shasum -a 256 -c ../dl/manifest-pipe2-ant.sha256)

## `archives/pipe2-local/`: the full fix-2 run (synthesis to signoff, 24 Oct 2026, morning)
Results (from `runs/pipe2/final/metrics.json`):
- 150 ns met in all 9 corners (worst setup +8.34 ns);
- DRC 0 (routing, Magic, KLayout), XOR 0, LVS unique match;
- antenna: 11 nets open, which the run above closes.

`power/` holds the switching-activity file. `engine_local_pipe2.sv` is the generated engine RTL. `manifest.sha256` has the SHA-256 of every file before packing.

Archives are tar + zstd, split into 8 GB parts. Routed power for both runs, and all source code and documentation, are in the RouteVoice repository at `routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/pipe2/`.
