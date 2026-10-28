#!/usr/bin/env bash
set -euo pipefail
W=/workspace/rv/overnight-20261014/engine-buffered
gds="${1:?completed GDS required}"
export TMPDIR="$W/tmp" XDG_CACHE_HOME="$W/cache" PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen
export PYTHONPATH="$W/pydeps:${PYTHONPATH:-}" OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1
mkdir -p "$W/runs/supplemental-klayout-drc"
cd "$W"
python3 /workspace/rv/overnight-20261014/fabric-k64/pdks/gf180mcuD/libs.tech/klayout/tech/drc/run_drc.py --path="$gds" --variant=D --topcell=rv_k64_array_port --run_dir="$W/runs/supplemental-klayout-drc" --mp=1 --thr=4 --run_mode=deep --density --antenna
