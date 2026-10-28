# Reproduction commands

Run from the repository root. All generated paths are beneath `overnight-20261014/floorplan/`. Do not use the SSD-linked `build/` directory as an active work directory.

```sh
python3 overnight-20261014/floorplan/build_blocks.py
python3 overnight-20261014/floorplan/refresh_measurements.py
python3 overnight-20261014/floorplan/make_floorplan.py --scenario custom7 --memory sram_open_macro --levers off --die-mm 34
python3 overnight-20261014/floorplan/make_floorplan.py --scenario custom7 --memory sram_open_macro --levers off --partition encoder --die-mm 25
python3 overnight-20261014/floorplan/make_floorplan.py --scenario custom7 --memory sram_open_macro --levers off --partition decoder --die-mm 25
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'python3 overnight-20261014/floorplan/run_selected.py'
python3 overnight-20261014/floorplan/render_heatmaps.py
python3 overnight-20261014/floorplan/summarize.py
```

`run_selected.py` invokes the following for each selected case, sequentially. `CASE` is one of `custom7_sram_open_macro_off_baseline_whole_34mm`, `custom7_sram_open_macro_off_baseline_encoder_25mm`, `custom7_sram_open_macro_off_baseline_decoder_25mm`.

```sh
QT_QPA_PLATFORM=offscreen OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4 nice -n 10 openroad -exit overnight-20261014/floorplan/runs/CASE/floorplan.tcl
nice -n 10 openroad -python overnight-20261014/floorplan/check_shorts.py overnight-20261014/floorplan/runs/CASE/floorplan.odb
```

Each `execution.json` saves the exact absolute OpenROAD argv, return code, elapsed time and minimum free storage. Logs are `logs/CASE.log`. The implementation revision in the successful runs is `dcf36133a369abc8f3c5e5738cd4d82e4903c0e0`. PDK revision is `54435919abffb937387ec956209f9cf5fd2dfbee`, GF180MCU-D.

The successful final overlap checks were rerun with via enclosures included:

```sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'nice -n 10 openroad -python overnight-20261014/floorplan/check_shorts.py overnight-20261014/floorplan/runs/custom7_sram_open_macro_off_baseline_whole_34mm/floorplan.odb > overnight-20261014/floorplan/logs/check_shorts_full.log 2>&1'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'nice -n 10 openroad -python overnight-20261014/floorplan/check_shorts.py overnight-20261014/floorplan/runs/custom7_sram_open_macro_off_baseline_encoder_25mm/floorplan.odb > overnight-20261014/floorplan/logs/check_shorts_encoder.log 2>&1 && nice -n 10 openroad -python overnight-20261014/floorplan/check_shorts.py overnight-20261014/floorplan/runs/custom7_sram_open_macro_off_baseline_decoder_25mm/floorplan.odb > overnight-20261014/floorplan/logs/check_shorts_decoder.log 2>&1'
```

For another explicit scenario, pass `--memory sram_4k_research` or `--memory sram_dense_custom`, `--levers on`, and optionally `--state conservative`. These switches generate inputs; they do not qualify those memories or altered numerics. Do not restore the earlier blanket die sweep.

Input refresh is explicit, not a background monitor. Re-run `refresh_measurements.py` when sibling files update, inspect the measured boundary, then regenerate selected cases if their sizes or currents actually change. An aggregate `$mem` count containing immutable coefficient ROMs must not silently be added as mutable SRAM; classify writable memories and avoid counting those ROMs twice.

The active PDK snapshot under `pdk/` contains only the nominal tech LEF, 3.3 V TT standard-cell Liberty, standard-cell LEF, IO LEFs and SRAM LEFs copied from the requested GF180MCU-D revision. Original PDK/model/research sources were not edited.
