#!/bin/bash
# Pack the pod's /workspace into zstd tar parts, upload each unit to a public HF dataset, delete local parts.
set -uo pipefail
REPO=sanjuhs/routevoice-pod-final-20261022
W=/workspace
S=/workspace/hfstage
L=/workspace/upload.log
export HF_TOKEN="$(cat /root/.hf_token)"
export HF_HUB_ENABLE_HF_TRANSFER=0
log(){ echo "$(date -u +%FT%TZ) $*" | tee -a "$L"; }
O=rv/overnight-20261014
F=$O/finish-1023
# name|paths (relative to /workspace)|excludes
UNITS=(
  "w10-runs-full|$F/w10-route/runs/full|"
  "w10-runs-C|$F/w10-route/runs/C|"
  "w10-rest|$F/w10-route|--exclude=$F/w10-route/runs/full --exclude=$F/w10-route/runs/C"
  "w15-chip|$F/w15-chip|"
  "w12-synth|$F/w12-synth|"
  "misc|$F/w14-blocks $O/engine-buffered $O/fabric-k64 $O/runpod rv/tools setup.log|"
)
python3 - <<'PY' || exit 1
import os
from huggingface_hub import HfApi
HfApi().create_repo(os.environ.get('REPO','sanjuhs/routevoice-pod-final-20261022'), repo_type='dataset', private=False, exist_ok=True)
PY
python3 -c "
from huggingface_hub import HfApi
api=HfApi()
for f in ['/workspace/pod-manifest.sha256','/workspace/README-hf.md']:
    api.upload_file(path_or_fileobj=f, path_in_repo=('README.md' if f.endswith('README-hf.md') else 'pod-manifest.sha256'), repo_id='$REPO', repo_type='dataset')
" && log "uploaded manifest + README" || { log "FAIL manifest upload"; exit 1; }
for u in "${UNITS[@]}"; do
  IFS='|' read -r name paths excl <<<"$u"
  if [ -f "$W/done-$name" ]; then log "skip $name (done)"; continue; fi
  rm -rf "$S"; mkdir -p "$S/$name"
  log "pack $name"
  cd "$W"
  # shellcheck disable=SC2086
  tar $excl -cf - $paths | zstd -T12 -3 -q | split -b 8G -d -a 2 - "$S/$name/$name.tar.zst.part"
  rc=("${PIPESTATUS[@]}")
  if [ "${rc[*]}" != "0 0 0" ]; then log "FAIL pack $name rc=${rc[*]}"; exit 1; fi
  n=$(cat "$S/$name"/*.part* | zstd -dc | tar -tf - | grep -vc '/$')
  log "pack $name ok parts=$(ls "$S/$name" | wc -l) files_in_tar=$n size=$(du -sh "$S/$name" | cut -f1)"
  (cd "$S/$name" && sha256sum *.part* > "$name.parts.sha256")
  echo "$n" > "$S/$name/$name.filecount"
  python3 -c "
from huggingface_hub import HfApi
HfApi().upload_folder(folder_path='$S/$name', path_in_repo='archives/$name', repo_id='$REPO', repo_type='dataset', commit_message='Add $name')
" || { log "FAIL upload $name"; exit 1; }
  cp "$S/$name/$name.parts.sha256" "$S/$name/$name.filecount" "$W/"
  touch "$W/done-$name"; log "uploaded $name"
done
rm -rf "$S"; log "ALL-DONE"
