#!/bin/bash
set -euo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash
W=/workspace/rv/overnight-20261014/projection-complete
cd "$W"
export TMPDIR="$W/tmp" OMP_NUM_THREADS=10 OPENBLAS_NUM_THREADS=1
# Existing pod only, max10+2 internal threads, four-hour hard bound.
set +e
timeout --signal=TERM --kill-after=30 14400 nix-shell /workspace/rv/tools/librelane/shell.nix --run "librelane --manual-pdk --pdk gf180mcuD --pdk-root /workspace/rv/overnight-20261014/fabric-k64/pdks --design-dir $W --run-tag complete-v1 --jobs 10 $W/configs/complete.json" >logs/physical-v1.log 2>&1
rc=$?
printf '%s\n' "$rc" >logs/physical-v1.exit
exit "$rc"
