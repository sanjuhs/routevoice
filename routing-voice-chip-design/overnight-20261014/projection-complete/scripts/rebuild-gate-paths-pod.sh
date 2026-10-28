#!/bin/bash
set -euo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash
W=/workspace/rv/overnight-20261014/projection-complete
cd "$W"
export TMPDIR="$W/tmp" OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
python3 scripts/fix_gate_vector_paths.py >logs/gate-vector-path-fix.log 2>&1
sha256sum gate-trace/sim >evidence/gate-sim-v1-invalid.sha256
nix-shell /workspace/rv/tools/librelane/shell.nix --run 'make -C gate-trace -f Vtb.mk -j2' >logs/gate-trace-recompile-paths.log 2>&1
sha256sum gate-trace/sim >evidence/gate-sim-v2.sha256
set +e
timeout --signal=TERM --kill-after=15 1200 ./gate-trace/sim >logs/gate-trace-v2-simulation.log 2>&1
rc=$?
printf '%s\n' "$rc" >logs/gate-trace-v2.exit
if grep -Eq 'Warning|Error|readmem.*not found' logs/gate-trace-v2-simulation.log; then
 printf '%s\n' 'Rejected simulator warnings/errors' >logs/gate-trace-v2-rejection.txt
 exit 2
fi
exit "$rc"
