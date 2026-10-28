# Physically decoded real K64 tile 0

**Scoped DRC and compositional transistor LVS pass.** The GDS contains the real first 64 projection rows, 320 lanes × 4 bits, 1,280 physical precharge/keeper/receiver channels, and ten frozen 120 × 120 µm local decoder macros. It remains a partial projection macro.

- Tile dimensions: **4669.7 × 240.8 µm**; area **1,124,463.76 µm²**; **54.905457 µm² per selection** including present periphery.
- Full tile and bank 0 scoped GF180 KLayout DRC: **0 markers**. FEOL, BEOL, connectivity and off-grid rules checked; antenna/density excluded.
- Actual Magic flat extraction: **111,460 transistors**. Each of ten components passes Netgen with a unique match and **zero property errors** against its distinct real-mask reference.
- Partition audit proves an exact disjoint cover of every extracted and reference transistor, no node merging, all 640 separate local wordlines, correct ownership of all 1,280 outputs, and exactly ten intended shared nets: VDD, VSS, PC, EVAL, ROW0–ROW5. Global power/control terminal fanout matches the independent reference.
- The complete analog portion also passes exact device-graph and dimension comparison: **87,040 transistors**.
- Reopened GDS readback: **20,480 selections / 81,920 bits, zero mismatches**, including 40,786 programmed Via1 ones.

The monolithic Netgen result is **bounded_incomplete** and is retained separately in `v1/netgen.log`. It is not presented as a monolithic LVS pass. The passing compositional proof covers the same full tile and all devices, including the 24,420 decoder and physical standard-cell transistors. Reference decoder connectivity comes from the separately qualified frozen handoff, expanded using the official GF180 transistor library; decoder logical correctness also relies on that worker's functional qualification.

The original 64 global M3 wordline wires were removed. A horizontally mirrored decoder occupies each bank's existing empty area. M2 source legs, M4 vertical tracks, and M5 target legs connect each decoder output to its own local array wordline. Shared M5 buses physically distribute address, evaluate, and supplies. Decoder M4 supply stripes physically reach those buses. There are no label-only joins.

**No decoded-tile timing or energy claim is made.** Prior ideal-source bank measurements do not qualify this integration. External ROW, EVAL and PC are explicit controls; phase generation, twenty-tile output selection/global wiring, output capture latches, and complete ARRAY-PORT integration remain missing. No decoded twenty-tile composition or LEF was produced.

Two auxiliary checker mistakes were corrected without changing any circuit: source/drain order in a fanout counter, and missing IDX ownership in the first component selector. Both failed versions are preserved. See `results.json`, `INTEGRATION.md`, `COMMANDS.md` and the original logs.
