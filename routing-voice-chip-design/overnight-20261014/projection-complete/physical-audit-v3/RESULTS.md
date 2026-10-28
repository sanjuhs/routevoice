# W8 complete-v3 — saved floorplan and PDN audit

**Macro placement and physical PG hookup are evidenced in the saved PDN-stage ODB. This is not a routed-result claim.** Inspection used the completed `17-openroad-generatepdn` database and reports, with one remote CPU affinity, and did not modify the active run, configuration, source database or RTL. Required source-reading compliance continued from the completed W8 reading.

## Placement and units

The database uses **2,000 units/µm**. `bank` is `PITCH_BANK_R1280`, orientation `R0`, placement status `FIRM`, located at **(500, 1200) µm**. Its bounding box is **(500,1200)–(1504,3458.85) µm**, entirely inside the **4500 × 4500 µm** die. The die footprint is20.25mm², fixed before routing; it is not a measured successfully routed area.

The placement log's raw values1,000,000 and2,400,000 are database units. An initial interim message incorrectly interpreted them as1,000 and2,400µm; direct ODB units inspection corrected that immediately. The JSON records the correct conversion and there is no observed macro die escape.

## Actual macro supply connections

All2,563 macro terminals exist. VDD and VSS terminals are logically connected to nets `VDD` and `VSS` with POWER/GROUND types. The exported full Metal4 spines appear at global x=503µm (VDD) and501µm (VSS), with the original Metal5 pad shapes present at their upper end.

The audit inspected actual saved special-wire via definitions, origins and layer geometry. **16 same-net PDN vias per supply have positive-area metal overlap with an exported macro power pin**. Each receipt records the via name, global origin, bounding box and exact matching-layer rectangles. This establishes a physical metal-contact witness, beyond merely naming the power net. VDD contacts span y=1257.77..3457.85µm; VSS contacts span1261.07..3457.85µm.

The PDN stage reports both `[INFO PSM-0040] All shapes on net VDD are connected.` and the equivalent VSS statement. `VDD-grid-errors.rpt` and `VSS-grid-errors.rpt` contain only a newline. Native metrics report0errors/0warnings for the completed generation stage. These checks and the contact witnesses do not establish DRC/LVS, IR drop, electromigration, full-bank transistor connectivity or signal routability.

The actual database retains Metal3 wordline and Metal2 receiver-output access, and the selected first/last WL/OUT terminals plus PC are connected to their expected logical signal nets. Signal escape/routing is not qualified by this stage.

## Physical area reconciliation

These values are computed from **actual OpenDB master width × height × instance occurrences**, not inferred from a parameter ratio or from GPL's internal area message:

| Physical category | Instances | Area, mm² |
| --- | ---: | ---: |
| Logic and other ordinary standard cells |325,604|6.4347282944|
| Well taps |114,907|0.5044876928|
| Endcaps |3,442|0.0151117568|
| W6 macro LEF envelope |1|2.2678854000|
| **All instances** |**443,954**|**9.2222131440**|

Standard cells including tap/endcap total6.9543277440mm². Logic includes the actual engine and integration/control/periphery/latches; this audit does not split those circuits into separate functional area claims. The physical sum reproduces the saved PDN native metric total9,222,213.14µm² and is consistent with the reported Yosys logic area6,434,728µm² at this revision.

The GPL log separately prints **“Standard cells area:7351469.316um²”**. That is a different placer-internal accounting value, not this master-geometry sum and not a demonstrated Liberty-versus-LEF discrepancy. Resolved `GPL_CELL_PADDING=0` and `DPL_CELL_PADDING=0`, so configured cell padding does not explain it. Its internal mechanism was not investigated further in this bounded audit; do not substitute that value into the physical area breakdown. Raw lines are preserved in `gpl-area-source.txt`.

## Artifacts and scope

- `odb-inspection.json`: macro coordinates/selected pin geometry, PG net statistics, individual same-net via contact witnesses, source ODB SHA-256 and CPU affinity.
- `physical-area.json`: exact physical category sums and every master count/dimension.
- `pdn-stage/`: copied native PG reports, log, metrics, configuration and command.
- `macro-pdn-evidence.svg` and `macro-pdn-evidence.svg.png`: geometry-derived preview; other cells and signal routes are deliberately not drawn.
- `inspect_odb.py`: reproducible read-only extraction; the source ODB remained on the pod because it exceeds200MB.

The generator was run under one CPU affinity. The native wrapper emits `.openroad ignored with -python`; this is separate from the completed PDN stage's zero-warning metric. Local Matplotlib/Pillow were unavailable, so the retained first render script was replaced with a dependency-free SVG generator and native Quick Look rasterization. PNG layout was visually reviewed.

No routed completion, extracted timing closure, DRC/LVS pass, full-array power, complete recognizer fit or sub-watt result is inferred.
