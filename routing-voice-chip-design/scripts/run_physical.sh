#!/usr/bin/env bash
set -euo pipefail
export NIX_BUILD_SHELL=/bin/bash
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh ]]; then
 source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
fi
command -v nix-shell >/dev/null || { echo 'Native Nix is required; run scripts/bootstrap.sh.' >&2; exit 2; }
export PDK_ROOT="$root/pdks"
export ROUTING_CONFIG="$(cd "$(dirname "${1:?Usage: run_physical.sh config.json}")" && pwd)/$(basename "$1")"
nix-shell "$root/tools/librelane/shell.nix" --run 'librelane --pdk gf180mcuD --pdk-root "$PDK_ROOT" "$ROUTING_CONFIG"'
