#!/usr/bin/env bash
cd /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design; source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh; export NIX_BUILD_SHELL=/bin/bash
mkdir -p /Users/sanju/rvssd/eco-local/tmp; s=$(date +%s)
nix-shell tools/librelane/shell.nix --run "export TMPDIR=/Users/sanju/rvssd/eco-local/tmp OMP_NUM_THREADS=12 PYTHONDONTWRITEBYTECODE=1; nice -n 5 librelane --condensed --log-level WARNING --from OpenROAD.RepairDesignPostGRT --with-initial-state /Users/sanju/rvssd/eco-local/inputs/state_02.json --manual-pdk --pdk gf180mcuD --pdk-root /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/pdks --design-dir /Users/sanju/rvssd/eco-local --run-tag eco --jobs 12 /Users/sanju/rvssd/eco-local/inputs/full-eco-local.json"
echo "exit=$? wall_s=$(( $(date +%s)-s ))"
