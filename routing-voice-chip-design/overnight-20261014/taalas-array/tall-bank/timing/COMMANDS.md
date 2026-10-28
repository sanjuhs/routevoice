# Reproduce tall-bank sampled timing

Run from the repository root. All active outputs remain under this directory. Check `df -h /` before every large run; at least 22 GiB must remain free. Limit concurrent EDA processes to four total, including other workers. Each command below uses one process and `nice`.

```sh
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/extract.py --rows 320 --version g2 --group 2'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/extract.py --rows 1280 --version v1'
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/prepare.py r320-g2
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/prepare.py r1280-v1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/rank_fullbank.py
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/rank_caps.py r320-g2
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/rank_caps.py r1280-v1
```

`extract.py` snapshots source geometry and emits exact Magic Tcl and commands in each extraction directory. G02 is emitted from the actual complete 320-row assembly, not regenerated from a synthetic image. `prepare.py` checks the complete extracted transistor graph, sizes and real programmed image, with bijective node canonicalization.

For each directory/corner/period listed in `results.json`, use:

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/simulate.py --directory r320-g2 --corner ss --period 60
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/simulate.py --directory r1280-v1 --corner ss --period 60
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/global_sensitivity.py --corner ss --period 40
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/taalas-array/tall-bank/timing/summarize.py
```

Use `typical` for TT. Each case directory contains its exact frozen `test.cir`, source scripts, `build.json`, ngspice command, log, result and compressed trace. To replay an existing deck exactly, run `nice -n 10 /opt/homebrew/bin/ngspice -b test.cir` from that case directory; use a new copied case directory to preserve the retained evidence. Model includes are absolute local GF180 PDK paths. Production runs enforce a 600-second wall timeout and reject incomplete traces even if ngspice returns status zero.

Early 20/40 ns runs used a PULSE PC source whose rounded fractional width produced near-coincident breakpoints with the explicit PWL aggressors. They aborted at the first precharge-return edge. The retained failures are numerical, not electrical protocol failures. Final short profiles use an explicit PWL PC source at the same intended phase times. Earlier isolated behavioral power monitor nodes were also replaced by post-transient vector calculations; they had no feedback to the circuit. Frozen decks distinguish these revisions and Gear versus trapezoidal integration. No incomplete trace receives energy or timing credit.

The authoritative optional 1280 comparison uses `--directory r1280-compact-v1` at both TT and SS, 60 ns. Its pattern-override.json deliberately limits coverage to alternating far-end rows 1278 and 1279, repeated twice. The full-pattern SS case in r1280-v1 is additional evidence only.

Closed `.ext` files are gzip-compressed; `closed-ext-compression.json` contains verified original hashes and restoration commands.
