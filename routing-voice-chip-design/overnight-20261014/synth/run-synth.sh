#!/usr/bin/env bash
cd "$(dirname "$0")"
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh; export NIX_BUILD_SHELL=/bin/bash
R=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design
/usr/bin/time -l nice -n 10 nix-shell $R/tools/librelane/shell.nix --run 'yosys -m slang -l yosys-fulltop.log fulltop.ys' > run-synth.out 2>&1
echo "EXIT $?" >> run-synth.out
