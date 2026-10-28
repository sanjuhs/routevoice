#!/bin/bash
set -euo pipefail
w2b_dir="$(cd "$(dirname "$0")" && pwd)"
repo_dir="$(cd "$w2b_dir/../.." && pwd)"
export TMPDIR="$w2b_dir/tmp" XDG_CACHE_HOME="$w2b_dir/cache" PYTHONDONTWRITEBYTECODE=1
export NIX_BUILD_SHELL=/bin/bash
export OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=3 NUMEXPR_NUM_THREADS=1
export W2B_CONFIG="$w2b_dir/configs/${1:?variant required}.json"
export W2B_PDK="$w2b_dir/pdks" W2B_DIR="$w2b_dir" W2B_TAG="${1}-${2:-v1}"
cd "$w2b_dir"
exec nice -n 10 nix-shell "$repo_dir/tools/librelane/shell.nix" --run 'export TMPDIR="$W2B_DIR/tmp"; export OMP_NUM_THREADS=3; librelane --condensed --log-level WARNING --manual-pdk --pdk gf180mcuD --pdk-root "$W2B_PDK" --design-dir "$W2B_DIR" --run-tag "$W2B_TAG" --jobs 3 "$W2B_CONFIG"'
