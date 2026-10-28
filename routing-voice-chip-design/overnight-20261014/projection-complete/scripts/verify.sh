#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export TMPDIR="$PWD/tmp" OMP_NUM_THREADS=2
SOURCE=../fabric-k64
verilator --binary --timing --top-module tb -Wno-fatal -j 2 --Mdir sim-full -o sim -I"$SOURCE/hf" -I"$SOURCE/hf/ARM-VFPv2" -f configs/sim-files.f >logs/rtl-compile.log 2>&1
./sim-full/sim >logs/rtl-simulation.log 2>&1
cat logs/rtl-simulation.log
