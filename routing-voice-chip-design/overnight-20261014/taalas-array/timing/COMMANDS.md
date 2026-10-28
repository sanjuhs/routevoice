All commands run from repository root. Every generated file is under `overnight-20261014/taalas-array/timing/`; installed models/PDK/specimens are read-only inputs.

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/prepare_slice.py
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'nice -n 10 klayout -b -r overnight-20261014/taalas-array/timing/generate_slice.py > overnight-20261014/taalas-array/timing/generation.log 2>&1'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 nice -n 10 python3 overnight-20261014/taalas-array/timing/check_slice.py'
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/simulate_slice.py > overnight-20261014/taalas-array/timing/simulation-bounded-klu.log 2>&1
```

`check_slice.py` writes the exact KLayout command to `drc-command.json`, runs Magic using explicit `PDK_ROOT=<repo>/pdks`, and independently compares all 8,192 extracted transistors with the actual image and W/L. Ngspice decks, logs, and waveforms are retained per corner. KLayout uses one thread; ngspice jobs run sequentially, with KLU solver. Disk free space was 31 GiB at launch; every check/simulation launch requires at least 22 GiB.

Preserved failures: `prepare_slice_failed_flat_order.py` attempted flat row-major packed decoding and failed W2b's unpacked hash. Corrected parser follows each rectangular-v1 block's declared byte offset/row/column and matches all 409,600 RTL choices. `extract-failed-pdk.log` preserves Magic's absent PDK_ROOT failure (Magic returned success but emitted no netlist). `stopped-sparse-typical-25ns/` and `stopped64rows-klu-typical-25ns/` preserve voluntarily stopped long 64-row transient attempts; neither gets pass credit. The bounded eight-address sequence follows the retained existing flow's coverage and contains both states and alternating states on the maximum-load column.

Joined-bank follow-up (actual routes, parent geometry revision 2):

```sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 nice -n 10 python3 overnight-20261014/taalas-array/timing/check_joined.py joined-bank0-v2'
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/qualify_joined.py joined-bank0-v2
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/simulate_joined.py joined-bank0-v2 > overnight-20261014/taalas-array/timing/joined-bank0-v2/simulation.log 2>&1
```

`joined-bank0-v1/` preserves the first joined GDS and 129 V2.3b DRC failures. The parent added missing Metal2 landings and supplied revision 2; its 0-marker DRC, flattened extracted graph, original node names and explicit port promotion are retained in `joined-bank0-v2/`. `qualify_joined.py` compares all 8,704 device terminals and dimensions to independent expected actual-mask and receiver tuples, allowing source/drain interchange. It asserts exactly one existing extracted node for every intended port; the port view changes only the `.subckt` declaration and no electrical connections.

Independent joined-bank Netgen LVS and negative control:

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/canonicalize_joined.py
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/netgen_joined.py'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/negative_joined.py'
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/finalize_joined.py
```

Netgen's first joined-bank run failed top-level pin-name matching while device classes matched. Preserved files start `first-prefix-`. A checked bijection removes hierarchical name prefixes from 4,454 distinct existing nodes for the LVS-only view; it neither merges nodes nor changes devices. `lvs-node-bijection.json` contains the map and hashes. The second native comparison matches uniquely without a property-error summary. The negative reference doubles one NMOS width and triggers a property error. Netgen also prints topology “Circuits match uniquely” for this negative, so topology matching alone is insufficient. The first negative analyzer incorrectly required absence of the topology match phrase; its false-negative result is preserved, and the corrected analyzer checks the property error directly. No electrical or layout source was changed to obtain this corrected interpretation.

A preliminary Nix-shell `python3` launch of the Netgen harness failed because that interpreter lacked NumPy; the recorded successful commands use the existing repository `.venv/bin/python` inside the shell. No installation was attempted.
