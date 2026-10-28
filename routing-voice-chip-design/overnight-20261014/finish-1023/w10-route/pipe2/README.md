# Engine slow-corner fix 2: split the 320:1 output select (lead, 23 Oct 2026)

## Why fix 1 was not enough
Fix 1 (`../pipe`) added a register before the FP32 affine stage. We compared it with the old design using the same slow-corner check: post-global-route database, SS 125 °C, placement-estimated parasitics (`../pipe/ss-check`). The results:

| Design | Path | Estimated SS slack | Final routed SS slack |
|---|---|---|---|
| Old (closure pass 2) | worst | +36.0 ns | **−36.2 ns** |
| Fix 1 | through `metadata.column` | +60.8 ns | not run |
| Fix 1 | worst (now inside the FP32 scale multiply) | +49.9 ns | not run |

For the old design the estimate was about 72 ns too optimistic. The cause is long routed wires in the die-wide 320:1 `accum[column]` select. Fix 1 still has that select in one cycle, so it would likely still fail SS by about 10 ns. Its flow was therefore stopped at detailed routing; the run is kept on the SSD at `/Users/sanju/rvssd/pipe-local`.

## Change
`make_engine.py` derives `engine_local_pipe2.sv` (on the SSD at `/Users/sanju/rvssd/pipe-local/`) from `engine-buffered/rtl/engine_local.sv`. The original file is not edited. The changes:
- **Per-group lane register.** Each 32-lane group registers its own lane for the *look-ahead* column, which is `column+1` on an output handshake and `column` otherwise. The output is then a 10:1 select of these group registers.
- **Registered correction.** The zero-point correction `activation_sum × zero_point` is registered the same way.
- **New PREP state.** One PREP state between the last ACCUM and OUTPUT fills these registers for column 0.

Throughput is unchanged at one column per cycle. Combined with fix 1, latency is 4,165 cycles per vector instead of the original 4,163.

## RTL proof
`run-rtl.sh` runs the bench copy `tb_array_port_pipe2.sv`. The only bench change is the cycle check, now 4,165.
```
PASS vectors=54 outputs=17280 cycles=301005 stalls=104077 aborts=4
```

## Physical flow
`run-flow.sh` runs the full local flow, with the same settings as closure pass 2 and fix 1. The run directory is `/Users/sanju/rvssd/pipe2-local/runs/pipe2`.

## Results (23 Oct, local Mac, `/Users/sanju/rvssd/pipe2-local/runs/pipe2`)

| Check | Fix 2 | Old closure pass 2 |
|---|---|---|
| Global-route overflow | **9** | 575 |
| Detailed routing | **0 violations** (12 → 0), ≈1 h 15 m | 0 |
| Setup slack, nom TT (extracted SPEF, 150 ns) | **+67.6 ns** | +56.7 ns |
| Setup slack, nom SS | **+21.6 ns** | −36.2 ns |
| Setup slack, max SS (worst corner) | **+8.34 ns** | −53.1 ns |
| Setup violations, all 9 corners | **0** | 30–31 at SS |
| Hold, all 9 corners | **met** (worst +0.300 ns, max FF) | met |
| Max-cap / max-slew counts (worst corner) | 24,383 / 902,170 | 30,786 / 927,712 |

`evidence/sta-postpnr-summary.rpt` has every corner. The slew and capacitance-limit counts are the same open item as in every earlier run; they are not setup or hold failures.

### Activity-annotated routed power
1. **Activity trace.** A fresh zero-delay gate simulation of the fix-2 synthesized netlist ran one real-speech projection. All 320 FP32 outputs are bit-exact, in 4,165 cycles. The trace was recorded at 20 ns and rescaled to 150 ns. Details: `evidence/activity-results.json` and `activity-simulation.log`.
2. **Bench changes.** The bench and runner are copies of `../gate-support`. Only the expected cycle count changed (4,163 → 4,165).
3. **Power run.** It was read with `read_saif -scope tb/dut` against the routed ODB, the nominal extracted SPEF and the 150 ns SDC, at TT (`evidence/power-pipe2.log`).

| Quantity | Value |
|---|---|
| Pins annotated | 1,365,355 annotated, 656,169 not (**67.5%**; the unannotated pins are repair, antenna and diode cells absent from the synthesized netlist) |
| Power at 150 ns | **0.188 W** (sequential 24.3 mW, combinational 142 mW, clock 21.5 mW) |
| Energy per projection | 0.188 W × 4,165 × 150 ns ≈ **117 µJ** |
| Energy per MAC (÷ 409,600) | **≈287 pJ** (closure pass 2: 256 pJ) |

