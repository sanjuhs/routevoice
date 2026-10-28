#!/bin/bash
set -euo pipefail
w5_dir="$(cd "$(dirname "$0")" && pwd)"
repo_dir="$(cd "$w5_dir/../../.." && pwd)"
export TMPDIR="$w5_dir/tmp" XDG_CACHE_HOME="$w5_dir/cache" PYTHONDONTWRITEBYTECODE=1
export NIX_BUILD_SHELL=/bin/bash OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export W5_CONFIG="$w5_dir/${1:-decoder}.json" W5_DIR="$w5_dir" W5_TAG="${1:-decoder}-${2:-v1}" W5_PDK="$repo_dir/overnight-20261014/fabric-k64/pdks"
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
cd "$w5_dir"
exec nice -n 10 nix-shell "$repo_dir/tools/librelane/shell.nix" --run 'export TMPDIR="$W5_DIR/tmp"; librelane --condensed --log-level WARNING --manual-pdk --pdk gf180mcuD --pdk-root "$W5_PDK" --design-dir "$W5_DIR" --run-tag "$W5_TAG" --jobs 1 "$W5_CONFIG"'
