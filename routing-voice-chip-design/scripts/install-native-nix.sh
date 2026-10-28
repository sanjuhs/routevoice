#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$root/tools/installers"
installer="$root/tools/installers/nix-installer.sh"
if [[ ! -s "$installer" ]]; then
 curl --proto '=https' --tlsv1.2 -fsSL https://artifacts.nixos.org/nix-installer -o "$installer"
fi
shasum -a 256 "$installer" > "$root/reports/nix-installer-sha256.txt"
export NIX_INSTALLER_BINARY_ROOT=https://github.com/NixOS/nix-installer/releases/download/2.35.1
sh "$installer" install --no-confirm --extra-conf '
extra-substituters = https://nix-cache.fossi-foundation.org
extra-trusted-public-keys = nix-cache.fossi-foundation.org:3+K59iFwXqKsL7BNu6Guy0v+uTlwsxYQxjspXzqLYQs=
extra-experimental-features = nix-command flakes
'
