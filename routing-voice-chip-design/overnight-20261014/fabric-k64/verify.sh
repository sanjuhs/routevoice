#!/bin/bash
set -euo pipefail
w2b_dir="$(cd "$(dirname "$0")" && pwd)"
export TMPDIR="$w2b_dir/tmp"
sim_jobs="${W2B_SIM_JOBS:-3}"
export OMP_NUM_THREADS="$sim_jobs" OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS="$sim_jobs"
cd "$w2b_dir"
variant="${1:?variant required}"
mode="${2:-full}"
tbfile="tb/${variant}.sv"
if [[ "$mode" == trace ]]; then tbfile="tb/trace_${variant}.sv"; fi
files=(hf/HardFloat_primitives.v hf/HardFloat_rawFN.v hf/isSigNaNRecFN.v hf/fNToRecFN.v hf/recFNToFN.v hf/iNToRecFN.v hf/mulRecFN.v hf/addRecFN.v hf/ARM-VFPv2/HardFloat_specialize.v rtl/engine.sv rtl/taalas_fp32_affine.sv rtl/taalas_projection_affine.sv rtl/metadata.sv rtl/index_fabric.sv "rtl/rv_k64_${variant}.sv" "$tbfile")
verilator_args=(--binary --timing)
if [[ "$mode" == trace ]]; then verilator_args+=(--trace); fi
nice -n 10 verilator "${verilator_args[@]}" --top-module tb -Wno-fatal -j "$sim_jobs" --Mdir "sim-${variant}-${mode}" -o sim -Ihf -Ihf/ARM-VFPv2 "${files[@]}" > "logs/${variant}-${mode}-compile.log" 2>&1
nice -n 10 "sim-${variant}-${mode}/sim" > "logs/${variant}-${mode}-simulation.log" 2>&1
cat "logs/${variant}-${mode}-simulation.log"
