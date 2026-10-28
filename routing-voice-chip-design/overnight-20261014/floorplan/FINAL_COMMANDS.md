# Final lossless-frontend floorplans: reproduction

Run from the repository root. All generated files remain in `overnight-20261014/floorplan/`.
Source snapshots and per-run `blocks_snapshot.json` preserve the inputs used tonight; a later
rebuild reads current sibling results and therefore can legitimately change the results.

```sh
df -h /
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'nice -n 10 python3 overnight-20261014/floorplan/measure_sram_bitcell.py'
nice -n 10 python3 overnight-20261014/floorplan/build_final.py
nice -n 10 python3 overnight-20261014/floorplan/prepare_final.py
nice -n 10 python3 overnight-20261014/floorplan/analyze_state_reduction.py
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'nice -n 10 python3 overnight-20261014/floorplan/run_selected.py final_pitch_sram_bitcell_large_macro_lossless_baseline_whole_29x31mm_pdn40_pads48 final_pitch_sram_dense_custom_lossless_baseline_whole_25x31mm_pdn40_pads48 final_pitch_sram_open_macro_lossless_baseline_encoder_25x29mm_pdn40_pads32 final_pitch_sram_open_macro_lossless_baseline_decoder_25x29mm_pdn40_pads32'
nice -n 10 python3 overnight-20261014/floorplan/build_final.py
nice -n 10 python3 overnight-20261014/floorplan/audit_final_refresh.py
nice -n 10 python3 overnight-20261014/floorplan/render_final.py
nice -n 10 python3 overnight-20261014/floorplan/report_final.py
nice -n 10 python3 overnight-20261014/floorplan/validate_final.py
```

`final_runs.json` records every exact generator argv. Each run directory contains
`execution.json` with the exact OpenROAD argv, exit code, runtime, minimum free space,
thread count and nice level. `run_selected.py` executes sequentially, sets four threads,
and enforces the 22 GiB disk guard. The final four runs each returned zero; minimum
observed free space was above 24 GiB. Geometry, source-refresh and reporting commands
use one Python process. No cloud or git commands are involved.

The post-run input refresh only changed source qualification metadata; see
`final_input_refresh_audit.json`. If that audit reports a physical-input change on a
future reproduction, regenerate and rerun the affected cases before reporting.
