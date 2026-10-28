#!/usr/bin/env bash
# Native macOS/Linux flow only. No containers or cloud execution.
set -euo pipefail
export NIX_BUILD_SHELL=/bin/bash
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh ]]; then
  source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
fi
command -v nix-shell >/dev/null || { echo 'Install native Nix using scripts/install-native-nix.sh first.' >&2; exit 2; }
if [[ ! -d "$root/tools/librelane/.git" ]]; then
 git clone --branch 3.0.11 https://github.com/librelane/librelane.git "$root/tools/librelane"
fi
actual="$(git -C "$root/tools/librelane" rev-parse HEAD)"
[[ "$actual" = 33ab64861c5570d65de69295da9a46f5bad32ee3 ]] || { echo 'LibreLane revision mismatch' >&2; exit 1; }
mkdir -p "$root/pdks" "$root/reports"
export PDK_ROOT="$root/pdks"
nix-shell "$root/tools/librelane/shell.nix" --run 'set -e; librelane --version; yosys -V; openroad -version' > "$root/reports/tool-versions.txt" 2> "$root/tools/native-tool-build.log"
nix-shell "$root/tools/librelane/shell.nix" --run 'ciel enable --pdk gf180mcu 54435919abffb937387ec956209f9cf5fd2dfbee'
