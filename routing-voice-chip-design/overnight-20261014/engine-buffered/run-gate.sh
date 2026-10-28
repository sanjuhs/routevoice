#!/usr/bin/env bash
set -euo pipefail
W=/workspace/rv/overnight-20261014/engine-buffered
cd "$W"
export TMPDIR="$W/tmp" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mode="${1:?full or activity}"; netlist="${2:?netlist}"
cells=/workspace/rv/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog
trace=(); bench=tb/gate_array_port.sv
if [[ "$mode" == activity ]]; then
 trace=(--trace-saif --trace-underscore --trace-depth 2)
 bench=tb/activity_array_port.sv
fi
if grep -Eq 'gf180mcu_fd_sc_mcu7t5v0__hold[[:space:](]' "$netlist"; then
 echo 'Cannot exclude an instantiated hold cell' >&2
 exit 1
fi
sha256sum "$netlist" "$bench" "$cells/primitives.v" "$cells/gf180mcu_fd_sc_mcu7t5v0.v" /workspace/rv/overnight-20261014/fabric-k64/rtl/index_fabric.sv > "evidence/gate-$mode-inputs.sha256"
verilator --binary --timing --autoflush --output-groups 0 "${trace[@]}" --top-module tb -DFUNCTIONAL -DGF180MCU_FD_SC_MCU7T5V0__HOLD_V -DGF180MCU_FD_SC_MCU7T5V0__HOLD_FUNC_V -Wno-fatal -j 4 --Mdir "gate-$mode" -o sim "$cells/primitives.v" "$cells/gf180mcu_fd_sc_mcu7t5v0.v" "$netlist" "$bench" /workspace/rv/overnight-20261014/fabric-k64/rtl/index_fabric.sv > "logs/gate-$mode-compile.log" 2>&1
if [[ "$mode" == activity ]]; then
 while [[ ! -f evidence/gate-full.status ]]; do sleep 10; done
fi
"gate-$mode/sim" > "logs/gate-$mode-simulation.log" 2>&1
echo "W9-STATUS: gate $mode passed" | tee "evidence/gate-$mode.status"
