#!/usr/bin/env bash
# Offload old 12 Oct run outputs to the SSD with checksum verification, then remove local copies.
set -euo pipefail
SRC=$HOME/.local/state/routevoice-internal-runs/$2
DST="/Volumes/Extreme Pro Dev/routevoice-checkpoints/internal-runs-offload-20261014/$2"
LIST=$1
mkdir -p "$DST"
while read -r d; do
  [ -n "$d" ] && [ -e "$SRC/$d" ] || continue
  rsync -a "$SRC/$d" "$DST/"
  # verify: checksum dry-run must report no differences
  if [ -z "$(rsync -anc --out-format='%n' "$SRC/$d" "$DST/")" ]; then
    rm -rf "$SRC/$d"; echo "OFFLOADED $d"
  else
    echo "VERIFY-FAILED $d (kept local)"
  fi
done < "$LIST"
df -h / | tail -1
