# Routing Voice Chip Design

Three-die, 180 nm speech-to-text research using the existing **Moonshine Tiny Streaming English** model. Execution is **local and native**: no Runpod or Docker. Sub-watt real-time transcription is the acceptance target, not an achieved result.

See [STATUS.md](STATUS.md) for measured results and the remaining installation gate.

## Scope and current evidence

The original project is preserved in GitHub commit `dcbc968`. The private Hugging Face backup and its verification status are recorded in `reports/backup-status.json`. The original conversation is retained in `docs/source-conversation.txt` as design input, not verified evidence.

The existing 45,233,659-byte mixed-precision model remains the software reference. Do not replace it with a newly trained ternary model or claim the fixed-point implementation already reproduces its speech accuracy.

Native tools and their pins are in `tools/lock.json`. The project-local PDK root is `pdks/`. Nix itself requires the system-wide `/nix` store on macOS. LibreLane source is under `tools/librelane/`.

## Native build

```sh
./scripts/install-native-nix.sh   # first installation only; macOS administrator authentication
./scripts/bootstrap.sh          # pinned native tools and GF180MCU-D
make python
.venv/bin/python scripts/fetch_model.py
.venv/bin/python scripts/reproduce_baseline.py
make test
./scripts/run_physical.sh physical/die1.json
```

Run commands from this folder. The three parallel and three serial tile configurations are included. The native tool bootstrap must pass before physical implementation is available. An installed PDK is not a completed RTL-to-GDS run.

## Evidence gates

1. Preserve and hash the exact baseline; reproduce its software transcript.
2. Export the actual tensors and operators, quantization scales/zero points and state interfaces. Attribute every tensor to a proposed die or an explicitly unresolved category.
3. Compare real constant tiles with stored-weight implementations; prove integer arithmetic and transfer/reset behavior. Selected tile tests do not prove whole-model equivalence.
4. Validate the complete quantized graph against held-out speech using WER, latency and real-time factor. Preserve floating-point operations until evidence supports replacements.
5. Implement all operators, bounded memory, scheduling, and three-die links. Run full-model RTL/FPGA co-simulation. Select an FPGA part before producing a hardware bitstream.
6. Run synthesis, placement, routing, extraction, timing, DRC and LVS on GF180. Bind real memory and IO macros; do not silently synthesize megabytes into flip-flops.
7. Estimate power with representative switching activity and all three dies, SRAM/ROM, IO, clocks, and regulators included. Measure FPGA system power separately. Silicon sub-watt operation requires measurement or a qualified pre-silicon estimate, never inference from software timing.

The open GF180 flow does not provide an SCL PDK, approved foundry signoff, a qualified mask-ROM compiler, packaging, or manufactured chips.

## Routing experiment

`scripts/compile_tile.py` compiles frozen signed 8-bit or 9-bit matrices into balanced constant shift/add expressions with a registered ready/valid interface. It preserves full integer dot products and applies no invented scale, activation quantizer, or cache approximation. The accumulator includes the most-negative operand case. Real selected UINT8 matrices are centered using their per-output zero points into signed 9-bit coefficients; centered runtime activations also have a signed 9-bit interface. Tests exhaust all 65,536 scalar INT8 input/weight combinations and check random dot products, reset and output stalls.

The generated circuits contain no runtime coefficient port. This removes weight storage for these circuits, but does not make their arithmetic, wire capacitance, fanout, or physical area free. Reusing the same arithmetic across different fixed matrices requires coefficient selection or additional constant networks; time multiplexing alone cannot eliminate this cost.

For an individual generated tile, `scripts/synthesize.sh module_name` runs local generic synthesis and structural checks. Supplying a GF180 Liberty path as the second argument maps to actual standard cells. Generic gate counts do not establish die area, timing, or power.

`./scripts/build-pdk-from-source.sh` is the separate native source-build entry point, using Ciel's open_pdks configure/make/install path and a separate `pdks-source/` root. It requires the native tool environment first. Availability of this script does not establish that the source rebuild has passed.

`scripts/compile_serial.py` builds an alternative with nine activation-bit cycles and one acceptance cycle. It preserves the same centered integer dot product. No runtime weight fetch is introduced. The serial test checks negative sign planes, mid-computation resets, stalls, and the three actual model slices.
