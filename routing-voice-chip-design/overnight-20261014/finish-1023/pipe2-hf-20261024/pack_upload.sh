#!/bin/bash
# Pack ~/rvssd/pipe2-local into zstd tar parts on the SSD, upload to a public HF dataset, then verify by download.
set -uo pipefail
REPO=sanjuhs/routevoice-engine-fix2-20261024
SRC=/Users/sanju/rvssd/pipe2-local
ST=/Users/sanju/rvssd/hfstage-pipe2
B=$(cd "$(dirname "$0")" && pwd)
HFPY=/Users/sanju/.hf-cli/venv/bin/python
log(){ echo "$(date +%FT%T) $*" | tee -a "$B/upload.log"; }
cp /Users/sanju/rvssd/pipe-local/engine_local_pipe2.sv "$SRC/engine_local_pipe2.sv"
rm -rf "$SRC/tmp"
log "manifest"
(cd "$SRC" && find . -type f -print0 | sort -z | xargs -0 shasum -a 256) > "$B/manifest.sha256" || { log "FAIL manifest"; exit 1; }
log "manifest files=$(wc -l < "$B/manifest.sha256")"
rm -rf "$ST"; mkdir -p "$ST/archives/pipe2-local"
log "pack"
(cd "$(dirname "$SRC")" && tar -cf - "$(basename "$SRC")") | zstd -T10 -3 -q | split -b 8000m -d -a 2 - "$ST/archives/pipe2-local/pipe2-local.tar.zst.part"
rc=("${PIPESTATUS[@]}"); [ "${rc[*]}" = "0 0 0" ] || { log "FAIL pack rc=${rc[*]}"; exit 1; }
(cd "$ST/archives/pipe2-local" && shasum -a 256 pipe2-local.tar.zst.part* > ../../parts.sha256)
log "pack ok $(du -sh "$ST" | cut -f1) parts=$(ls "$ST/archives/pipe2-local" | wc -l)"
cp "$B/manifest.sha256" "$ST/manifest.sha256"; cp "$B/README-hf.md" "$ST/README.md"; cp "$ST/parts.sha256" "$B/parts.sha256"
"$HFPY" -c "
from huggingface_hub import HfApi
HfApi().create_repo('$REPO', repo_type='dataset', private=False, exist_ok=True)" || { log "FAIL create"; exit 1; }
log "upload"
"$HFPY" -c "
from huggingface_hub import HfApi
HfApi().upload_large_folder(folder_path='$ST', repo_id='$REPO', repo_type='dataset')" >> "$B/upload.log" 2>&1 || { log "FAIL upload"; exit 1; }
log "uploaded; verifying by download"
V=/Users/sanju/rvssd/hfverify-pipe2; rm -rf "$V"; mkdir -p "$V"
"$HFPY" -c "
from huggingface_hub import snapshot_download
snapshot_download('$REPO', repo_type='dataset', local_dir='$V')" >> "$B/upload.log" 2>&1 || { log "FAIL download"; exit 1; }
(cd "$V/archives/pipe2-local" && shasum -a 256 -c ../../parts.sha256) >> "$B/upload.log" 2>&1 || { log "FAIL parts checksum"; exit 1; }
mkdir -p "$V/x" && (cat "$V"/archives/pipe2-local/*.part* | zstd -dc | tar -C "$V/x" -xf -) || { log "FAIL extract"; exit 1; }
(cd "$V/x/pipe2-local" && shasum -a 256 -c "$B/manifest.sha256" > "$B/verify.txt" 2>&1); vrc=$?
ok=$(grep -c ': OK$' "$B/verify.txt"); bad=$(grep -vc ': OK$' "$B/verify.txt")
log "verify rc=$vrc ok=$ok bad=$bad"
[ $vrc -eq 0 ] && { rm -rf "$V" "$ST"; log "ALL-DONE verified; staging and verify copies removed"; }
