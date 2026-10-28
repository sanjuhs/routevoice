#!/bin/bash
set -euo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash
W=/workspace/rv/overnight-20261014/projection-complete
cd "$W"
python3 scripts/check_gate_vectors.py
export TMPDIR="$W/tmp" OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
mode=${1:-trace}
netlist=${2:?netlist required}
cells=/workspace/rv/overnight-20261014/fabric-k64/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog
# GF180 hold-cell weak-strength syntax is unsupported by pod Verilator5.044.
# Exclude only that unused cell after asserting it is absent from this netlist.
if grep -Eq 'gf180mcu_fd_sc_mcu7t5v0__hold[[:space:]]' "$netlist"; then
  echo 'Cannot exclude hold model: cell is used' >&2; exit 2
fi
trace='';if [ "$mode" = trace ];then trace="--trace --trace-underscore";fi
nix-shell /workspace/rv/tools/librelane/shell.nix --run "verilator --binary --timing $trace --autoflush --top-module tb -DFUNCTIONAL -DGF180MCU_FD_SC_MCU7T5V0__HOLD_V -DGF180MCU_FD_SC_MCU7T5V0__HOLD_FUNC_V -Wno-fatal -j 2 --Mdir gate-$mode -o sim $cells/primitives.v $cells/gf180mcu_fd_sc_mcu7t5v0.v $netlist tb/bank_model.sv tb/gate_$mode.sv" >logs/gate-$mode-compile.log 2>&1
set +e
timeout --signal=TERM --kill-after=15 2400 ./gate-$mode/sim >logs/gate-$mode-simulation.log 2>&1
rc=$?
printf '%s\n' "$rc" >logs/gate-$mode.exit
exit "$rc"
