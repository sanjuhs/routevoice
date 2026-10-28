#!/usr/bin/env bash
# Usage: run-codex.sh <name> <brief.md>  — runs one Codex worker, logs to logs/codex-<name>.log
set -uo pipefail
cd "$(dirname "$0")/.."
name="$1"; brief="$2"
echo "=== Codex worker $name started $(date) ==="
codex exec -C . - < "$brief" 2>&1 | tee -a "overnight-20261014/logs/codex-$name.log"
echo "=== Codex worker $name exited $(date) code ${PIPESTATUS[0]} ===" | tee -a "overnight-20261014/logs/codex-$name.log"
