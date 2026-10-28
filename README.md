# RouteVoice

**A speech-recognition transformer compiled into hardwired-weight logic, with its compute engine laid out in open 180 nm silicon.**

![Demo: three real recordings go through the hardware model and come out as bit-exact text](routing-voice-chip-design/release-v1/demo/routevoice-demo.gif)

<sub>Replay of the recorded RTL simulations (Verilator, about 310 million clocks per clip). The bars follow the logged clock milestones; every count comes from the logs. Full 1080p version with audio: [`routevoice-demo.mp4`](routing-voice-chip-design/release-v1/demo/routevoice-demo.mp4).</sub>

RouteVoice takes [Moonshine Tiny](https://github.com/moonshine-ai/moonshine), an open 34 M-parameter speech recognizer, and builds it as hardware in which the weights are part of the chip instead of being fetched from memory.

- Each transformer weight becomes a 4-bit index into a 16-entry codebook shared by 64 weights.
- Each index is fixed in metal: the positions of tiny Via1 connections in a mask-programmed array.

The idea follows public patent documents from [Taalas](https://taalas.com); this is an independent, fully open implementation.

| | |
|---|---|
| 🎧 **Demo** | [Three clips, audio to text, bit-exact](routing-voice-chip-design/release-v1/demo/) |
| 🎬 **Explainer video** | [Speech → Silicon, 5 min](#explainer-video) |
| 🪖 **Product concept** | [RoutingModule-180 helmet voice module: live website](https://routing-module-180.vercel.app) |
| 📄 **Paper** | [`paper/RouteVoice-paper-draft.pdf`](paper/RouteVoice-paper-draft.pdf) |
| 🧪 **Evidence** | [`release-v1/`](routing-voice-chip-design/release-v1/) · [lab log](OVERNIGHT-PROGRESS.md) · [run data on Hugging Face](https://huggingface.co/datasets/sanjuhs/routevoice-engine-fix2-20261024) |

## What is proven

| Claim | Evidence |
|---|---|
| The full recognizer RTL turns real audio into the right text, **bit-exact** with the frozen model: "Switch on the lights", "Plant present.", "Seasonable." (18/18 internal outputs each) | [`release-v1/demo/`](routing-voice-chip-design/release-v1/demo/), [`w11-taalas-e2e/`](routing-voice-chip-design/overnight-20261014/finish-1023/w11-taalas-e2e/RESULTS.md) |
| Weight storage drops from 28.6 MB to 17.5 MB with zero mismatches | [W11 results](routing-voice-chip-design/overnight-20261014/finish-1023/w11-taalas-e2e/RESULTS.md) |
| The 1280×320 projection engine (409,600 MACs) is routed in GF180MCU and **passes every open signoff check**: DRC 0 (routing, Magic, KLayout), LVS unique match, XOR 0, antenna 0 | [signoff table](routing-voice-chip-design/release-v1/figures/signoff-table.md) |
| It meets a 150 ns clock in all 9 PVT/RC corners; routed power with real-speech activity is 0.188 W (287 pJ/MAC) | [`w10-route/pipe2/`](routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/pipe2/README.md) |
| All 98 weight matrices exist as mask-programmed banks: 31.5 M four-bit weights in 174.7 mm², 81 banks DRC-clean | [W13 results](routing-voice-chip-design/overnight-20261014/finish-1023/w13-arrays/RESULTS.md) |

## Inside the silicon

<table>
<tr>
<td width="50%"><img src="routing-voice-chip-design/release-v1/figures/layout/weight-bank-zoom0400.png" alt="Weight bank close-up"></td>
<td width="50%"><img src="routing-voice-chip-design/release-v1/figures/layout/engine-zoom0300.png" alt="Engine standard cells"></td>
</tr>
<tr>
<td><b>The weights, in metal.</b> A 10 µm window of a weight bank. The cell grid is regular; the amber Via1 squares are not. Their positions are the stored 4-bit indices, so this pattern <i>is</i> the model.</td>
<td><b>The compute engine.</b> A 30 µm window of the routed 1280×320 engine: standard cells of the select-and-accumulate datapath. The full engine is 22.84 mm² with 1.15 M cells and 68.9 m of wire.</td>
</tr>
<tr>
<td><img src="routing-voice-chip-design/release-v1/figures/layout/weight-bank-zoom0008.png" alt="Weight bank at 8x"></td>
<td><img src="routing-voice-chip-design/release-v1/figures/layout/engine-zoom0040.png" alt="Engine at 40x"></td>
</tr>
<tr>
<td>One weight bank zoomed out: 409,600 four-bit weights in 2.27 mm².</td>
<td>The engine zoomed out: three routing layers over dense logic.</td>
</tr>
</table>

Full zoom sequences, from die to transistors, are in [`release-v1/figures/layout/`](routing-voice-chip-design/release-v1/figures/layout/).

![Engine signoff: all manufacturing checks pass](routing-voice-chip-design/release-v1/figures/signoff-table.png)

## Why it scales

![Weight-array area against model size: measured GF180 points and projections](routing-voice-chip-design/release-v1/figures/scaling-area.png)

At the measured 5.55 µm² per hardwired weight, a speech model of tens of millions of weights fits a cheap mature node today. A 1 B-parameter language model would need about 5,500 mm² at 180 nm. Assuming a 20–40× area reduction at 28 nm, it would fit in roughly 140–280 mm². Only the blue points are measured; the line and the band are projections. There is also an [energy chart](routing-voice-chip-design/release-v1/figures/scaling-energy.png).

## The idea behind it: a voice module for helmets

<table>
<tr>
<td width="40%"><a href="https://routing-module-180.vercel.app"><img src="docs/media/helmet-v4-hero.jpg" alt="RoutingModule-180 helmet render"></a></td>
<td width="60%"><a href="https://routing-module-180.vercel.app"><img src="docs/media/helmet-system.jpg" alt="From spoken intent to physical action"></a></td>
</tr>
</table>

RouteVoice started as the speech engine for **RoutingModule-180**, a voice module for motorcycle helmets that runs locally, with no cloud. A rider says a command; the module recognizes it on-chip, routes it to a tool (camera, lights, music, recording, SOS), checks it against a fixed safety policy, and answers by voice.

**[routing-module-180.vercel.app](https://routing-module-180.vercel.app)** renders the helmet live in the browser and simulates one spoken command travelling through the module, stage by stage. The helmet is a design concept (Blender renders and product sheets), not a built product. The site's latency figures come from earlier host benchmarks, not from this chip.

The broader bet is that small, fixed AI models, built straight into cheap chips, can give everyday devices a voice interface: speech in, a small language model, speech out.

## Explainer video

[![Speech → Silicon explainer: The Mission, Anatomy of Moonshine, Four-Bit Codebooks, Fabric and Die Budget](docs/media/explainer-poster.jpg)](docs/media/speech-to-silicon-explainer.mp4)

**[▶ Watch: Speech → Silicon (5 min, vertical)](docs/media/speech-to-silicon-explainer.mp4)**

Eight chapters: the mission, inside Moonshine, the Taalas trick, four-bit codebooks, the RTL engine, synthesis, the weight fabric and die budget, and an honest scorecard. I made it on 29 Sep 2026, before the engine was routed, so its scorecard shows the project at that date. The tables above are current.

## What is not done

- **No silicon.** Nothing has been fabricated or signed off by a foundry.
- **The full chip is not integrated.** The two-die top level is partly placed and routed; full-chip DRC/LVS, timing and IR drop are still open.
- **Area.** The recognizer's mutable state is synthesized as flip-flops (about 1,198 mm² of logic) and must move to SRAM.
- **Real-time operation** of the whole recognizer is unproven.
- **Warnings.** The engine still has max-slew, max-cap and max-fanout warnings.

Details are in [`release-v1/README.md`](routing-voice-chip-design/release-v1/README.md#what-is-not-done) and the paper's Limitations section.

## Repository map

| Path | What it is |
|---|---|
| [`routing-voice-chip-design/release-v1/`](routing-voice-chip-design/release-v1/) | **Start here:** demo, figures, signoff table, scaling data, and the scripts that make them |
| [`routing-voice-chip-design/overnight-20261014/finish-1023/`](routing-voice-chip-design/overnight-20261014/finish-1023/) | Final evidence: W10 engine routing, W11 bit-exact recognizer, W12 synthesis, W13 weight banks, W14 macros, W15 two-die integration |
| [`routing-voice-chip-design/rtl/`](routing-voice-chip-design/rtl/), [`scripts/`](routing-voice-chip-design/scripts/), [`tests/`](routing-voice-chip-design/tests/), [`physical/`](routing-voice-chip-design/physical/) | RTL sources, tooling, tests and physical-design inputs |
| [`routing-voice-chip-design/docs/`](routing-voice-chip-design/docs/), [`reports/`](routing-voice-chip-design/reports/) | Design notes, proof gates and dated audit reports |
| [`paper/`](paper/) | LaTeX source and PDF; `make-arxiv.sh` builds the arXiv bundle |
| [`OVERNIGHT-PROGRESS.md`](OVERNIGHT-PROGRESS.md) | Chronological lab log of the final push |
| [`docs/media/`](docs/media/) | Explainer video and helmet images used in this README |

Large run directories are on Hugging Face:
- [`sanjuhs/routevoice-engine-fix2-20261024`](https://huggingface.co/datasets/sanjuhs/routevoice-engine-fix2-20261024): final engine GDS and signoff runs, 97 GB;
- [`sanjuhs/routevoice-pod-final-20261022`](https://huggingface.co/datasets/sanjuhs/routevoice-pod-final-20261022): cloud workspace, 53 GB.

## How it was built

AI coding agents (Claude and Codex) did the work under my direction, using an all-open-source flow: Verilator, Yosys and OpenROAD via LibreLane, Magic, KLayout and Netgen, on the GF180MCU-D PDK. Cloud compute cost $34.82. Many paths in the evidence files are absolute paths from the original machine.

This repository is a snapshot of the RouteVoice parts of a larger private working repository, taken on 28 Oct 2026.

## License

Apache-2.0 for this repository's own code and documents. Moonshine Tiny is MIT-licensed by its authors. The GF180MCU PDK and the open EDA tools carry their own licenses.

Sanjay Prasad H S
