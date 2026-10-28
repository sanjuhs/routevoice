#!/bin/bash
set -eo pipefail
export TMPDIR="$fabric_dir/tmp"
extra=()
if [[ -n "${W2_FROM_STEP:-}" ]]; then extra+=(--from "$W2_FROM_STEP"); fi
if [[ -n "${W2_TO_STEP:-}" ]]; then extra+=(--to "$W2_TO_STEP"); fi
if [[ -n "${W2_INITIAL_STATE:-}" ]]; then extra+=(--with-initial-state "$W2_INITIAL_STATE"); fi
exec librelane --condensed --log-level VERBOSE --manual-pdk --pdk gf180mcuD --pdk-root "$W2_PDK" --design-dir "$fabric_dir" --run-tag "$W2_TAG" --jobs "${W2_NUM_THREADS:-8}" "${extra[@]}" "$W2_CONFIG"
