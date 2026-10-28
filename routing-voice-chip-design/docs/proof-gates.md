# What the experiment proves and the next proof gates

Evidence reviewed 2026-09-07. Native local execution only; no Docker or Runpod.

The present result proves that three small fixed-weight integer slices match their reference arithmetic and that one serial slice can be implemented through a native GF180 RTL-to-GDS flow. It does not demonstrate a complete speech recognizer in hardware, a three-die area fit, production signoff, or a sub-watt system.

The 18,236-byte entry in the partition report is 38 unresolved/shared encoder constants. It is not the model size or evidence of hardware feasibility. The six graphs have 44,435,754 initializer bytes. If “18K” means 180 nm, that is a fabrication process dimension, not a success criterion.

## Fastest useful progression

1. **Complete projection:** replace the 8×8 partial calculation with one complete 1280×320 projection from the existing model. Preserve input zero points, per-output weight zero points, accumulator bounds, output scaling and bias. Compare against the original graph on recorded real activations plus boundary cases. Report numerical error separately for integer arithmetic and floating-point conversion. Compare actual mapped area/latency for constant networks and a folded implementation; do not extrapolate die fit from the tiny slice alone.
2. **Complete model co-simulation:** keep a working software reference, substitute validated hardware operators progressively, and implement all remaining operators and persistent state. Resolve the 38 constants and prove the graph cuts. Include reset, variable audio length, backpressure, cache bounds and die-link traffic. A hybrid run validates the replaced operators only; explicitly label remaining software operations.
3. **Accuracy and capacity gate:** run a held-out, human speech corpus with clean/noisy cases and an unchanged reference. Record WER, utterance completion, streaming latency, peak memory, link traffic and sustained real-time factor. Select explicit acceptable WER degradation and latency targets before accepting results. Check the full weight storage, KV caches, scratch memory and IO, including the heavily loaded decoder die.
4. **FPGA gate:** select a concrete FPGA and supported toolchain after resource estimates. Add clock/reset, host/audio interfaces and constraints; close timing and run full inference on recorded and live audio. Compare transcripts and intermediate tensors to the same reference. Report any host-side work. Cloud FPGA requires a board-specific implementation and deployment image; a GDS file cannot be loaded into it.
5. **180 nm energy/physical gate:** implement the three complete dies and memories, characterize die links and IO, use representative switching activity with extracted parasitics, and sum compute, SRAM/ROM, clocks, IO and applicable system overhead at the selected voltage/clock. Close all electrical checks. FPGA power is a measurement of the FPGA implementation, not proof of 180 nm ASIC power. Silicon measurements ultimately validate the fabricated product.

Gate 1 is the immediate scalability experiment. A full PDK source rebuild is useful for tool reproducibility, but the installed prepared PDK already supports that experiment. Rebuilding tools does not resolve model mapping or establish power feasibility.

## Current limitations

- Only one 8×8 serial tile routed; the other two mapped but not routed.
- First physical flow: zero setup/hold violations and zero reported route/Magic DRC and LVS errors, but 39 slew and one capacitance violation remain. KLayout DRC did not run.
- Full flow used nominal 5 V; standalone synthesis comparison used 3.3 V. Do not combine them into one power/area operating point.
- Full PDK source rebuild has not run. Open research PDK results are not foundry production signoff.
- Seven RTL tests passed again on 2026-09-07. CPU reference transcript reproduced; see current software-baseline.json for timings. This one clip is not a WER benchmark.
- Native tools cover substantial digital implementation work, but FPGA place-and-route, appropriate memory macros, package/board design and foundry signoff need their own supported tooling and inputs.

No defensible completion date or sub-watt claim follows from the current tile. Each gate produces a concrete pass/fail result before escalating cost.
