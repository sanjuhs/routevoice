# Status — 2026-09-07

**Native local setup and model-derived routing experiments are working. The complete three-die STT accelerator and sub-watt target are not yet demonstrated.**

## Preserved baseline

- GitHub snapshot: `dcbc968` on `sanjuhs/route-voice-llm-hardware-v1`.
- Private Hugging Face backup: `sanjuhs/route-voice-hardware-backup`, commit `0b39f7630620909d90857c1d84b5d95d09ad6d23`.
- Verified source bundle and existing artifact archive against remote SHA-256 and byte counts. [Backup evidence](reports/backup-status.json).
- The snapshot excludes credentials, installed dependency environments and caches. Concurrent Aditi generation after that snapshot is outside its scope and was left untouched.

## Native installation

LibreLane **3.0.11** is installed directly in `.venv/`, with its pinned source in `tools/librelane/`. The isolated package check passes. GF180MCU-D revision **54435919abffb937387ec956209f9cf5fd2dfbee** is installed under `pdks/`; 45 technology/library files passed the installation inventory. Both 7-track and 9-track libraries are present. [PDK evidence](reports/pdk-installation.json).

Nix **2.35.1** is now installed after macOS authentication. The pinned native tool environment built successfully, including LibreLane package tests (146 passed, one skipped, one expected failure). Yosys **0.62** and OpenROAD revision **dcf36133a369abc8f3c5e5738cd4d82e4903c0e0** pass startup checks. Native bootstrap was rerun successfully. No Docker or Runpod is used by these scripts. The PDK source rebuild remains unrun.

Nix needs the system `/nix` store; the model, PDK, project tools, sources and output files remain in this project folder. [Native status](reports/native-status.json).

## Model reproduction and inventory

The exact eight model-package files total **45,233,659 bytes**, with all original hashes preserved. Six ORT graphs contain **881 nodes** and **485 initializers**, totaling **44,435,754 initializer bytes**. [Tensor/operator manifest](reports/tensor-manifest.json).

The fresh local CPU smoke test transcribed the 3.819-second reference clip as:

> It wasn't until later that I realized what had actually happened.

Measured transcription time was **0.1167 seconds**, excluding **0.2024 seconds** of initialization. This is one software smoke test, not held-out WER, streaming latency, FPGA performance or power evidence. [Runtime result](reports/software-baseline.json).

## Proposed three-die split

| Die | Proposed responsibilities | Assigned initializer bytes |
|---|---|---:|
| 1 | Audio frontend and encoder blocks 0–2 | 5,839,480 |
| 2 | Encoder blocks 3–5 and adapter | 5,059,573 |
| 3 | Cross-attention K/V projection and text decoder | 33,518,465 |
| Unresolved/shared | 38 encoder constants requiring graph-cut review | 18,236 |

This is a candidate partition from graph and tensor names, not a verified executable partition or an area allocation. Every initializer remains accounted for. Die 3 includes the packaged duplicated vocabulary matrices. A shared immutable table remains a design option requiring address/scale and memory-macro validation. [Partition and assumptions](reports/three-die-partition.json).

The current graph uses floating-point operations and dynamic activation quantization. Many weight tensors are **UINT8 with per-output zero points**. Centering them can require **signed 9-bit** values. Hardware must preserve the zero-point subtraction and scales; treating these bytes as signed INT8 or ternary weights would change the model.

A hypothetical 320-value, 50-Hz boundary carries **0.512 Mbit/s at FP32**, before protocol overhead. **0.128 Mbit/s at INT8** is conditional on an accuracy-validated quantization change. Current decoder self-K/V costs **15,360 bytes per token**, and cross-K/V costs **15,360 bytes per retained encoder step**. A 100-token/80-step example alone consumes 2,764,800 bytes, before other state and scratch buffers. These are examples, not selected cache limits.

## Actual routing experiments

Three distinct 8×8 slices were extracted from encoder block 0, encoder block 3, and decoder cross-attention block 0 FFN output projections. Each source matrix is 1280×320 in ONNX K×N order. The export preserves the per-output zero points, selected coordinates, orientation and hashes.

Both implementations compute the exact **partial centered integer dot product**. They do not implement the other 1272 terms, activation quantization, floating scales, bias, normalization, dynamic attention, token decoding, or the complete model.

| Slice | Parallel cells | Parallel cell area, mm² | Bit-serial cells | Bit-serial cell area, mm² |
|---|---:|---:|---:|---:|
| Die 1 | 7,555 | 0.16573 | 3,365 | 0.07985 |
| Die 2 | 7,442 | 0.16014 | 3,267 | 0.07901 |
| Die 3 | 7,589 | 0.16522 | 3,273 | 0.07797 |

Cell counts for serial implementations should be read from [the machine-readable synthesis report](reports/mapped-synthesis.json) if regenerated. Areas are Yosys/ABC Liberty sums at the GF180 7-track TT 25°C/3.3 V corner. They exclude placement/routing, clock tree, filler/tap/decap cells, IO/pads, memories, and package overhead. These are not die areas or power estimates.

The parallel design accepts one vector per cycle when unstalled. The serial design uses nine compute cycles and one acceptance cycle. Serial processing cuts these mapped cell-area sums roughly in half; it does not prove the full dense model fits.

All **seven test methods** pass, including exhaustive 65,536 INT8 scalar combinations, wider centered-operand limits, actual model slices, output backpressure, and resets during serial computation. All six mapped netlists pass structural checks. [RTL checks](reports/rtl-tests.txt).

All six parallel/serial physical configurations load successfully against the installed PDK. [Configuration evidence](reports/physical-config-check.json).

The first native serial-tile flow now completes synthesis, placement, clock-tree construction, detailed routing, extraction, timing analysis and GDS generation. Magic DRC, Netgen LVS, layout XOR and route antenna checks report zero errors. Setup and hold violation counts are zero, but **39 max-slew and one max-cap violations remain**. **KLayout DRC did not run**, because its runset is unset. This is not a signoff-clean result. The flow used the PDK default 5.00 V nominal corner, unlike the earlier 3.30 V standalone synthesis comparison. No workload-based power claim is made. [Native physical evidence](reports/native-physical-smoke.json).

## Remaining work

1. Run and audit the PDK source rebuild; resolve the first native flow’s electrical-limit violations and missing KLayout DRC coverage before extending the physical result to the other slices.
2. Compare serial/folded constant networks against concrete ROM-backed implementations using available macros, traffic, switching activity and physical area.
3. Resolve the encoder graph cut, dynamic quantization, nonlinearity/attention operators, SRAM allocation, decoder bounds, shared tables and three-die links.
4. Validate full-model numerical equivalence and held-out speech accuracy; choose explicit latency, WER and real-time operating points.
5. Select the FPGA part and board, create the board wrapper/constraints, and run the complete model on FPGA hardware.
6. Close extracted physical timing and power for all three dies, IO and memory. Demonstrate the sub-watt system budget with defensible power evidence.

The attachment is a conversation, not a research-paper PDF. Its area/power numbers are hypotheses. A separate paper has not been supplied in this task.

## Follow-up verification

The seven RTL tests and reference transcription passed again on 2026-09-07. See [proof gates](docs/proof-gates.md) for the bounded path from the partial tile to complete-model co-simulation, FPGA validation and ASIC power evidence.
