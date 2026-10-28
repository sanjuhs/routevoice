# Preserved launcher issues

1. First verification launcher exited before compiling: macOS Bash 3 with `set -u` rejected the empty `flags` array expansion. Observed output: `overnight-20261014/fabric/verify.sh: line 10: flags[@]: unbound variable`. Original launcher is `verify.initial-bash3-failure.sh`; corrected launcher uses an optional scalar flag. No test received pass credit for the failed launch.
2. Full V1 first physical attempt was interrupted at 103.54 seconds while LibreLane's verbose Rich console processing was spending CPU on huge constant-table lines. The condensed restart uses unchanged RTL. Original `runs/rv_fixed_proj320_rom-v1` and `logs/rv_fixed_proj320_rom-v1.flow.log` remain.
3. Full V1 condensed restart was killed by its disk guard after 100.12 seconds, at 22,879,318,016 free bytes. No completed technology-map or area result is credited to that run.
4. The V2 first attempt did not launch EDA: its guard saw 21,132,218,368 free bytes. This is below the requested system floor of 20 GiB; W2 had already stopped its active flow at its higher 22 GiB threshold. W2 cannot stop unrelated jobs.
5. The first 64-row launch unexpectedly passed the disk precheck after system space recovered. Task-local duplicate PDK cleanup was then started without first resolving the yielded launch result. The PDK removal raced config loading, causing missing-file errors. This was a W2 orchestration mistake. The failed attempt is preserved; the complete PDK copy was restored and its copy process was awaited before the corrected `restored` attempt.
6. Early ABC temporary files used the toolchain's inherited `/tmp` despite the outer TMPDIR export. The corrected launcher explicitly exports task-local TMPDIR inside the Nix `--run` shell. Task artifacts and persistent outputs are all under the authorized workspace.

None of these failures is a numerical circuit failure or a physical signoff pass.

7. The 45%-utilization slice completed synthesis, floorplan, default PDN and placement, but post-GPL repair inserted 43,363 buffers and detailed placement failed on 840 instances (`DPL-0036`). The `util30` continuation starts at `OpenROAD.Floorplan` using the original pre-PNR state, with 30% core utilization, 55% placement density and maximum placement displacements of 1500 x / 800 y. No electrical or signoff checker is disabled.

8. V2 has 42,319 total signal port bits. Its initial resource-refused attempt used stock pin settings. Before actual EDA, the V2 config was changed to permit IO placement on all five metals, using their LEF directions (H: Metal1/3/5, V: Metal2/4), one-track minimum separation and minimum-width (1x) pins. This is an explicit internal-array interface placement choice, not a claim of a package pinout. PDN defaults and routing/DRC/LVS checks remain enabled. Valid pin access and DRC still have to be demonstrated by the flow.

9. V2 enables LibreLane `DEDUPLICATE_CORNERS`: during PnR this removes only identical liberty/layer-RC/via-R analysis cases. The configured nine final STA corners remain unchanged. This follows the implementation in `tools/librelane/librelane/steps/openroad.py` and avoids repeating identical pre-extraction calculations. The in-progress slice continuation retains its original setting.

V2 physical floorplan prepared at 30% core utilization / 55% placement density with displacement X=1500, Y=800, following the slice legalization failure at 45% and successful legalization at 30%. This change preceded any actual V2 EDA launch.

The first optional gate-check invocation supplied a guessed `.v` filename and failed its `netlist.is_file()` assertion before launching any compiler. The corrected invocation reads the actual `nl` path from synthesis `state_out.json`. This is an argument error, not a verification failure.
