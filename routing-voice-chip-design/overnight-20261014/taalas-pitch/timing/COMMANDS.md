# Reproduction contract

All commands execute from repository root, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1` and nice priority. Start only after the exact parent layout revision is DRC-clean. Preserve the generated directory rather than overwriting a prior attempt.

```
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/timing/prepare_w6.py --source overnight-20261014/taalas-pitch/REVISION/bank.gds --rows HEIGHT'
.venv/bin/python overnight-20261014/taalas-pitch/timing/normalize.py rHEIGHT-gGROUP
.venv/bin/python overnight-20261014/taalas-pitch/timing/rank_caps.py rHEIGHT-gGROUP
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/timing/simulate.py --directory rHEIGHT-gGROUP --corner ss --period 60 --segments 32'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/timing/simulate.py --directory rHEIGHT-gGROUP --corner typical --period 60 --segments 32'
```

`prepare_w6.py` selects its group from all1280 columns using actual layout-route resistance and real-image drain count. It reopens the exact parent GDS and exports only the selected subbank; Magic independently extracts the array and joined stacked layout. `normalize.py` checks every extracted MOS against the real image and receiver transistor circuit. `rank_caps.py` refines the heuristic within that128-column subbank using actual extracted metal capacitance and selects its16-column ground-strap group. `simulate.py` snapshots each executed deck/build/protocol source and reports finite-window source energy.

`adapt.py`, `simulate-w5-source.py`, and `normalize-w5-source.py` preserve initial scaffold/source provenance, not the final executable pipeline: later geometry reading improvements are in the executable scripts.

After the full-bank native Magic extraction finishes successfully, the official capacitance export reads its saved `.ext` without modifying it. The output is compressed directly through a FIFO; producer and decompressed SHA256/byte counts must agree, and every MOS line must match the LVS export byte for byte.

```
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/timing/export_fullbank_caps.py --gzip'
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-pitch/timing/rank_fullbank_caps.py --spice overnight-20261014/taalas-pitch/timing/fullbank-caps/extracted-cap.spice.gz --geometry overnight-20261014/taalas-pitch/r1280-v2/geometry.json --extraction-input overnight-20261014/taalas-pitch/verification/r1280-v2/input.json --output rank.json
```

If the global candidate differs from the pilot, prepare its group with `prepare_w6.py --group GROUP`, then normalize and run `rank_caps.py r1280-gGROUP --global-bit BIT --global-rank-source overnight-20261014/taalas-pitch/timing/fullbank-caps/rank.json`. Use a fresh directory for every changed rank/stimulus. Compare exact full-bank/crop signed incident capacitance with `compare_crop_caps.py --crop r1280-gGROUP`.

`global_control_sensitivity.py --directory FRESH_INPUT_DIRECTORY --corner ss --period 60` is an optional, explicitly limited full-WL/PC-loading sensitivity. Clone immutable characterization inputs into a new directory first. It adds measured full-bank control C and remote intrinsic gate loads to a geometry-R rail approximation, retaining the primary stock-driver count. It does not model full-bank current or energy.

The complete-control 60 ns SS case converged but failed precharge and phase checks. Its control-delay diagnostic selected one conservative 120 ns protocol; it did not tune the circuit or search a minimum period. `guarded_full_control.py --directory r1280-g09-fullcontrol-guarded` reproduces the SS follow-up. `guarded_full_control_tt.py --directory r1280-g09-fullcontrol-guarded` runs its native TT companion. Use the same Nix/nice/single-thread invocation above. Both use immutable hard-linked inputs described in `source-data-origin.json`, separate output directories, and retained source snapshots. SS asserts every physical circuit line identical to the failed 60 ns deck; TT asserts device/capacitor identity and resistor connectivity while intentionally changing native PVT and temperature-scaled geometry resistance.

After successful export and all native LVS work, the verifier losslessly compressed the original `verification/r1280-v2/W6_PITCH_BANK_FLAT.ext` to `.ext.gz` and verified the decompressed SHA256 before removing only the raw copy. See `verification/r1280-v2/native-ext-compression.json`. The exporter receipt describes its historical original path at export time. Replaying the native export requires restoring the archived `.ext` first; retained official full-cap SPICE and all timing inputs remain independently available.

The six idle local `W6_TIMING_{ARRAY,JOINED}.ext` intermediates were archived after their native extraction and all subsequent timing-input generation completed. `native-extraction-archives.json` and per-file `.ext.archive.json` record no-reader checks and independent decompressed SHA/byte verification before raw removal. Their `.ext.gz` files restore exact original bytes; no cap/canonical inputs, decks, or traces were changed.

The guarded TT run progressed unusually slowly through its first static precharge interval. The parent authorized extending only its original Python wait from 1,200 to an absolute 2,400 seconds, preserving the native process. `extend_owned_tt_wait.py` validates exact owned PIDs/cwd, pauses only the Python waiter, checks a 22.2 GiB disk reserve, and resumes the original waiter on native exit or deadline. The per-case `watchdog-extension.json` records the process identities, deadline, runtime implementation check, and actions. No circuit, model, tolerance, timestep, or initial condition was changed.

At finalization, the parent requested lossless archival of all three idle cropped `source-joined.gds` inputs because host background activity continued consuming disk space. `cropped-gds-archives.json` and each `.gds.archive.json` record no-reader checks, independent decompressed SHA/byte equality, and identity to the historical extraction source hash before raw removal. Restore exact original names from `.gds.gz` for replay. The final `r1280-v2/bank.gds`, canonical/capacitance netlists, timing decks and traces were not changed.
