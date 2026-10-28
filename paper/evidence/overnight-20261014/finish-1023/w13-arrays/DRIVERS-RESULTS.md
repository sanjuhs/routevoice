# W13 driver, capture and escape results

**Components are staged for all 14 blocks and 81 bank instances. Complete peripheral qualification remains pending.** The original array artifacts and final inventory are unchanged.

## Published components

| Component | Delivery | Qualification |
|---|---|---|
| Four control shapes | `macros/<block>_drivers/{gds,lef,lib,v}` | Selected GF180 DRC0, exact-final full transistor LVS plus wrong-width negative, functional checks, nine-corner routed STA |
| Four output-escape and four WL/PC bridge masters | `macros/<block>_drivers/passive-escape/` | All4 shape seams DRC0 and full conductor graph/open-negative; native LEF/Liberty/Verilog readers pass |
| Shared capture80 candidate | `macros/<block>_drivers/capture80-candidate/` | DRC0, standalone full transistor LVS plus negative, functional latch checks, provisional timed Liberty; placement and full timing qualification pending; sampled SS150ns convergence passes |

Control publication is bound by `drivers-work/control/FINAL-CONTROL-ARTIFACTS.json`; capture and passive publication by `drivers-work/escape/{capture-staging-receipt,passive-staging-receipt}.json`. Passive mappings bind every original bank hash and check all 103,680 source-pin rectangles against actual GDS-derived bank pins. Signal bridge masters contain WL/PC only: the separate per-shape M5 supply-join/M4-pad/Via4 recipe is required. These are additive overlays to merge with the bank and control, not separate placeable blocks.

| Control rows | Setup slack ns | Hold slack ns | Slew/cap violations | Exact-final full native LVS |
|---:|---:|---:|---|---|
|256|77.179|0.604|0/0|PASS + wrong-width rejection|
|640|75.686|0.585|0/0|PASS + wrong-width rejection|
|768|73.931|0.570|0/0|PASS + wrong-width rejection|
|1280|56.425|0.520|0/0|PASS + wrong-width rejection|

Control STA uses150ns and9 corners. Receipts are `drivers-work/hier-r{256,640,768,1280}-final-v1/result.json`; all actual standard-cell, fillcap and PC child transistors are compared. R640/R768 each retain one explicit planning-fanout exception:16 logic inputs plus one passive antenna diode. Native readers check36 control Liberty views,4 Verilog views and4 repaired LEFs. Control area56.58470692395mm² is0.00070692395mm² above the exact56.584mm² reservation due to5nm ceiling, and0.41529307605mm² below the rounded57mm² budget.

## Whole-example physical and transistor evidence

All four R0 and proposed MX80 control/bank seams pass selected DRC, actual driver-terminal-to-WL/PC and common-PG connectivity,1280 output paths, and the WL0-open negative. Original bank/control/capture subtrees are proved identical before parent placement.

**The complete R256 R0 bank+control+escape now passes native transistor LVS and a wrong-width negative:** `drivers-work/hier-merged-r256-v4/result.json`. This example retains the old top-fed PC connection and has no capture or new bypass. Its input SHA is `fb252a0032a5281633664122150be4925869ae4f01b3181f1de1457c460886ea`. Provenance under `escape/control-integration-R256-v4/R0/` connects the labels-only port repair, exact bank-only flattening, and removal of only164,104 private OPEN annotations. Process geometry and every external port remain unchanged; this is not a device or LVS waiver.

Complete R256 MX80 bank/control/capture native LVS and wrong-width negative pass from `escape/control-integration-R256-v4/MX80/full-native-verification-v1/`. The independent reference retains all original devices and maps OUTi to capture Di. Verification geometry has zero whole-top process XOR over2,334,888 source polygons,72,625 retained labels and1,299 external ports. It still uses the old PC feed. The distinct `escape/control-integration-R256-MX80-bypass-v1/` candidate now passes selected DRC0 and the full conductor graph; all original cell geometry/text/instances are exact, with one published passive overlay added. Its optimized native input preserves all geometry and1,299 ports; direct full transistor LVS and wrong-width negative now pass in `drivers-work/hier-complete-r256-mx80-bypass-v1/result.json`. The old-feed MX80 pass is separately retained in `drivers-work/hier-complete-r256-mx80-v1/result.json`.

## Capture timing view and actual-load observations

The capture master is1050×80µm, including its46µm left extension, with1280 real latq_1 latches and16 buf_8 enable buffers. Standalone native LVS compares20,864 raw MOS (20,544 after parallel reduction),12,835 nets, with a wrong-width rejection. Functional tests cover transparent/update/hold behavior across8 patterns. Capture-only explicit input metal capacitance spans1.59375–17.54176fF; intrinsic gate charge is additional, so the old10fF receiver-output assumption is insufficient.

The staged SS3.00V125°C Liberty is explicitly provisional and `dont_use`:5,120 arcs using source-PDK sequential tables, actual standalone lumped metal capacitance and composed enable-buffer transport with zero wire resistance. Source tables are interpolated within their characterized axes; no safe-bound or full-PVT claim is made. Native checks verify state/port inventory and nonzero correct-polarity arcs. Transparent borrowing analysis is not certified. The original untimed view and failed parser/semantic experiments remain recorded. Method and evidence: `escape/capture-liberty-work/METHOD.md` and `escape/capture-provisional-artifact-receipt.json`.

The true maximum column has815 connected drains. Its actual native group plus escape, all1280 latches and16 enable buffers forms an185216-MOS conductor union with capacitance counted once. The bypass150ns sample atSS3.00V125°C passes functional checks for rows1279→1276, all1280 PC gates at each guard,64 enable edges across two cycles and96 Q-hold checks. Maximum observed enable delay is2.848707416ns, normalized slew3.067691129ns, and minimum sampled D-settle-to-enable-close interval16.151977816ns. Receipt: `timing/actual815-union-v1/ss3v-bypass150-max01-v1/{result,capture-timing-observations}.json`.

