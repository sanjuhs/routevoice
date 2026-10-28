#!/usr/bin/env bash
W=/workspace/rv/overnight-20261014/engine-buffered
while pgrep -f "^gate-activity/sim" >/dev/null; do sleep 10; done
cp $W/evidence/array_port-mapped-speech.saif /workspace/rv/overnight-20261014/power-bufv4/bufv4-mapped-speech.saif
. /nix/var/nix/profiles/default/etc/profile.d/nix.sh; export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash
SAIF=/workspace/rv/overnight-20261014/power-bufv4/bufv4-mapped-speech.saif nix-shell /workspace/rv/tools/librelane/shell.nix --run "openroad -exit -no_splash /workspace/rv/overnight-20261014/power-bufv4/power_bufv4.tcl" > /workspace/rv/overnight-20261014/power-bufv4/saif.log 2>&1
echo "exit=$?" >> /workspace/rv/overnight-20261014/power-bufv4/saif.log
