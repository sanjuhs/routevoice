#!/usr/bin/env bash
set -euo pipefail
W=/workspace/rv/overnight-20261014/engine-buffered
cd "$W"
export TMPDIR="$W/tmp" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cells=/workspace/rv/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog
verilator --lint-only --timing --top-module tb -DFUNCTIONAL -DGF180MCU_FD_SC_MCU7T5V0__HOLD_V -DGF180MCU_FD_SC_MCU7T5V0__HOLD_FUNC_V -Wno-fatal "$cells/primitives.v" "$cells/gf180mcu_fd_sc_mcu7t5v0.v" runs/buf-v2/01-yosys-synthesis/rv_k64_array_port.nl.v tb/gate_array_port.sv /workspace/rv/overnight-20261014/fabric-k64/rtl/index_fabric.sv
echo 'W9-STATUS: corrected cell-library parser check passed; not a simulation result'
