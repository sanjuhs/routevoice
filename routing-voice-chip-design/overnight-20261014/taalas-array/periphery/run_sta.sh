#!/bin/bash
set -euo pipefail
w5_dir="$(cd "$(dirname "$0")" && pwd)"
repo_dir="$(cd "$w5_dir/../../.." && pwd)"
export TMPDIR="$w5_dir/tmp" XDG_CACHE_HOME="$w5_dir/cache" PYTHONDONTWRITEBYTECODE=1
export NIX_BUILD_SHELL=/bin/bash OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export W5_CONFIG="$w5_dir/mux128b.json" W5_DIR="$w5_dir" W5_PDK="$repo_dir/overnight-20261014/fabric-k64/pdks"
export W5_STATE="$w5_dir/runs/mux128b-v1/53-openroad-rcx/state_out.json"
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
cd "$w5_dir"
exec nice -n 10 nix-shell "$repo_dir/tools/librelane/shell.nix" --run 'export TMPDIR="$W5_DIR/tmp"; librelane --condensed --log-level WARNING --manual-pdk --pdk gf180mcuD --pdk-root "$W5_PDK" --design-dir "$W5_DIR" --run-tag mux128b-poststa --jobs 1 --only OpenROAD.STAPostPNR --override-config RUN_MCSTA=true --with-initial-state "$W5_STATE" "$W5_CONFIG"'
