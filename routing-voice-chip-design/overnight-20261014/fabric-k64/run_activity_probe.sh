#!/bin/bash
set -euo pipefail
w2b_dir="$(cd "$(dirname "$0")" && pwd)"
repo_dir="$(cd "$w2b_dir/../.." && pwd)"
export W2B_DIR="$w2b_dir" TMPDIR="$w2b_dir/tmp" XDG_CACHE_HOME="$w2b_dir/cache" NIX_BUILD_SHELL=/bin/bash OMP_NUM_THREADS=1
exec nice -n 10 nix-shell "$repo_dir/tools/librelane/shell.nix" --run 'export TMPDIR="$W2B_DIR/tmp"; sta -no_splash -exit "$W2B_DIR/activity_probe.tcl"'
