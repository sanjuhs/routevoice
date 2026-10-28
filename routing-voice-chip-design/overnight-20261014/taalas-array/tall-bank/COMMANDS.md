# Tall-bank commands and evidence

Run from the repository root, with writes confined to `overnight-20261014/taalas-array/`. These commands reproduce retained output names; use a copied configuration and fresh output names to preserve this evidence. Keep at least 22 GiB free on `/`, use `nice`, and allow at most four concurrent computation threads across all jobs. Each DRC command uses two threads; extraction and transient jobs each use one. No git or cloud operation was used.

The existing `.venv/bin/python` has `klayout.db`. Native EDA executables are resolved from the existing Nix installation and their expanded commands are saved in each run directory. If needed, enter the authorized shell first:

```sh
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix
```

Actual generation and selected hierarchical DRC commands, sequentially:

```sh
df -h /
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/build.py --rows 320
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/check_drc.py --rows 320 --which timing-subbank
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/check_drc.py --rows 320 --which assembly
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/build.py --rows 1280
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/check_drc.py --rows 1280 --which timing-subbank
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/check_drc.py --rows 1280 --which assembly
```

`build.py` reuses the existing tall-array and pre2 receiver generators in memory, preserves source files, programs the real frozen indices, writes GDS, reopens it and reconstructs the logical image. Optional 1,280-row generation requires 24 GiB free at launch to reserve headroom. The four 320-row banks use striped logical addressing. Bank3 for independent LVS was exported directly from the emitted assembly:

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python - <<'PY'
from pathlib import Path
import klayout.db as k
p = Path('overnight-20261014/taalas-array/tall-bank/r320')
l = k.Layout()
l.read(str(p / 'assembly.gds'))
o = k.SaveLayoutOptions()
o.select_cell(l.cell('TALL_BANK_R320_B03').cell_index())
l.write(str(p / 'bank3.gds'), o)
PY
```

Each `r*/{assembly,timing-subbank}-drc-command.json` records the concrete KLayout invocation; matching `.log`, `.lyrdb` and `-drc.json` preserve output and counts. The reused `experiments/taalas-access/main.drc` includes the official GF180 deck with FEOL, BEOL, connectivity and off-grid enabled, 5LM/11K/MIM-B, hierarchical mode and two threads; density and antenna are excluded.

Independent original-packed-model/W2b identity, full-bank extraction, Netgen, negative control and compression receipts: [verification/COMMANDS.md](verification/COMMANDS.md).

Actual worst-column selection, capacitance extraction, geometry-resistance construction, stock-driver models, per-corner SPICE protocols, failed trials and waveforms: [timing/COMMANDS.md](timing/COMMANDS.md). Every simulated case retains its exact deck, command, source snapshots, trace hash and result. Earlier G03 candidate cases remain separate from the final full-bank-ranked G02 cases.

After all measurements finish, collect the comparison and refresh the root evidence manifest:

```sh
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/collect.py
```

The prior 64-row root handoff is archived in `baseline64/`. Its underlying evidence remains at its original paths in the parent workspace. Running the older root `scripts/collect_handoff.py` would replace the current root comparison, so use the tall-bank collector for this follow-up.
