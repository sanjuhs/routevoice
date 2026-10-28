#!/bin/bash
# Supplemental official GF180 checker; run only on completed GDS.
set -euo pipefail
w2b_dir="$(cd "$(dirname "$0")" && pwd)"
variant="${1:?variant required}"
gds="${2:?completed GDS path required}"
export TMPDIR="$w2b_dir/tmp" XDG_CACHE_HOME="$w2b_dir/cache" PYTHONDONTWRITEBYTECODE=1 QT_QPA_PLATFORM=offscreen
export OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=1
mkdir -p "$w2b_dir/runs/${variant}-klayout-drc"
exec nice -n 10 python3 "$w2b_dir/pdks/gf180mcuD/libs.tech/klayout/tech/drc/run_drc.py" --path="$gds" --variant=D --topcell="rv_k64_${variant}" --run_dir="$w2b_dir/runs/${variant}-klayout-drc" --mp=1 --thr=3 --run_mode=deep --density --antenna
