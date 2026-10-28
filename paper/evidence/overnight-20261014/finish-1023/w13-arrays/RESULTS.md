# W13 whole-model Taalas index arrays

Updated 2026-10-20T22:44:56.147308+00:00. **complete research macro handoff.**

98 unique matrices, 31,457,280 four-bit selections (125,829,120 bits), 81 physical banks, all 14 floorplan fabric blocks, no padding. These are 98 matrices across six original shape classes, not 98 distinct dimensions.

All original packed hashes, complete codebook reconstruction versus executable K64 tensors, affine metadata, tied transpose and W6 image identity pass. [Source/address manifest](manifest-work/manifest.json) documents every matrix→bank→block span; [addressing and integration](INTEGRATION.md) defines the physical contract.

Completed bank checks: build 81/81; readback 81/81; selected DRC0 81/81; views 81/81; full LVS 6 named banks. Blocks READY 14/14.

| Block | Banks built/total | DRC0 | Area mm² | Floorplan mm² | Δ mm² | READY |
|---|---:|---:|---:|---:|---:|---|
| encoder_fabric_L0 | 3/3 | 3 | 6.803536 | 6.803536 | -0.000000 | yes |
| encoder_fabric_L1 | 3/3 | 3 | 6.803536 | 6.803536 | -0.000000 | yes |
| encoder_fabric_L2 | 3/3 | 3 | 6.803536 | 6.803536 | -0.000000 | yes |
| encoder_fabric_L3 | 3/3 | 3 | 6.803536 | 6.803536 | -0.000000 | yes |
| encoder_fabric_L4 | 3/3 | 3 | 6.803536 | 6.803536 | -0.000000 | yes |
| encoder_fabric_L5 | 3/3 | 3 | 6.803536 | 6.803536 | -0.000000 | yes |
| decoder_fabric_L0 | 5/5 | 5 | 10.269364 | 10.205304 | 0.064060 | yes |
| decoder_fabric_L1 | 5/5 | 5 | 10.269364 | 10.205304 | 0.064060 | yes |
| decoder_fabric_L2 | 5/5 | 5 | 10.269364 | 10.205304 | 0.064060 | yes |
| decoder_fabric_L3 | 5/5 | 5 | 10.269364 | 10.205304 | 0.064060 | yes |
| decoder_fabric_L4 | 5/5 | 5 | 10.269364 | 10.205304 | 0.064060 | yes |
| decoder_fabric_L5 | 5/5 | 5 | 10.269364 | 10.205304 | 0.064060 | yes |
| embedding_head_tied_once | 26/26 | 26 | 58.108086 | 58.056838 | 0.051248 | yes |
| producer_KV_and_positions | 7/7 | 7 | 14.163137 | 14.060640 | 0.102496 | yes |

Total realized bounding-rectangle area: **174.708620 mm²**; floorplan uniform-density estimate **174.170514 mm²**; difference **0.538106 mm²**. Physical area includes readout and local metal, not the separately budgeted external periphery. LEF origin preserves positive GDS coordinates; its envelope includes the tiny bottom-origin margin.

Total LEF placement envelope: 174.711873 mm². Sum with independent 30µm halos on every bank: 190.323862 mm² (engineering packing allowance, not measured placed area). W15 must repack the 81 actual rectangles; old aggregate block placements are not automatically valid.

## Per-bank verification

| Bank | Shape | Readback bits | DRC markers | Full LVS | Shape representative |
|---|---|---:|---:|---|---|
| W13_ENC0_B00 | 1280×320 | 1638400 | 0 | unique match + negative rejected | W13_ENC0_B00 |
| W13_ENC0_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC0_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC1_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC1_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC1_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC2_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC2_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC2_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC3_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC3_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC3_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC4_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC4_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC4_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC5_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC5_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_ENC5_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC0_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC0_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC0_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC0_B03 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC0_B04 | 640×320 | 819200 | 0 | unique match + negative rejected | W13_DEC0_B04 |
| W13_DEC1_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC1_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC1_B02 | 1280×320 | 1638400 | 0 | unique match + negative rejected | W13_ENC0_B00 |
| W13_DEC1_B03 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC1_B04 | 640×320 | 819200 | 0 | not run | W13_DEC0_B04 |
| W13_DEC2_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC2_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC2_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC2_B03 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC2_B04 | 640×320 | 819200 | 0 | not run | W13_DEC0_B04 |
| W13_DEC3_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC3_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC3_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC3_B03 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC3_B04 | 640×320 | 819200 | 0 | not run | W13_DEC0_B04 |
| W13_DEC4_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC4_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC4_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC4_B03 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC4_B04 | 640×320 | 819200 | 0 | not run | W13_DEC0_B04 |
| W13_DEC5_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC5_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC5_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC5_B03 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_DEC5_B04 | 640×320 | 819200 | 0 | not run | W13_DEC0_B04 |
| W13_EMB_B00 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B03 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B04 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B05 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B06 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B07 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B08 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B09 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B10 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B11 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B12 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B13 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B14 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B15 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B16 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B17 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B18 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B19 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B20 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B21 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B22 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B23 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B24 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_EMB_B25 | 768×320 | 983040 | 0 | unique match + negative rejected | W13_EMB_B25 |
| W13_PROD_B00 | 1280×320 | 1638400 | 0 | unique match + negative rejected | W13_ENC0_B00 |
| W13_PROD_B01 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_PROD_B02 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_PROD_B03 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_PROD_B04 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_PROD_B05 | 1280×320 | 1638400 | 0 | not run | W13_ENC0_B00 |
| W13_PROD_B06 | 256×320 | 327680 | 0 | unique match + negative rejected | W13_PROD_B06 |

## Qualification boundaries

- Selected research GF180 DRC excludes density and antenna; no foundry signoff.
- Stored-address branch: four NMOS bit cells per selection, analog receivers and local/common metal.
- Provisional Liberty proxy, no new SPICE timing characterization, no power model.
- External control decoder/WL/PC drivers, latches, output escape, numerical codebooks/products, dynamic attention/state and whole-chip PDN remain outside macro.
- Flat packing requires explicit controller address translation; no current RTL integration claim.
- W15 must place 81 real rectangles and budget interbank routing/halos; area sum does not prove previous block rectangles or die placement still fit.
- One tied embedding/head array requires access arbitration; no concurrent transpose/gather port.
- Full LVS credited only to named physical banks. Those banks contain spans from all original matrix shape classes; this is not full LVS of each original matrix. Other banks have full readback and DRC, and physical shape representative coverage.

Deliverables are in `macros/<block>/{gds,lef,lib,v}` as individual banks. Completed GDS offloaded for the disk reserve has checksummed `.gds.pointer.json` files; `GDS-LOCATIONS.json` resolves each actual artifact and marks SSD sources that need internal staging before active EDA, with evidence in `runs/<bank>/`, source provenance in `manifest-work/`, and native LVS in `lvs-work/`. Existing W5/W6 artifacts remain read-only. All active compute is internal, local and limited to 6 cores; 22 GiB free disk is guarded.

Earlier/native failures, if any, are preserved at their original paths. No whole-chip fit, sub-watt or complete-recognizer signoff follows from this bank handoff.

Combined native view load and exact cell/pin retention: **PASS (81 macros in each tool)** in OpenSTA, OpenROAD and Yosys. See `complete-view-checks/results.json`. The first checker run is preserved in `complete-view-checks-v1-failed/`: it assumed fully qualified OpenSTA pin names, while that API returns local pin names. Correcting the checker required no delivered-view changes.
