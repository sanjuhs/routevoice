#!/usr/bin/env bash
set -euo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash PYTHONDONTWRITEBYTECODE=1
W=/workspace/rv/overnight-20261014/engine-buffered
export TMPDIR="$W/tmp" OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1
exec nix-shell /workspace/rv/tools/librelane/shell.nix --run "python3 $W/watch-power.py"
