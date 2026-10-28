# W9 retained checkpoint

The morning archive contains the exact synthesized buffered netlist, placed OpenDB/DEF/netlists/SDC and completed reports. Overlay `final-delta-evidence.tar.gz` when available; its `delta-base.json` identifies the required morning archive hash. No routed or signoff result is implied by these checkpoints.

The retained input for physical repair is `runs/buf-v4/25-checker-powergridviolations/state_out.json`, referencing the completed `23-openroad-globalplacement` database. Repair was not complete at the morning handoff; a partial in-memory repair cannot be resumed from its iteration counter.

On an authorized environment with the original repository/PDK paths restored, copy `run-flow-v4-physical.sh` under a fresh name and change only its run tag and associated log/exit names before rerunning it. The required LibreLane entry point is `--from OpenROAD.RepairDesignPostGPL --with-initial-state .../runs/buf-v4/25-checker-powergridviolations/state_out.json`. Keep `configs/array_port_buf.json`. Do not overwrite the retained failed attempts.

The corrected synthesis is reproduced through `librelane_pi.py` and `synthesize_pi.py`: ABC PI buffering (`-p`) plus an ABC-only bare driving-cell name, with ten mirrored RTL row domains. Numerical tables and model artifacts remain unchanged.

For eventual routed characterization, `run-power.py` selects the extracted nominal TT SPEF and reads the unique frozen trace `evidence/array_port-mapped-speech-w9-frozen.saif`. Use its 20 ns estimate only with the reported timing/electrical validity flag. The trace is also available as a verified gzip file and in the morning archive.
