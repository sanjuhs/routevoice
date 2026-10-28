# Optional lead-run monolithic decoded-tile LVS

W5 used no cloud resources. Full hierarchical DRC of the 20-tile **partial** assembly completed locally. The decoded tile's monolithic Netgen comparison was stopped after 600.44 seconds while still graph-matching; its partial logs are retained. The compositional alternative checks all ten extracted banks plus exact actual/reference device coverage and shared-net topology. Consult `timing/decoded-tile/results.json` for its final disposition.

This is an **optional additional monolithic comparison**, not a request to treat the complete macro as implemented. More CPU does not supply missing phase control, global mux/latch routing, full-macro timing or a 20-tile composition netlist. Netgen is largely single-threaded here; a 32-core host is not assumed to give a 32× speedup. The lead controls any cloud run and spending under the existing authorization.

Copy these retained files without changing their contents:

* `overnight-20261014/taalas-array/timing/decoded-tile/v1/canonical.spice`
* `overnight-20261014/taalas-array/timing/decoded-tile/v1/reference.spice`
* The GF180 PDK `libs.tech/netgen/gf180mcuD_setup.tcl` and its referenced setup files from the same pinned PDK revision (`54435919abffb937387ec956209f9cf5fd2dfbee`).
* For audit, also copy `v1/connectivity.json`, `partition-audit.json`, all `bank*-lvs-result.json`, and the decoder/reference-generation sources. GDS is not needed to rerun the already-extracted netlist comparison; copying it enables separate extraction reproduction.

On a Linux host with the same Netgen 1.5.316 and the repository/PDK tree restored, start at the repository root:

```sh
ROUTEVOICE_REPO="$(pwd)"
cd overnight-20261014/taalas-array/timing/decoded-tile/v1
timeout 3600s nice -n 10 netgen -batch lvs \
  'canonical.spice W5_DECODED_TILE_FLAT' \
  'reference.spice W5_DECODED_TILE_FLAT' \
  "$ROUTEVOICE_REPO/pdks/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl" \
  monolithic-cloud-netgen.log > monolithic-cloud-console.log 2>&1
```

Use new log names; preserve the Mac's timeout. Require successful process completion, `Circuits match uniquely.`, no `Property errors`, and matched top-level pins. Archive the full logs, exact tool version, runtime, return code and input SHA256 values even if the attempt times out. Do not label an incomplete graph match or equal device counts as LVS success. No additional cloud command for a completed 20-tile macro exists yet, because that physical top remains unimplemented.
