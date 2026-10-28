# Credible Taalas design-point reproduction

Run from the repository root. Writes remain inside the W3 floorplan workspace. Inputs are live siblings; exact completed-run inputs are frozen in each `blocks_snapshot.json` and in `inputs/pitch-*/` with SHA256 hashes.

```sh
set -e
nice -n 10 python3 overnight-20261014/floorplan/build_credible.py
nice -n 10 python3 overnight-20261014/floorplan/prepare_credible.py
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'nice -n 10 python3 overnight-20261014/floorplan/run_selected.py pitch1280v2_sram_dense_custom_on_baseline_whole_25x31mm_pdn40_pads48 pitch1280v2_sram_open_macro_on_baseline_encoder_25x29mm_pdn40_pads32 pitch1280v2_sram_open_macro_on_baseline_decoder_25x29mm_pdn40_pads32 pitch1280v2_sram_open_macro_books_baseline_encoder_26x29mm_pdn40_pads32 pitch1280v2_sram_open_macro_books_baseline_decoder_26x29mm_pdn40_pads32'
nice -n 10 python3 overnight-20261014/floorplan/render_credible.py
nice -n 10 python3 overnight-20261014/floorplan/report_credible.py
nice -n 10 python3 overnight-20261014/floorplan/validate_credible.py
```

`prepare_credible.py` records every exact generation command in `credible_runs.json`. Example (single die):

```sh
nice -n 10 python3 overnight-20261014/floorplan/make_floorplan.py --blocks overnight-20261014/floorplan/blocks_credible.json --scenario pitch1280v2 --memory sram_dense_custom --levers on --partition whole --die-mm 25 --height-mm 31 --pdn-width-um 40 --supply-pad-pairs 48
```

For two-die runs, `encoder`/`decoder` are legacy CLI names for balanced die A/B, not implemented architectural partitions. `--levers books` preserves frontend FP32 and all mutable state, changing only book physical storage. `--levers on` enables frontend INT8 plus books-in-array; **no KV8** is enabled in this design point. `--levers off` preserves FP32/binary books. A1/A2 engine duplication and link allowances are included automatically.

Full runs use sequential OpenROAD processes at nice10 and at most4threads, with22GiB disk preflight/monitoring and600s/run guards. Each run records the exact OpenROAD command, timing, return code and minimum free space. Geometry checks automatically run through `nice -n 10 openroad -python .../check_shorts.py .../floorplan.odb`.

Early attempts without digital book-access allowance use the unversioned `pitch1280_...` names and are superseded; details in `credible_superseded_access_allowance.json`. The first generation launch had a corrected Python syntax error and missing-Tcl failure, retained in `credible_launch_failure.json` and its log. The versioned `pitch1280v2_...` cases include28.292mm² additional digital book access; do not combine their reports with unversioned trials.

`as_built_tonight_RESULTS.md`, `as_built_tonight_results.json` and `as_built_tonight_blocks.json` freeze the prior W5 stretched-pitch analysis. `report_credible.py` appends the new section without recomputing or replacing that evidence.
