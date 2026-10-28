# RouteVoice

**A speech-recognition transformer compiled into hardwired-weight logic, with its compute engine laid out in open 180 nm silicon.**

RouteVoice takes Moonshine Tiny, an open 34 M-parameter speech recognizer, and builds it as hardware where the weights are fixed in the chip instead of fetched from memory. Each transformer weight is a 4-bit index into a 16-entry codebook shared by 64 weights, and each index is set by Via1 positions in a mask-programmed array. The approach follows ideas in public patent documents from Taalas; this is an independent implementation.

![Weight-bank close-up: the irregular amber via pattern over a regular cell grid encodes the stored weights](routing-voice-chip-design/release-v1/figures/layout/weight-bank-zoom0400.png)

## What is proven

| Claim | Evidence |
|---|---|
| The full recognizer RTL turns real audio into the right text, **bit-exact** with the frozen model: "Switch on the lights", "Plant present.", "Seasonable." (18/18 internal outputs each, about 310 M simulated clocks) | [`release-v1/demo/`](routing-voice-chip-design/release-v1/demo/), `finish-1023/w11-taalas-e2e/` |
| Weight storage drops from 28.6 MB to 17.5 MB with zero mismatches | W11 `RESULTS.md` |
| The 1280×320 projection engine (409,600 MACs) is routed in GF180MCU and **passes every open signoff check**: DRC 0 (routing, Magic, KLayout), LVS unique match, XOR 0, antenna 0 | [signoff table](routing-voice-chip-design/release-v1/figures/signoff-table.md) |
| It meets a 150 ns clock in all 9 PVT/RC corners; routed power with real-speech activity is 0.188 W (287 pJ/MAC) | `finish-1023/w10-route/pipe2/` |
| All 98 weight matrices exist as mask-programmed banks: 31.5 M four-bit weights in 174.7 mm², 81 banks DRC-clean | `finish-1023/w13-arrays/` |

## What is not done

- **No silicon.** Nothing has been fabricated or foundry-signed-off.
- **The full chip is not integrated.** The two-die top level is partly placed and routed; full-chip DRC/LVS, timing and IR drop are open.
- **Area.** The recognizer's mutable state is synthesized as flip-flops (about 1,198 mm² of logic) and must move to SRAM.
- **Real-time operation** of the whole recognizer is unproven.
- The engine still has max-slew, max-cap and max-fanout warnings.

Details: [`release-v1/README.md`](routing-voice-chip-design/release-v1/README.md#what-is-not-done) and the paper's Limitations section.

## Why it matters

At the measured 5.55 µm² per hardwired weight, a speech model of tens of millions of weights fits a cheap mature node today. [The scaling chart](routing-voice-chip-design/release-v1/figures/scaling-area.png) projects larger models. A 1 B-parameter LM would need about 5,500 mm² at 180 nm. Assuming a 20–40× area reduction, it would fit roughly 140–280 mm² at 28 nm; that figure is a projection, not a measurement.

## Start here

- **Release package and demo:** [`routing-voice-chip-design/release-v1/`](routing-voice-chip-design/release-v1/)
- **Paper:** [`paper/RouteVoice-paper-draft.pdf`](paper/RouteVoice-paper-draft.pdf) (LaTeX source in [`paper/`](paper/))
- **Lab log:** [`OVERNIGHT-PROGRESS.md`](OVERNIGHT-PROGRESS.md)
- **Large run directories (Hugging Face):** [`sanjuhs/routevoice-engine-fix2-20261024`](https://huggingface.co/datasets/sanjuhs/routevoice-engine-fix2-20261024) (final engine GDS and signoff runs), [`sanjuhs/routevoice-pod-final-20261022`](https://huggingface.co/datasets/sanjuhs/routevoice-pod-final-20261022) (cloud workspace)

## How it was built

The design was carried out by AI coding agents (Claude and Codex) under my direction, with an all-open-source flow: Verilator, Yosys/OpenROAD via LibreLane, Magic, KLayout and Netgen on the GF180MCU-D PDK. Cloud compute cost $34.82. Many paths in the evidence files are absolute paths from the original machine.

This repository is a snapshot of the RouteVoice parts of a larger private working repository, taken on 28 Oct 2026.

## License

Apache-2.0 for this repository's own code and documents. Moonshine Tiny is MIT-licensed by its authors; the GF180MCU PDK and the open EDA tools carry their own licenses.

Sanjay Prasad H S
