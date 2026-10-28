# W5 command and evidence index

The current tall-bank follow-up is reproduced by [tall-bank/COMMANDS.md](tall-bank/COMMANDS.md), including 320/1,280-row layout, DRC, independent full-bank LVS, all-bit readback and timing. Its collector preserves the prior handoff in `tall-bank/baseline64/` and adds the new measured comparison to the root reports.

All commands are run from the repository root. Active inputs and outputs remain on the Mac's internal filesystem under `overnight-20261014/taalas-array/`; no git or cloud operation was performed. Use `nice`, at most four concurrent threads across this worker, and stop launches below 22 GiB free. The final free-space observation is in `results.json`. Original generators, model artifacts and failures are retained.

The native tools are supplied by:

```sh
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix
```

Run Python commands with `PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python`. Scripts select existing native Nix tools and record their concrete invocations; no installation is required. Do not rerun into retained output names if preserving the original evidence; use a copied workspace/configuration and new run tags.

Root generation and checks, in dependency order:

```sh
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/build_base.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/check_base.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/qualify_tile_lvs.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/normalize_tile_lvs.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/build_readout.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/check_readout_tile.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/check_readout_lvs.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/export_readout_lef.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/scripts/collect_handoff.py
```

`check_base.py` and the port-promotion-only stage deliberately retain the original hierarchical pin-name mismatch; the final bijective name-normalization stage is the qualifying comparison. It changes no transistor, dimension or connectivity. `base/commands.jsonl`, `integrated/drc-command.json` and `integrated/lvs-commands.jsonl` contain the actual executable/argument vectors. Some historical stage scripts have assertions on retained failures: do not interpret a later report without inspecting these logs. The temporary PID-specific `resume_drc_after_lvs.py` is historical process scheduling only and must not be rerun.

Independent subflows and all exact per-corner/deck commands:

* [Analog timing and negative-control LVS](timing/COMMANDS.md).
* [Full 20-tile partial assembly](timing/full-readout/COMMANDS.md).
* [Digital decoder/mux implementation](periphery/RESULTS.md), with each `runs/*/` step's `COMMANDS` and logs.
* Latch implementation: `periphery/LATCH-RESULTS.md` and `periphery/latch-results.json`.
* [Decoded-tile generation and compositional LVS](timing/decoded-tile/COMMANDS.md), with the separately preserved monolithic timeout.
* [Optional lead-run monolithic LVS](CLOUD-REQUEST.md); W5 used no cloud.

Every zero-marker KLayout statement uses the reused GF180 FEOL, BEOL, connectivity and off-grid rules with 5LM/11K/MIM-B. Density and antenna are excluded. Netgen pass requires topology match **and no property errors**; a doubled-width negative control demonstrates why the topology phrase alone is insufficient. No open-flow result is represented as foundry signoff.
