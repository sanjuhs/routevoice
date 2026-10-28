#!/usr/bin/env bash
# Mirror overnight workspace + progress file to the SSD every 20 minutes (excludes PDK copies and huge run dirs' tmp files).
R=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1
DST="/Volumes/Extreme Pro Dev/routevoice-checkpoints/overnight-20261014"
while true; do
  if [ -d "/Volumes/Extreme Pro Dev" ]; then
    rsync -a --exclude 'pdks/' --exclude '*/tmp/' "$R/routing-voice-chip-design/overnight-20261014/" "$DST/workspace/" 2>>"$DST/backup-errors.log"
    cp "$R/OVERNIGHT-PROGRESS.md" "$R/routing-voice-chip-design/AGENTS.md" "$DST/" 2>/dev/null
    echo "$(date '+%F %T') mirrored" >> "$DST/backup.log"
  fi
  sleep 1200
done
