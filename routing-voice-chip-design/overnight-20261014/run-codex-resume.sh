#!/usr/bin/env bash
# Usage: run-codex-resume.sh <name> <session-id> <guidance.md> — resumes a Codex worker session with new lead guidance
set -uo pipefail
cd "$(dirname "$0")/.."
name="$1"; sid="$2"; guide="$3"
echo "=== Codex worker $name RESUMED $(date) with $guide ===" | tee -a "overnight-20261014/logs/codex-$name.log"
codex exec resume "$sid" - < "$guide" 2>&1 | tee -a "overnight-20261014/logs/codex-$name.log"
echo "=== Codex worker $name exited $(date) code ${PIPESTATUS[0]} ===" | tee -a "overnight-20261014/logs/codex-$name.log"
