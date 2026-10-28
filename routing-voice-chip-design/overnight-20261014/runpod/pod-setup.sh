#!/usr/bin/env bash
# Runs ON the pod: install Nix (no init), FOSSi binary cache, then realise the LibreLane shell.
set -x
export DEBIAN_FRONTEND=noninteractive
command -v rsync >/dev/null || (apt-get update -qq && apt-get install -y -qq rsync xz-utils)
if ! [ -x /nix/var/nix/profiles/default/bin/nix ]; then
  CONF=$'extra-substituters = https://nix-cache.fossi-foundation.org\nextra-trusted-public-keys = nix-cache.fossi-foundation.org:3+K59iFwXqKsL7BNu6Guy0v+uTlwsxYQxjspXzqLYQs=\nextra-experimental-features = nix-command flakes\nmax-jobs = auto'
  curl -sSfL https://artifacts.nixos.org/nix-installer | sh -s -- install linux --init none --no-confirm --extra-conf "$CONF" \
  || curl -sSfL https://install.determinate.systems/nix | sh -s -- install linux --init none --no-confirm --extra-conf "$CONF"
fi
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh 2>/dev/null || . /nix/var/nix/profiles/default/etc/profile.d/nix.sh
# no daemon running in a container: use single-user store access
export NIX_REMOTE=local
nix --version
cd /workspace/rv && NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'librelane --version; openroad -version; yosys -V' 
echo SETUP-DONE