The ≈12% energy increase pays for meeting timing at SS. It comes from the 10 × 27-bit group registers, the registered correction, and the extra repair buffering.

### Signoff (flow finished 24 Oct ≈03:30 IST, exit 0, 30,681 s wall)
| Check | Result |
|---|---|
| Detailed-routing DRC | **0** |
| Magic DRC | **0** |
| KLayout DRC (main GF180 deck) | **0** |
| GDS XOR, Magic vs KLayout | **0** differences |
| Netgen LVS | **Circuits match uniquely**: 0 device/net/pin/property differences |
| Antenna | **11 nets / 12 pins open** (closure pass 2 had 4/4) |
| Die / utilization | 4,769.75 × 4,787.67 µm = 22.84 mm², 53.9% |
| Routed wire | 68.9 m |

Evidence: `evidence/manufacturability.rpt`, `evidence/final-metrics.json`. The run (51 GB, of which `final/` is 13 GB) is on the SSD at `/Users/sanju/rvssd/pipe2-local/runs/pipe2`. It is backed up, checksum-verified, to the public HF dataset `sanjuhs/routevoice-engine-fix2-20261024` (see `../../pipe2-hf-20261024/`).

The antenna item is closed by the run below.

## Antenna close-out (24 Oct evening, final signoff)
LibreLane's post-route antenna repair had stopped at its default 3 rounds while still converging (199 → 41 → 24 → 11 nets). `run-antenna.sh` reruns from the same detailed-routing input state (`runs/pipe2/46-openroad-detailedrouting/state_in.json`) with `full-pipe2-ant-local.json`. That config is identical to `full-pipe2-local.json` except `DRT_ANTENNA_REPAIR_ITERS: 10`. The design and all other settings are unchanged. Run directory: `/Users/sanju/rvssd/pipe2-local/runs/pipe2-ant`. Exit 0, 24,170 s wall: detailed routing 2 h 13 m, KLayout DRC 2 h 7 m.

Antenna repair rounds (`evidence-ant/antenna-repair-rounds.txt`): 199 → 41 → 24 → 11 → 8 → 5 → 5 → 5 → 1 → 1 → **0** (after round 10, confirmed by the separate antenna check). Each round adds diodes and re-routes locally; diodes went from 6,453 to 7,452.

| Check | Antenna close-out (final) | Fix 2 run above |
|---|---|---|
| Detailed-routing DRC | **0** | 0 |
| Antenna (separate check step) | **0 nets / 0 pins** | 11 / 12 |
| Magic DRC / KLayout DRC | **0 / 0** | 0 / 0 |
| GDS XOR, Magic vs KLayout | **0** | 0 |
| Netgen LVS | **Circuits match uniquely**, 0 differences | same |
| Disconnected pins / illegal overlaps / power-grid violations | **0 / 0 / 0** | 0 / 0 / 0 |
| Setup slack: nom TT / nom SS / max SS (worst) | **+67.5 / +21.4 / +8.10 ns** | +67.6 / +21.6 / +8.34 ns |
| Hold, worst (max FF) | **+0.324 ns** | +0.300 ns |
| Setup/hold violations, 9 corners | **0 / 0** | 0 / 0 |
| Max-cap / max-slew counts (worst corner) | 24,390 / 902,948 | 24,383 / 902,170 |
| Cells / die / utilization / wire | 1,146,232 / 22.84 mm² / 53.95% / 68.9 m | 1,145,233 / same / 53.9% / 68.9 m |
| Routed power, same SAIF (`evidence-ant/power-pipe2-ant.log`) | **0.188 W, ≈117 µJ/projection, ≈287 pJ/MAC**, 67.5% annotated | same |

The LibreLane manufacturability report says: Antenna Passed, LVS Passed, DRC Passed (`evidence-ant/manufacturability.rpt`). The other evidence is in `evidence-ant/`: `final-metrics.json`, `sta-postpnr-summary.rpt`, `lvs.netgen.json`, `lvs-tail.rpt` and `antenna-check.rpt`.

The run (46 GB) is backed up to the same HF dataset under `archives/pipe2-ant/` (record in `../../pipe2-ant-hf-20261024/`).

Remaining open item: the slew/cap-limit counts (as in every run). They do not cause setup or hold failures.
