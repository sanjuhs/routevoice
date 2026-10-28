# ARRAY-PORT checkpoint continuation (not executed)

The approved first physical phase is capped at four cumulative hours, including the interrupted v1 attempt. Preserve its result. This recipe is for a subsequent bounded phase operated by the lead; it is not an automatic retry or an authorization to extend the stopped phase.

`evidence/array_port-checkpoint31-manifest.json` hashes the last completed state and all 11 referenced files. The step31 state points to the step28 placed netlist/ODB/DEF/SDC, generated power connections, source header and early SDF views. The unfinished step32 has no saved repaired database; its printed counters do not imply a resumable partial repair. APFS-compressed SDF files retain their ordinary paths and exact bytes.

On the same Mac/workspace, set the following variables from the repository root, then run within the new phase's explicit disk/time guard:

```sh
export W2B_DIR="$PWD/overnight-20261014/fabric-k64"
export W2B_PDK="$W2B_DIR/pdks"
export TMPDIR="$W2B_DIR/tmp" XDG_CACHE_HOME="$W2B_DIR/cache" PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=3 NUMEXPR_NUM_THREADS=1
nice -n10 nix-shell tools/librelane/shell.nix --run 'export TMPDIR="$W2B_DIR/tmp"; librelane --condensed --log-level WARNING --manual-pdk --pdk gf180mcuD --pdk-root "$W2B_PDK" --design-dir "$W2B_DIR" --run-tag array_port-continuation --from OpenROAD.RepairDesignPostGPL --with-initial-state "$W2B_DIR/runs/array_port-v2/31-openroad-stamidpnr/state_out.json" --jobs 3 "$W2B_DIR/configs/array_port.json"'
```

The `--from` and `--with-initial-state` option names and `OpenROAD.RepairDesignPostGPL` step ID were checked in the actual LibreLane 3.0.11 source. The command itself has not been run or claimed to pass. Use a fresh run tag to preserve all prior logs. After relocating, the state and every referenced path need rebasing; `relocate.py` handles RTL/config/testbench paths only. A fresh cloud synthesis uses the simpler existing CLOUD-REQUEST recipe and avoids stale checkpoint paths.

Retain the full 1280×320 boundary, complete books and declared widths. A follow-up change to explicit row/decode driver distribution needs fresh functional and physical verification; do not treat the present low-level fanout diagnostics as an extracted result.
