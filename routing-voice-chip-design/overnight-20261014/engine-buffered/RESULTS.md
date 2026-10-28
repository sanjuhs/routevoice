# W9 buffered ARRAY-PORT engine

Updated 2026-10-14T02:12:23.254804+00:00. Status: **partial_in_progress**.

1280x320 ARRAY-PORT engine only. Custom index array, sense/read circuits, pads, upstream quantizer and recognizer excluded.

Latest completed step: `26-openroad-stamidpnr`; flow exit: `None`.

ABC buffering enabled, maximum fanout 16, sizing enabled, 20 ns clock. The W9-local synthesis wrapper adds `buffer -p` to cover primary inputs (including extracted register outputs). ABC-only driver uses the bare cell name. Ten RTL row-register copies each drive 32 lanes. Repair/CTS/route/signoff retained. DRT 12 threads, STA 4.

Pinned LibreLane supplied ABC a cell/pin driver (`inv_1/ZN`), which ABC could not resolve. Stock buffering and the first `-p` attempt therefore produced the same ineffective map. V4 fixes the ABC-only driver to the bare cell name and enables PI buffering; the 3,000-load smoke test reaches max fanout 16. Both failed maps and logs are preserved in `synthesis-checkpoint.tar.gz`; see `FAILURES.md`. The tested V4 combination also includes RTL duplication; no separate ablation is claimed.

## Completion

- rtl: passed
- configuration: complete
- synthesis: buf-v4/01-yosys-synthesis
- routing: None
- extraction: None
- sta: buf-v4/26-openroad-stamidpnr
- gate_replay: 54 vectors / 17280 outputs passed (serial)
- activity: vector0 / 320 outputs passed
- power: pending

## Area

| Measurement | Value |
|---|---|
| design__die__area | 16266600 µm² (16.266600 mm²) |
| design__core__area | 16083600 µm² (16.083600 mm²) |
| design__instance__area | 6902640 µm² (6.902640 mm²) |
| design__instance__area__stdcell | 6902640 µm² (6.902640 mm²) |
| design__instance__utilization | 0.429172 |

## Timing

Each corner identifies its last fresh STA source; missing corners are pending. Before post-PNR STA these are early diagnostics. Pre-CTS propagated-clock results include an unsynthesized clock network. Frequency formula does not certify hold, electrical or physical signoff.

| Corner | Setup WNS ns | Hold worst slack ns | 1000/(20−WNS) MHz | Source |
|---|---:|---:|---:|---|
| nom_tt_025C_3v30 | -171.658 | -177.617 | 5.217627231840049 | buf-v4/26-openroad-stamidpnr |
| nom_ss_125C_3v00 | -60.51570438268323 | 2.020295099508737 | 12.419937298779606 | buf-v4/07-openroad-staprepnr |
| nom_ff_n40C_3v60 | -2.5759892725807436 | 0.37401699462840776 | 44.29484741182668 | buf-v4/07-openroad-staprepnr |
| min_tt_025C_3v30 | None | None | None | None |
| min_ss_125C_3v00 | None | None | None | None |
| min_ff_n40C_3v60 | None | None | None | None |
| max_tt_025C_3v30 | None | None | None | None |
| max_ss_125C_3v00 | None | None | None | None |
| max_ff_n40C_3v60 | None | None | None | None |

## Fanout

Post-synthesis audit: `16` maximum non-clock load count.
Mapped buffers: 19045; nets above 16: 0; distinct duplicated row bit-6 nets: 10.

## Physical repair progress

{
  "iteration": 151000,
  "area_change_percent": 26.3,
  "resized_cells": 30139,
  "inserted_buffers": 23829,
  "repaired_nets": 19309,
  "remaining_nets": 191596,
  "source": "/workspace/rv/overnight-20261014/engine-buffered/runs/buf-v4-physical/01-openroad-repairdesignpostgpl/openroad-repairdesignpostgpl.log"
}

## Power and signoff

Routed SPEF + new mapped SAIF power is pending. No power or energy result claimed.
{
  "annotated_pins": 1299526,
  "unannotated_pins": 0,
  "coverage_fraction": 1.0,
  "stage": "buf-v4/23-openroad-globalplacement",
  "routed": false,
  "report": "/workspace/rv/overnight-20261014/engine-buffered/evidence/placed-saif-annotation.rpt"
}

Raw signoff counts and their completed stages are in `results.json`. Missing or skipped checks receive no pass credit.

Separate ideal-pre-CTS diagnostic: `stopped_redundant_diagnostic`. This declared STA-behavior deviation is not silently substituted for the requested-settings run; see `DIAGNOSTICS.md`.

The report is partial until routing, extracted STA, DRC/LVS/antenna checks, the full mapped replay and activity power have completed.

## Lead addendum (07:55 IST)

The lead measured pre-route power for this placed `buf-v4` database with the new mapped SAIF (100% annotated, consistent with `evidence/placed-saif-annotation.rpt`): **0.798 W, ≈66.4 µJ per projection, ≈162 pJ/MAC**. Ideal clock, no clock tree, no repair, placement RC. See `../power-bufv4/RESULTS.md`. The pod was terminated at 07:52; W9 run data is on the SSD (`routevoice-checkpoints/overnight-20261014/pod-final/engine-buffered/`). Routed signoff did not complete.
