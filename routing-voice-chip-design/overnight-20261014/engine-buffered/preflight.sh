#!/usr/bin/env bash
set -uo pipefail
W=/workspace/rv/overnight-20261014/engine-buffered
export TMPDIR="$W/tmp" PYTHONDONTWRITEBYTECODE=1
python3 -c 'import klayout.db, docopt; print("KLAYOUT_DRC_DEPENDENCIES_OK")'
command -v klayout
command -v openroad
command -v verilator
date -u
