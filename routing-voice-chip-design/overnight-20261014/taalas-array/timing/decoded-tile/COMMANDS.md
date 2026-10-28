# Exact reproduction

Run from repository root; maintain at least 22 GiB free on `/`. All outputs are inside this directory. DRC uses 2 threads; Magic and each Netgen run use 1 thread, with nice 10. Limit simultaneous jobs to 2 threads here.

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/build.py v1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/readback.py
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/reference.py
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/check.py v1 bank0'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/check.py v1 tile'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/extract.py'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/lvs.py'
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/dimensions.py
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'for bank_group in 0 1 2 3 4 5 6 7 8 9; do PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/partition_lvs.py "$bank_group" || break; done'
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/audit_partition.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/finalize_compositional.py
```

`lvs.py` produces the bijectively normalized full extraction and launches monolithic Netgen. The original run was manually bounded at 600 seconds, retaining outputs; the component commands are the completed proof. Each component command has a 200-second timeout. Exact nested tool arguments are in `v1/*command*.json`; hashes are in `results.json` and `v1/geometry.json`. Bank 0 was originally run by `bank_lvs.py`, which is equivalent to `partition_lvs.py 0` except for its top-cell name.
