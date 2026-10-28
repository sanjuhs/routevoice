#!/bin/bash
set -euo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash
W=/workspace/rv/overnight-20261014/projection-complete
cd "$W"
export QT_QPA_PLATFORM=offscreen OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export W8_IMAGE_CONFIG="$W/runs/complete-v3/resolved.json"
export W8_IMAGE_DEF="$W/${1:?relative DEF required}"
export W8_IMAGE_OUTPUT="$W/${2:?relative PNG required}"
timeout --signal=TERM --kill-after=10 180 nix-shell /workspace/rv/tools/librelane/shell.nix --run "klayout -b -r $W/scripts/render_layout.py"
