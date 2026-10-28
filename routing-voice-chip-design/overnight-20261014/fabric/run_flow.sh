#!/bin/bash
set -euo pipefail
fabric_dir="$(cd "$(dirname "$0")" && pwd)"
repo_dir="$(cd "$fabric_dir/../.." && pwd)"
export TMPDIR="$fabric_dir/tmp"
export XDG_CACHE_HOME="$fabric_dir/cache"
export PYTHONDONTWRITEBYTECODE=1
export NIX_BUILD_SHELL=/bin/bash
export OMP_NUM_THREADS=${W2_NUM_THREADS:-8} OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=${W2_NUM_THREADS:-8} NUMEXPR_NUM_THREADS=1
export _OPENLANE_MAX_CORES=${W2_NUM_THREADS:-8}
export W2_CONFIG="${W2_CONFIG_PATH:-$fabric_dir/configs/${1:?variant required}.json}"
export W2_PDK="$fabric_dir/pdks"
export fabric_dir
export W2_RUNS="$fabric_dir/runs"
export W2_TAG="${1}-${2:-v1}"
cd "$fabric_dir"
exec nice -n 10 nix-shell "$repo_dir/tools/librelane/shell.nix" --run 'bash "$fabric_dir/flow_entry.sh"'
