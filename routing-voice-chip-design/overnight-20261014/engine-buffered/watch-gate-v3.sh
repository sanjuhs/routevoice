#!/usr/bin/env bash
set -euo pipefail
W=/workspace/rv/overnight-20261014/engine-buffered
cd "$W"
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh
export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash PYTHONDONTWRITEBYTECODE=1
while true; do
 if [[ ! -d runs/buf-v3 ]]; then sleep 5; continue; fi
 state=$(find runs/buf-v3 -path '*-yosys-synthesis/state_out.json' -print -quit)
 if [[ -n "$state" ]]; then break; fi
 if [[ -f evidence/flow-buf-v3.exit ]]; then exit 1; fi
 sleep 20
done
synth=$(dirname "$state")
python3 fanout.py "$synth/rv_k64_array_port.nl.v.json" > evidence/synthesis-fanout.json
echo 'W9-STATUS: mapped fanout collected'
nix-shell /workspace/rv/tools/librelane/shell.nix --run "bash $W/run-gate.sh full $W/$synth/rv_k64_array_port.nl.v"
nix-shell /workspace/rv/tools/librelane/shell.nix --run "bash $W/run-gate.sh activity $W/$synth/rv_k64_array_port.nl.v"
