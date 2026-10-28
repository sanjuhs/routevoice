#!/bin/bash
# Pack the antenna close-out run (runs/pipe2-ant + its config and log) into zstd tar parts, add it to the existing
# public HF dataset under archives/pipe2-ant/, then verify by downloading just those files back.
set -uo pipefail
REPO=sanjuhs/routevoice-engine-fix2-20261024
SRC=/Users/sanju/rvssd/pipe2-local
ST=/Users/sanju/rvssd/hfstage-pipe2-ant
B=$(cd "$(dirname "$0")" && pwd)
HFPY=/Users/sanju/.hf-cli/venv/bin/python
ITEMS="runs/pipe2-ant inputs/full-pipe2-ant-local.json flow-ant.log"
log(){ echo "$(date +%FT%T) $*" | tee -a "$B/upload.log"; }
log "secret scan"
(cd "$SRC" && grep -rIlE 'hf_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{30,}|rpa_[A-Za-z0-9]{20,}' $ITEMS) && { log "FAIL secret scan hit"; exit 1; }
log "manifest"
(cd "$SRC" && find $ITEMS -type f -print0 | sort -z | xargs -0 shasum -a 256) > "$B/manifest-pipe2-ant.sha256" || { log "FAIL manifest"; exit 1; }
log "manifest files=$(wc -l < "$B/manifest-pipe2-ant.sha256")"
rm -rf "$ST"; mkdir -p "$ST/archives/pipe2-ant"
log "pack"
(cd "$SRC" && tar -cf - $ITEMS) | zstd -T10 -3 -q | split -b 8000m -d -a 2 - "$ST/archives/pipe2-ant/pipe2-ant.tar.zst.part"
rc=("${PIPESTATUS[@]}"); [ "${rc[*]}" = "0 0 0" ] || { log "FAIL pack rc=${rc[*]}"; exit 1; }
(cd "$ST/archives/pipe2-ant" && shasum -a 256 pipe2-ant.tar.zst.part* > ../../parts-pipe2-ant.sha256)
log "pack ok $(du -sh "$ST" | cut -f1) parts=$(ls "$ST/archives/pipe2-ant" | wc -l)"
cp "$B/manifest-pipe2-ant.sha256" "$ST/"; cp "$ST/parts-pipe2-ant.sha256" "$B/"; cp "$B/README-hf.md" "$ST/README.md"
log "upload"
"$HFPY" -c "
from huggingface_hub import HfApi
HfApi().upload_large_folder(folder_path='$ST', repo_id='$REPO', repo_type='dataset')" >> "$B/upload.log" 2>&1 || { log "FAIL upload"; exit 1; }
log "uploaded; verifying by download"
V=/Users/sanju/rvssd/hfverify-pipe2-ant; rm -rf "$V"; mkdir -p "$V"
"$HFPY" -c "
from huggingface_hub import snapshot_download
snapshot_download('$REPO', repo_type='dataset', local_dir='$V', allow_patterns=['archives/pipe2-ant/*','parts-pipe2-ant.sha256','manifest-pipe2-ant.sha256','README.md'])" >> "$B/upload.log" 2>&1 || { log "FAIL download"; exit 1; }
(cd "$V/archives/pipe2-ant" && shasum -a 256 -c ../../parts-pipe2-ant.sha256) >> "$B/upload.log" 2>&1 || { log "FAIL parts checksum"; exit 1; }
mkdir -p "$V/x" && (cat "$V"/archives/pipe2-ant/*.part* | zstd -dc | tar -C "$V/x" -xf -) || { log "FAIL extract"; exit 1; }
(cd "$V/x" && shasum -a 256 -c "$B/manifest-pipe2-ant.sha256" > "$B/verify.txt" 2>&1); vrc=$?
ok=$(grep -c ': OK$' "$B/verify.txt"); bad=$(grep -vc ': OK$' "$B/verify.txt")
log "verify rc=$vrc ok=$ok bad=$bad"
[ $vrc -eq 0 ] && { rm -rf "$V" "$ST"; log "ALL-DONE verified; staging and verify copies removed"; }