**The paired0.2ns→0.1ns numerical refinement passes unchanged criteria:**2.88949mV maximum sampled voltage difference≤3mV,10µV maximum PC-guard difference, and12.7904ps maximum observed D/Q/E/WL/PC crossing difference≤100ps. The accepted fine observation is bound to every capture delivery by `CAPTURE-SAMPLED-TIMING.json`; original GDS/LEF/Liberty/Verilog bytes are unchanged. The older300ns top-fed sample passed functional checks but failed both convergence comparisons: maximum voltage difference22.751mV for1ns→0.2ns and5.009mV for0.2ns→0.1ns, against the unchanged3mV criterion. Failures remain in both `ss3v-physical300-*/numerical-convergence.json` receipts. Actual-data evidence is sampled SS only; clock-wire resistance remains ideal, other1152 capture inputs are quiet, and112 bitline aggressors are ideal sources. This does not establish full timing characterization or all-row throughput.

## PC connection and remaining placement scope

Earlier five-corner driver screens omitted approximately2248µm of vertical M4 PC-spine resistance from the actual top injection. Their incomplete-model passes remain recorded. Corrected top-fed screens pass macro-pin/25ns gate-state checks, but internal8.6ns slew screening fails atSS125(13.266ns),TT25(9.198ns),FF125(11.302ns).

The new8µm M4 bypass occupies the existing60µm control gap and adds a lower PC feed at bank(5µm,10µm). All five standalone native-C/explicit-rail-R screens pass pin, internal8.6ns slew and24.099ns guard checks; receipts are `timing/pc-bypass-v1-*/result.json`. SS125 pin/gate slew is6.866/6.942ns. All four shapes now pass selected DRC, full conductor graph, bypass-only continuity, PC-open negative and native view readers. Separate `pc-bypass-candidate/` views are published in all14 block folders for81 instances; receipts are `control/pc-bypass-review/all-shapes-v1/{PUBLICATION,INTEGRITY,MX-placement-contract}.json`. Added native coupon capacitance is212.56133/503.58291/600.59257/988.621fF for256/640/768/1280 rows. This is passive geometry/interface qualification; the old control inventory remains immutable.

W15's authorized R0 placement and60µm reservation remain unchanged. MX orientation plus80µm capture reservation is a proposed placement change, not approved or applied. Standalone capture delivery does not adopt that placement.

## Retained failures and limits

Two-PC-buffer v3 failed actual nonlinear load despite its lumped NLDM pass; PC3 supersedes it. Original R1280 routing had2094 slew/66 cap failures, first repair92/3, final0/0. Missing PC export geometry produced1222 XOR differences before correction. The first merged R256 comparison failed missing promoted ports; labels-only repair and exact provenance now support the passing native result. Unfinished native permutation/import attempts and all numerical failures remain on record.

Selected GF180 DRC excludes density/antenna and is not foundry signoff. Provisional views omit switching-power characterization and distributed capture-clock resistance. No complete peripheral READY, full-recognizer closure, or all-row one-row-per-clock guarantee is claimed.

Completed inactive review/negative GDS copies were archived with verified SHA256 and pointers; `escape/inactive-seams-v1-archive.json` records1,139,048,998 bytes reclaimed. Active native inputs remain internal. No original array or final inventory was modified.

The shape-specific phase proposal is `timing/external-phase-contract-v2.json`: R1280 PC command edges30/149.8ns; R256/640/768 shift both by+20ns to50/169.8ns, while evaluation and capture commands remain unchanged. Nine-corner envelopes give24.099ns minimum PC-off-start guard and15.903ns minimum release guard. Controller implementation and full short-shape captured-data proof remain separate.

## Final component scope and area

The R256 complete bank/control/escape/capture example with the published PC bypass now has selected DRC0, exact full conductor connectivity and direct full native transistor LVS with a rejected wrong-width reference. Verification-only flattening and private-label omission preserve every process polygon and external port. This completes that example's transistor connectivity proof; MX80 placement remains unapproved and full PVT/load characterization remains outside the sampled result.

Short-shape SS2.97V/125°C actual-load screens also pass pin/internal slew and24.099ns guard: R2566.040/6.066ns, R6406.352/6.398ns, R7686.456/6.508ns. These are distinct from the accepted SS3.00V captured-data simulation. The shape-specific external phase generator still needs implementation; no full short-shape captured-data result is claimed. Final timing detail: `drivers-work/timing/{RESULTS.md,results.json}`.

Original built-array area174.70862028mm² + control footprints56.58470692395mm² + proposed capture80 footprints81×1050×80µm²=6.804mm² gives **238.09732720395mm²**. Passive escape/bridge/bypass overlays add zero footprint inside the existing envelopes. This sum is not packed die area and capture80 adoption is pending. Using the original arrays'5nm-rounded LEF envelopes gives238.10058016395mm² instead. Per-block areas and both definitions are recorded in `drivers-work/escape/peripheral-area-v1.json`; original array reports are untouched.

All14 capture folders include `CAPTURE-SAMPLED-TIMING.json` and `CAPTURE-SOURCE-BINDING.json`, tying accepted sample results to exact delivered capture/control/escape/bypass source geometry and routing envelopes. Original component files and inventories remain unchanged. Scoped capture-candidate READY means research component with provisional Liberty and a passing sampled SS150ns case; it does not mean final placement adoption, whole-model timing closure or complete peripheral READY.
