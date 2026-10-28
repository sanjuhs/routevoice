# Measured-input reproduction

Run from repository root. All generated files are inside `overnight-20261014/floorplan/`.

```sh
nice -n 10 python3 overnight-20261014/floorplan/build_measured.py
nice -n 10 python3 overnight-20261014/floorplan/find_measured_outlines.py
nice -n 10 python3 overnight-20261014/floorplan/make_floorplan.py --blocks overnight-20261014/floorplan/blocks_measured.json --scenario measured320 --die-mm 44 --height-mm 53 --pdn-width-um 40
nice -n 10 python3 overnight-20261014/floorplan/make_floorplan.py --blocks overnight-20261014/floorplan/blocks_measured.json --scenario measured320 --partition encoder --die-mm 32 --height-mm 38 --pdn-width-um 40
nice -n 10 python3 overnight-20261014/floorplan/make_floorplan.py --blocks overnight-20261014/floorplan/blocks_measured.json --scenario measured320 --partition decoder --die-mm 32 --height-mm 38 --pdn-width-um 40 --supply-pad-pairs 32
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'nice -n 10 python3 overnight-20261014/floorplan/run_selected.py measured320_sram_open_macro_off_baseline_whole_44x53mm_pdn40 measured320_sram_open_macro_off_baseline_encoder_32x38mm_pdn40 measured320_sram_open_macro_off_baseline_decoder_32x38mm_pdn40_pads32'
nice -n 10 python3 overnight-20261014/floorplan/render_measured.py
nice -n 10 python3 overnight-20261014/floorplan/report_measured.py
```

The initial three failed IR cases used these same generation commands with `--pdn-width-um 40` omitted (default20), and the same runner names without `_pdn40`. Their outputs/logs are preserved. `execution.json` records exact OpenROAD command, return code, elapsed time, minimum free space, nice and thread limit for each attempt. Each Tcl includes `set_thread_count 4`; runner limits BLAS/OMP/VECLIB threads to4. Guard:22GiB free before launch and during each process;600s maximum per run.

`build_measured.py` snapshots and hashes live siblings on each invocation. To reproduce exact completed outputs, use each run's immutable `blocks_snapshot.json`, not potentially updated live siblings. Generated LEF/Tcl/voltage-source CSVs are retained. `check_shorts.py` is automatically run through `nice -n 10 openroad -python ... floorplan.odb` after each successful OpenROAD process.

The measured axis has6selection scenarios ×3memory densities ×2lever states. Only measured320/open/off has completed physical cases. The 18 original requested comparisons are included in the36row area table; other combinations remain arithmetic screens.

Die B also retained a40µm/16pair failure in `measured320_sram_open_macro_off_baseline_decoder_32x38mm_pdn40`. It used the same command without `--supply-pad-pairs 32`, then reran with32pairs for IR. The original20µm cases omit both width and pad overrides. Two large historical failed-output files were losslessly compressed with verified SHA256; see `old_failure_compression_receipt.json` for restoration.
