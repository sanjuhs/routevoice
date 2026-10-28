# RouteVoice v1 release package (28 Oct 2026)

What this milestone shows: a complete speech-recognition transformer (Moonshine Tiny, 4-bit codebook weights) compiled into hardwired-weight logic, verified bit-exact from audio to text in RTL simulation. Its 1280×320 compute engine is laid out in the open GF180MCU 180 nm process and passes every manufacturing check the open flow runs. It also shows what the approach would take at larger model sizes.

What it does not show: no chip has been fabricated, and the full two-die chip is only partly integrated. See [What is not done](#what-is-not-done).

## Contents

| Folder | What it is |
|---|---|
| [`demo/`](demo/) | The three audio clips the hardware model transcribes bit-exactly, their simulation logs, a rendered demo animation (MP4 and GIF), and `replay.py` for a terminal replay |
| [`figures/layout/`](figures/layout/) | 1920×1080 zoom sequences rendered from the GDS: one weight bank and the routed engine, from full die down to transistors |
| [`figures/signoff-table.png`](figures/signoff-table.png), [`.md`](figures/signoff-table.md) | Engine signoff results, read from the final run's metrics |
| [`figures/scaling-area.png`](figures/scaling-area.png), [`scaling-energy.png`](figures/scaling-energy.png), [`scaling-data.csv`](figures/scaling-data.csv) | Area and compute energy against model size: measured points plus labelled projections |
| [`scripts/`](scripts/) | The scripts that made all of the above |
| [`../../paper/`](../../paper/) | Research paper (LaTeX, PDF, and `make-arxiv.sh` for the arXiv source bundle) |

## The demo

![Demo: three recordings go through the hardware model and come out as bit-exact text](demo/routevoice-demo.gif)

[`demo/routevoice-demo.mp4`](demo/routevoice-demo.mp4) is the same animation at 1080p with the clip audio (34 s). It is made by `scripts/make_demo_video.py` from the logs: the progress bars and clock counter follow the logged clock milestones, and the reply counters are the logged totals.

| Clip | Audio | RTL text | Tokens | Clocks | Check |
|---|---|---|---|---:|---|
| 1 | Wispr 007 seg 0, 1.28 s | "Switch on the lights" | 28176, 373, 278, 26068, 2 | 312,578,649 | 18/18 internal outputs bit-identical |
| 2 | Wispr 031 seg 1, 1.28 s | "Plant present." | 18058, 2198, 29889, 2 | 309,272,913 | 18/18 |
| 3 | LibriSpeech dev-clean 1919-142785-0022 seg 0, 1.22 s | "Seasonable." | 24791, 519, 29889, 2 | 308,976,820 | 18/18 |

Each WAV is the exact PCM the RTL consumed: `scripts/extract_clips.py` checks every clip's SHA-256 against the v49 tally before writing it (`demo/clips/clips.json`). The simulations ran on 21 Oct 2026 under Verilator, about an hour each. `replay.py` replays the recorded logs fast-forwarded; it does not re-simulate.

```sh
python3 demo/replay.py --play     # all three clips, with audio (macOS)
python3 demo/replay.py --clip 1 --seconds 30
```

Full evidence: `../overnight-20261014/finish-1023/w11-taalas-e2e/`.

## Key numbers

| Item | Value | Source |
|---|---|---|
| Weight storage after index + codebook | 28.6 MB → 17.5 MB, 0 mismatches | W11 `RESULTS.md` |
| Weight banks, all 98 matrices | 31,457,280 four-bit weights in 174.7 mm², 81 banks DRC-clean | W13 `RESULTS.md` |
| Engine die | 22.84 mm², 1,146,232 cells, 68.9 m of wire | `w10-route/pipe2/evidence-ant/final-metrics.json` |
| Engine signoff | DRC 0 (routing, Magic, KLayout), LVS unique match, XOR 0, antenna 0 | same |
| Engine timing at 150 ns | 9/9 corners met, worst setup +8.10 ns (SS), worst hold +0.32 ns | same |
| Engine power, real-speech activity | 0.188 W, 117 µJ per projection, 287 pJ/MAC | `w10-route/pipe2/README.md` |

## What is not done

- **No silicon.** All results come from open-source tools on an open PDK.
- **The chip is not integrated.** The two-die top level has real weight banks and 4 logic macros placed and routed, with top-level wiring DRC 0. Drivers are still pending, IR drop fails under the assumed load, and full-chip DRC/LVS and timing have not been run (`w15-chip/RESULTS.md`).
- **Engine warnings.** Max-slew (902,948 at worst corner), max-cap and max-fanout warnings remain. They cause no setup or hold failure, but foundry signoff would require fixing them.
- **Area.** As written, the full recognizer synthesizes to about 1,198 mm² of GF180 logic, because its 8.17 M mutable bits are flip-flops. They need mapping to SRAM.
- **Real time is unproven** for the whole recognizer. One engine meets a dense one-pass estimate; a real-time service schedule has not been built.
- **The scaling charts are projections.** Only the filled points are measured. The 28 nm bands assume 20–40× smaller area and 10–30× lower energy than GF180; they are not measurements.

## Large files

The engine's run directories (97 GB) and the cloud pod's workspace (53 GB) are in public Hugging Face datasets, checksum-verified:
- [`sanjuhs/routevoice-engine-fix2-20261024`](https://huggingface.co/datasets/sanjuhs/routevoice-engine-fix2-20261024): fix-2 engine run and antenna close-out, including the final GDS;
- [`sanjuhs/routevoice-pod-final-20261022`](https://huggingface.co/datasets/sanjuhs/routevoice-pod-final-20261022): full cloud workspace.

## Rebuilding the figures

```sh
pip install klayout matplotlib numpy soundfile
python scripts/render_gds.py <bank.gds> figures/layout weight-bank --zooms 1,8,64,400 --cx 0.43 --cy 0.6
python scripts/render_gds.py <engine.gds> figures/layout engine --zooms 1,6,40,300
python scripts/make_figures.py       # signoff table, scaling charts, paper figure
python scripts/make_demo_video.py    # demo/routevoice-demo.mp4 and .gif (needs pillow and ffmpeg)
```

The bank GDS (`W13_ENC0_B00`, 159 MB, SHA-256 in `../overnight-20261014/finish-1023/w13-arrays/GDS-LOCATIONS.json`) is too large for git and is not in this repository. The engine GDS is `runs/pipe2-ant/final/gds/rv_k64_array_port.gds` in the engine HF dataset (978 MB). `extract_clips.py` needs the original segment `.npy` files, which are in the private working archive.
