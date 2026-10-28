#!/usr/bin/env bash
set -uo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash
W=/workspace/rv/overnight-20261014/engine-buffered
cd "$W"
mkdir -p tmp logs evidence
nix-shell /workspace/rv/tools/librelane/shell.nix --run "export TMPDIR=$W/tmp OMP_NUM_THREADS=12 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1; python3 $W/librelane_pi.py --condensed --log-level WARNING --from Yosys.Synthesis --with-initial-state $W/runs/buf-v1/05-yosys-jsonheader/state_out.json --manual-pdk --pdk gf180mcuD --pdk-root /workspace/rv/overnight-20261014/fabric-k64/pdks --design-dir $W --run-tag buf-v3 --jobs 12 $W/configs/array_port_buf.json" > logs/flow-buf-v3.log 2>&1
rc=$?
echo "$rc" > evidence/flow-buf-v3.exit
echo "W9-STATUS: flow buf-v3 exited $rc" >> logs/flow-buf-v3.log
exit "$rc"
