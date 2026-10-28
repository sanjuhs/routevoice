#!/usr/bin/env bash
set -euo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash
W=/workspace/rv/overnight-20261014/engine-buffered
export TMPDIR="$W/tmp" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
exec nix-shell /workspace/rv/tools/librelane/shell.nix --run "python3 $W/run-shards.py"
