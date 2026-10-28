#!/bin/bash
set -euo pipefail
w2b_dir="$(cd "$(dirname "$0")" && pwd)"
v="${1:?variant required}"
netlist="${2:-runs/${v}-v2/06-yosys-synthesis/rv_k64_${v}.nl.v}"
export TMPDIR="$w2b_dir/tmp" OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=2
cd "$w2b_dir"
cell_dir="$w2b_dir/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog"
files=("$cell_dir/primitives.v" "$cell_dir/gf180mcu_fd_sc_mcu7t5v0.v" "$netlist" "tb/activity_${v}.sv")
if [[ "$v" == array_port ]]; then files+=(rtl/index_fabric.sv); fi
nice -n 10 verilator --binary --timing --autoflush --trace-saif --trace-underscore --trace-depth 2 --top-module tb -DFUNCTIONAL -Wno-fatal -j 2 --Mdir "activity-${v}" -o sim "${files[@]}" > "logs/${v}-activity-compile.log" 2>&1
nice -n 10 "activity-${v}/sim" > "logs/${v}-activity-simulation.log" 2>&1
cat "logs/${v}-activity-simulation.log"
