#!/bin/bash
set -euo pipefail
w2b_dir="$(cd "$(dirname "$0")" && pwd)"
variant="${1:?variant required}";netlist="${2:?gate netlist path required}"
export TMPDIR="$w2b_dir/tmp" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$w2b_dir"
cell_dir="$w2b_dir/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog"
files=("$cell_dir/primitives.v" "$cell_dir/gf180mcu_fd_sc_mcu7t5v0.v" "$netlist" "tb/gate_${variant}.sv")
if [[ "$variant" == array_port ]]; then files+=(rtl/index_fabric.sv); fi
nice -n 10 verilator --binary --timing --autoflush --top-module tb -DFUNCTIONAL -Wno-fatal -j 1 --Mdir "gate-${variant}" -o sim "${files[@]}" > "logs/${variant}-gate-compile.log" 2>&1
nice -n 10 "gate-${variant}/sim" > "logs/${variant}-gate-simulation.log" 2>&1
cat "logs/${variant}-gate-simulation.log"
