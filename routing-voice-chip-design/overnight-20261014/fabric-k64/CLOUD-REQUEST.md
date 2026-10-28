# W2b SC-ROM handoff — lead operated, no cloud resource started

The complete 1280×320 K64 **standard-cell comparator** synthesized successfully at 20 ns: 436,025 mapped cells, 8.255466688 mm² summed cell area, zero unmapped cells, zero inferred latches and zero synthesis check errors. This is not routed area or a timing pass. RTL passes 54 vectors / 17,280 integer and 17,280 FP32 outputs with resets and stalls. Both variants also pass the complete mapped-netlist functional replay (54 vectors / 17,280 FP32 outputs, four resets and 104,112 stall events).

SC-ROM was stopped after 49.2 cumulative local minutes (including the interrupted TMPDIR-correction attempt), during pre-PNR STA. Its successful synthesis took 34m16.337s. ARRAY-PORT's repair step processed about 32,000 of 321,396 nets in roughly 14 minutes. Extrapolating that observed rate to the larger SC-ROM, with CTS/routing/extraction/signoff still pending, makes completion within ~2.5 hours unlikely. This is a runtime forecast, not a physical impossibility conclusion. ARRAY-PORT continues locally. Evidence: `evidence/sc_rom-v2-budget-stop.json`, `evidence/sc_rom-guard.json`, and `runs/sc_rom-v2/06-yosys-synthesis/`.

## Exact payload

Copy this workspace preserving its relative layout. The required EDA/verification file list is `evidence/cloud-file-list.txt`; all 5,343 files, including the actual PDK, are SHA-256 bound in `evidence/cloud-inputs.json`. Copy those two manifests and this document too. `configs/sc_rom.json` is the exact tested config. No host weight service or candidate-model download is needed to run the frozen RTL. Candidate regeneration/identity auditing additionally requires original repository model inputs documented in `COMMANDS.md` and `evidence/identity.json`.

From the local workspace, optionally create a payload for the lead (this command has not been run):

```sh
tar -czf sc-rom-cloud-inputs.tar.gz -T evidence/cloud-file-list.txt evidence/cloud-inputs.json evidence/cloud-file-list.txt CLOUD-REQUEST.md
```

Use an x86_64 Linux CPU machine with at least 64 GiB RAM and 50 GiB free workspace storage. Those are provisioning recommendations, not measured minima. The worker has not rented a pod or incurred cloud spending. Any lead-operated run remains under the lead's spending guard.

## Pinned tool environment and commands

Use LibreLane 3.0.11, commit `33ab64861c5570d65de69295da9a46f5bad32ee3`, with its locked Nix dependencies and the supplied GF180MCU-D PDK (`open_pdks` commit `54435919abffb937387ec956209f9cf5fd2dfbee`). On a machine with Nix installed, from the copied workspace:

```sh
mkdir -p tmp cache
python3 - <<'PY'
from pathlib import Path
import hashlib,json
for x in json.loads(Path('evidence/cloud-inputs.json').read_text()):
    assert hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'], x['path']
print('All cloud input hashes match')
PY
python3 relocate.py
git clone https://github.com/librelane/librelane.git toolchain-librelane
git -C toolchain-librelane checkout 33ab64861c5570d65de69295da9a46f5bad32ee3
nix-shell toolchain-librelane/shell.nix --run 'bash cloud_flow.sh sc_rom' > logs-sc-rom-cloud.txt 2>&1
```

`relocate.py` changes only path prefixes in copied config/testbench files. `cloud_flow.sh` sets internal TMPDIR, uses nice 10, `--jobs 6`; config caps detailed route at 3 threads and multicorner STA at 2. It starts from synthesis to avoid stale absolute paths/checkpoints. The 3.3 V Liberty files are explicit; the PDK's default 5 V setting is not the selected timing corner. Nine PVT/RC combinations are selected. Keep the 20 ns starting target and report violations honestly.

The integrated KLayout DRC runset resolves to null in this PDK integration. After GDS exists, run the official supplied standalone deck within the pinned shell:

```sh
bash run_klayout_drc.sh sc_rom /absolute/path/to/final/rv_k64_sc_rom.gds
```

Use `power.tcl` with the final netlist/SDC/extracted SPEF, the actual corner Liberty, and `evidence/sc_rom-speech.vcd` (included in the payload). Record VCD annotation coverage; report default/propagated activity if internal names do not map. The VCD is a real captured activation vector, not random stimulus. `verify_gate.sh sc_rom /absolute/path/to/final/netlist.v` runs the external-output mapped/routed netlist regression; it needs Verilator and C++ build tools. Do not infer a routed correctness pass from RTL tests.

Return final netlist, SDC, SPEF, GDS/DEF, rendered PNG, reports/logs, exact tool revisions, all corner timing and power/annotation reports, Magic/KLayout DRC, Netgen LVS and antenna results. Routed area/energy/fabric partition and achievable MHz remain unmeasured locally. A completed placement or valid GDS alone does not establish signoff.

The payload now also includes ARRAY-PORT’s complete mapped real-vector SAIF, with full pin coverage at the local placement checkpoint. SC-ROM’s attempt to generate mapped SAIF stopped at the22GiB disk headroom guard during compilation; no SC SAIF pass is claimed. Its existing RTL VCD remains available. On the lead’s machine, after synthesis and relocation, a complete mapped trace can be generated with the supplied two-thread launcher:

```sh
bash run_gate_activity.sh sc_rom /absolute/path/to/sc_rom-cloud/06-yosys-synthesis/rv_k64_sc_rom.nl.v
```

This checks320 outputs for saved vector0 at4163cycles and writes `evidence/sc_rom-mapped-speech.saif`. Do not credit an interrupted build. Pass the completed SAIF through W2B_SAIF to `power.tcl`, and repeat actual annotation coverage on the final routed netlist. Final routing may add cells or change mapped identities. `report_units` prints units into the invocation log; preserve it.
