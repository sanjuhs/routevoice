#!/usr/bin/env bash
# Source rebuild, separate from the downloaded reference PDK.
set -euo pipefail
export NIX_BUILD_SHELL=/bin/bash
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh ]]; then
 source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
fi
command -v nix-shell >/dev/null || { echo 'Install native Nix and bootstrap tools first.' >&2; exit 2; }
export ROUTING_SOURCE_PDK_ROOT="$root/pdks-source"
mkdir -p "$ROUTING_SOURCE_PDK_ROOT"
nix-shell "$root/tools/librelane/shell.nix" --run 'ciel build --pdk gf180mcu --pdk-root "$ROUTING_SOURCE_PDK_ROOT" -j 4 54435919abffb937387ec956209f9cf5fd2dfbee'
