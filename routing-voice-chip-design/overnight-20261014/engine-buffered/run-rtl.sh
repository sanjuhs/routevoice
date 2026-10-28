#!/usr/bin/env bash
set -euo pipefail
W=/workspace/rv/overnight-20261014/engine-buffered
B=/workspace/rv/overnight-20261014/fabric-k64
cd "$W"
export TMPDIR="$W/tmp" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
verilator --binary --timing --autoflush --output-groups 0 --top-module tb -Wno-fatal -j 2 --Mdir rtl-full -o sim -I"$B/hf" -I"$B/hf/ARM-VFPv2" "$B/hf/HardFloat_primitives.v" "$B/hf/HardFloat_rawFN.v" "$B/hf/isSigNaNRecFN.v" "$B/hf/fNToRecFN.v" "$B/hf/recFNToFN.v" "$B/hf/iNToRecFN.v" "$B/hf/mulRecFN.v" "$B/hf/addRecFN.v" "$B/hf/ARM-VFPv2/HardFloat_specialize.v" rtl/engine_dup.sv "$B/rtl/taalas_fp32_affine.sv" "$B/rtl/taalas_projection_affine.sv" "$B/rtl/metadata.sv" "$B/rtl/index_fabric.sv" "$B/rtl/rv_k64_array_port.sv" tb/array_port.sv > logs/rtl-full-compile.log 2>&1
rtl-full/sim > logs/rtl-full-simulation.log 2>&1
echo 'W9-STATUS: duplicated-register RTL full regression passed' | tee evidence/rtl-full.status
