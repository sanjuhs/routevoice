#!/usr/bin/env bash
# Full local LibreLane flow (synthesis -> signoff) for the pipelined engine; same settings as closure pass 2.
cd /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/..; source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh; export NIX_BUILD_SHELL=/bin/bash
s=$(date +%s)
nix-shell tools/librelane/shell.nix --run "export TMPDIR=/Users/sanju/rvssd/pipe-local/tmp OMP_NUM_THREADS=12 PYTHONDONTWRITEBYTECODE=1; nice -n 5 python3 /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/finish-1023/w10-route/librelane_pi.py --condensed --log-level WARNING --manual-pdk --pdk gf180mcuD --pdk-root /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/pdks --design-dir /Users/sanju/rvssd/pipe-local --run-tag pipe --jobs 12 /Users/sanju/rvssd/pipe-local/inputs/full-pipe-local.json"
echo "exit=$? wall_s=$(( $(date +%s)-s ))"
