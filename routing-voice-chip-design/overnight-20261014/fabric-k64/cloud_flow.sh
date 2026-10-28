#!/bin/bash
# Lead-operated only. Does not create, rent, or contact any cloud resource.
set -euo pipefail
w2b_dir="$(cd "$(dirname "$0")" && pwd)"
export TMPDIR="$w2b_dir/tmp" XDG_CACHE_HOME="$w2b_dir/cache" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=6 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=6 NUMEXPR_NUM_THREADS=1
cd "$w2b_dir"
exec nice -n 10 librelane --manual-pdk --pdk gf180mcuD --pdk-root "$w2b_dir/pdks" --design-dir "$w2b_dir" --run-tag "${1:?variant required}-cloud" --jobs 6 "configs/$1.json"
