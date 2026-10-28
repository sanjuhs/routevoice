# W6 reproduction

Run from the repository directory. Writes go only under this W6 workspace. The retained output directories are immutable revisions: use a fresh `--revision` for another build. All jobs use one thread, `nice`, and check at least 22 GiB free before starting.

The commands below are the historical invocations for the retained revisions. For a new run, choose a fresh revision name and update the corresponding DRC directory.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/scripts/build.py --rows 64 --revision v2
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/scripts/build.py --rows 1280 --revision v2
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/scripts/drc.py r64-v2'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/scripts/drc.py r1280-v2'
```

The exact KLayout argv arrays are in each revision's `drc-command.json`; command stdout is in the root build/DRC logs. `scripts/build-v1.py` and `r64-v1/` retain the first failed geometry. Revision2 shifts the receiver origin right0.09um to preserve0.28um Metal3 spacing and moves the lower ground-via row up0.4um to meet Metal4 enclosure. It changes no model index or device dimensions.

Full extraction/reference/Netgen commands and independent source image audit are under [verification/](verification/), each including the actual invoked argv and input hashes. New SPICE commands/decks/extraction and finite-window scope are under [timing/COMMANDS.md](timing/COMMANDS.md). The W5/October area baselines are snapshotted with hashes in [baseline/manifest.json](baseline/manifest.json).

Selected DRC includes GF180 FEOL, BEOL, connectivity and off-grid. Density/antenna and foundry signoff remain excluded. No cloud or git commands are used.

Small external build inputs are also preserved as `baseline/08-indices.npy`, `09-array-generate_layout.py` and `10-receiver-generate_layout.py`. The generator reads their original source paths; compare those files against the retained SHA256 values before reproducing a run. These snapshots were captured after construction; independent GDS readback and LVS tie the delivered layout to the original packed model image.

## Retained compressed evidence

The full-bank native extraction and four idle SPICE exports are retained as lossless `.gz` files. [Native extraction compression](verification/r1280-v2/native-ext-compression.json) and [SPICE compression](verification/r1280-v2/spice-evidence-compression.json) record the original and archive paths, sizes, SHA256 values and independent decompression checks. The [64-row archival receipt](verification/r64-v2/slice-evidence-compression.json) covers its native extraction and four SPICE exports. Local timing extraction and cropped-layout archives have corresponding receipts under [timing](timing/). Historical execution receipts intentionally retain the paths actually used.

For a rerun, first establish sufficient free space beyond the 22 GiB floor, then decompress the required archive to a fresh path inside this W6 workspace and verify its raw SHA256 against the receipt. Do not overwrite retained artifacts or assume the compressed path was used by an earlier command. The capacitance export can be read as a gzip stream.

The guarded TT sensitivity ended with native return code -15 after the 22.2 GiB disk reserve triggered. Its [guard receipt](timing/r1280-g09-fullcontrol-guarded/typical-120ns-s32/watchdog-extension.json) preserves the bounded runtime extension, owned-process termination and parent resumption. This run has no final trace; it must not be replayed over its existing output directory.

Final ledger and manifest generation, after all worker reports are frozen:

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/scripts/summarize.py --final
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/scripts/handoff_manifest.py
```
