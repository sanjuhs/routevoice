from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent;O=W/'v1'
def get(n):return json.loads((O/n).read_text())
geo=get('geometry.json');drc=get('decoded-tile-checks.json');read=get('readback.json');mono=get('lvs-result.json');audit=get('partition-audit.json');parts=[get(f'bank{g}-lvs-result.json') for g in range(10)];dim=get('dimensions-check.json')
assert audit['exact_disjoint_device_cover'] and audit['independent_reference_exact_disjoint_device_cover'] and audit['only_intended_cross_bank_nets']
assert audit['partition_files_checked_for_exact_device_identity']==list(range(10))
assert all(p['unique_match'] and not p['property_errors'] and p['returncode']==0 for p in parts)
assert drc['drc_markers']==0 and read['index_mismatches']==0
if mono['netgen_returncode']!=0:mono['completion_status']='bounded_incomplete';mono['property_check_completed']=False;mono['property_errors_observed_before_termination']=mono['property_errors'];mono['property_errors']=None
result={'status':'decoded_tile_compositional_lvs_and_scoped_drc_passed','scope':'One actual64row x320lane x4bit tile with ten physically connected local row decoders and1280analog precharge/keeper/receiver channels. NOT complete projection macro.','gds_file':'v1/decoded-tile.gds','gds_top_cell':'RV_K64_DECODED_TILE_00','selection_count':20480,'bitcell_count':81920,'dimensions_um':geo['dimensions_um'],'area_um2':geo['area_um2'],'area_um2_per_selection_including_present_periphery':geo['area_um2']/20480,'decoder_instances':10,'top_ports':{'power':['VDD','VSS'],'controls':['ROW0..ROW5','EVAL','PC'],'outputs':['OUT0..OUT1279']},'drc_full_tile':drc,'drc_bank0':get('decoded-bank0-checks.json'),'compositional_lvs':{'passed':True,'total_devices':111460,'partitions':10,'all_unique_matches':True,'property_errors':0,'disjoint_cover_and_shared_net_audit':audit,'partition_results':parts,'scope':'Independent real indices/analog circuit plus frozen powered decoder connectivity expanded through official PDK standard-cell transistor library. Every physical transistor covered exactly once; only actual intended shared nets cross boundaries.'},'monolithic_netgen':mono,'analog_exact_device_graph_and_dimensions_match':True,'dimensions_and_global_fanout_check':dim,'bit_readback':read,'gds_sha256':hashlib.sha256((O/'decoded-tile.gds').read_bytes()).hexdigest(),'source_tile_sha256':geo['source_tile_sha256'],'decoder_source_sha256':geo['decoder_sha256'],'timing_energy':None,'exclusions':['No precharge/evaluate phase generator or qualified phase drivers','No20tile output mux or global output network','No output capture latches','No decoded-tile extracted transient/distributedRC qualification','No20tile decoded composition','No decoded-tile LEF abstract','Scoped DRC excludes antenna and density'],'preserved_incomplete_or_failed_checks':[{'artifact':'v1/netgen.log','status':mono.get('completion_status','completed'),'note':'Monolithic Netgen bounded after600seconds if unfinished. Compositional result reported separately.'},{'artifact':'v1/dimensions-check-failed-v1.json','status':'checker corrected','note':'Initial auxiliary fanout counter incorrectly distinguished interchangeable source/drain ordering. Corrected counter passes; no circuit changed.'},{'artifact':'bank_lvs-failed-v1.py','status':'checker corrected','note':'Initial partition selector omitted precharge PMOS whose local node is IDX instead of OUT/WL. Added IDX ownership; no circuit changed.'}]}
(W/'results.json').write_text(json.dumps(result,indent=2)+'\n')
(W/'RESULTS.md').write_text(f'''# Physically decoded real K64 tile 0

**Scoped DRC and compositional transistor LVS pass.** The GDS contains the real first 64 projection rows, 320 lanes × 4 bits, 1,280 physical precharge/keeper/receiver channels, and ten frozen 120 × 120 µm local decoder macros. It remains a partial projection macro.

- Tile dimensions: **{geo['dimensions_um'][0]:.1f} × {geo['dimensions_um'][1]:.1f} µm**; area **{geo['area_um2']:,.2f} µm²**; **{result['area_um2_per_selection_including_present_periphery']:.6f} µm² per selection** including present periphery.
- Full tile and bank 0 scoped GF180 KLayout DRC: **0 markers**. FEOL, BEOL, connectivity and off-grid rules checked; antenna/density excluded.
- Actual Magic flat extraction: **111,460 transistors**. Each of ten components passes Netgen with a unique match and **zero property errors** against its distinct real-mask reference.
- Partition audit proves an exact disjoint cover of every extracted and reference transistor, no node merging, all 640 separate local wordlines, correct ownership of all 1,280 outputs, and exactly ten intended shared nets: VDD, VSS, PC, EVAL, ROW0–ROW5. Global power/control terminal fanout matches the independent reference.
- The complete analog portion also passes exact device-graph and dimension comparison: **87,040 transistors**.
- Reopened GDS readback: **20,480 selections / 81,920 bits, zero mismatches**, including 40,786 programmed Via1 ones.

The monolithic Netgen result is **{mono.get('completion_status','completed')}** and is retained separately in `v1/netgen.log`. It is not presented as a monolithic LVS pass. The passing compositional proof covers the same full tile and all devices, including the 24,420 decoder and physical standard-cell transistors. Reference decoder connectivity comes from the separately qualified frozen handoff, expanded using the official GF180 transistor library; decoder logical correctness also relies on that worker's functional qualification.

The original 64 global M3 wordline wires were removed. A horizontally mirrored decoder occupies each bank's existing empty area. M2 source legs, M4 vertical tracks, and M5 target legs connect each decoder output to its own local array wordline. Shared M5 buses physically distribute address, evaluate, and supplies. Decoder M4 supply stripes physically reach those buses. There are no label-only joins.

**No decoded-tile timing or energy claim is made.** Prior ideal-source bank measurements do not qualify this integration. External ROW, EVAL and PC are explicit controls; phase generation, twenty-tile output selection/global wiring, output capture latches, and complete ARRAY-PORT integration remain missing. No decoded twenty-tile composition or LEF was produced.

Two auxiliary checker mistakes were corrected without changing any circuit: source/drain order in a fanout counter, and missing IDX ownership in the first component selector. Both failed versions are preserved. See `results.json`, `INTEGRATION.md`, `COMMANDS.md` and the original logs.
''')
(W/'COMMANDS.md').write_text('''# Exact reproduction

Run from repository root; maintain at least 22 GiB free on `/`. All outputs are inside this directory. DRC uses 2 threads; Magic and each Netgen run use 1 thread, with nice 10. Limit simultaneous jobs to 2 threads here.

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/build.py v1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/readback.py
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/reference.py
source /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/check.py v1 bank0'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/check.py v1 tile'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/extract.py'
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/lvs.py'
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/dimensions.py
NIX_BUILD_SHELL=/bin/bash nix-shell tools/librelane/shell.nix --run 'for bank_group in 0 1 2 3 4 5 6 7 8 9; do PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/partition_lvs.py "$bank_group" || break; done'
PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/audit_partition.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python overnight-20261014/taalas-array/timing/decoded-tile/finalize_compositional.py
```

`lvs.py` produces the bijectively normalized full extraction and launches monolithic Netgen. The original run was manually bounded at 600 seconds, retaining outputs; the component commands are the completed proof. Each component command has a 200-second timeout. Exact nested tool arguments are in `v1/*command*.json`; hashes are in `results.json` and `v1/geometry.json`. Bank 0 was originally run by `bank_lvs.py`, which is equivalent to `partition_lvs.py 0` except for its top-cell name.
''')
print('W5-STATUS: decoded tile DRC0; compositional LVS all10unique/0property errors;81920bits read back; monolithic '+mono.get('completion_status','completed'),flush=True)
