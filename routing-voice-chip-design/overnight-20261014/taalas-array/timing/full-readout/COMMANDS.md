Run from repository root, with active work on internal filesystem. All generated outputs stay here.

```sh
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/full-readout/build.py > overnight-20261014/taalas-array/timing/full-readout/build.log 2>&1'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/full-readout/check.py'
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/full-readout/finalize.py
```

`drc-command.json` records the exact native KLayout invocation, pinned reused GF180 deck, top cell, deep hierarchical mode and two-thread cap. The check has a 420-second execution cap and preserves a timeout instead of granting pass credit. Generation and DRC launches assert at least 22 GiB free; observed free space during DRC was 27 GiB.

The source parent GDS hash and index image hash are recorded in `geometry.json`. `build.py` rereads the emitted 147.9 MB GDS and reconstructs every selection from actual programmed Via1 positions. It validates that the shared base has removed exactly the source programmed mask connections/OPEN labels before inserting each new image. This is mask readback, not complete transistor LVS.
