#!/usr/bin/env bash
set -euo pipefail
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash PYTHONDONTWRITEBYTECODE=1
W=/workspace/rv/overnight-20261014/engine-buffered
export TMPDIR="$W/tmp"
exec python3 "$W/finish.py"
