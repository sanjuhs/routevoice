# Lead power check: W9 buffered 1280×320 ARRAY-PORT engine (`buf-v4`), pre-route

Run by the lead on the pod at 07:23–07:30 IST, 14 Oct 2026. **Pre-route, pre-repair, pre-CTS. Not signoff.**

## Inputs (hashes in `inputs.sha256`)

- **Database:** `engine-buffered/runs/buf-v4/23-openroad-globalplacement/rv_k64_array_port.odb`, the globally placed W9 netlist. Synthesis capped fanout at 16; there are 10 duplicated row registers and 19,045 ABC buffers. Post-placement repair (resizing) is not included.
- **Constraints:** `engine-buffered/evidence/ideal-prects.sdc`, W9's SDC with an ideal clock (0.15 ns transition). Everything else is unchanged at 20 ns.
- **Parasitics:** placement-estimated (`set_wire_rc` Metal2 signal / Metal4 clock).
- **Library:** `gf180mcu_fd_sc_mcu7t5v0` TT 25 °C 3.3 V.
- **Activity:** a gate-level SAIF of the mapped buf-v4 netlist running one real-activation projection, from `tb/activity_array_port.sv` (W9's bench).
  - The run passed: 320 outputs checked, 4,163 cycles, 0 stalls, 83.26 µs (`lead-gate-activity.log`).
  - The lead ran W9's already-compiled simulator directly, because W9's queue held it behind a redundant unsharded replay.
- **Script:** `power_bufv4.tcl`. Logs: `default.log` (no SAIF) and `saif.log`.

## Results

| Quantity | Value |
|---|---|
| Cell area (report_design_area) | 6.43 mm², 40% utilization |
| Pins annotated by the SAIF | **1,299,526 of 1,299,526 (0 unannotated)** |
| Power, real activity | **0.798 W** (internal 0.331, switching 0.467, leakage 0.00002). Combinational 82.5%, sequential 17.5% |
| Power, default activity (bound only) | 0.487 W |
| Energy per projection (0.798 W × 83.26 µs) | **66.4 µJ** |
| Energy per MAC (÷ 409,600) | **≈162 pJ** |
| Setup worst slack at 20 ns (ideal clock, before repair) | −125.2 ns → ≈6.9 MHz if unrepaired |
| Hold worst slack | +0.89 ns |

## Comparison

| Design | Power with real activity | pJ/MAC |
|---|---|---|
| Unbuffered `apnorepair`, post-CTS (`power/power_cts.log`) | 8.59 W, 75% of pins annotated | ≈1,750 |
| **Buffered `buf-v4`, placed (this run)** | **0.80 W, 100% of pins annotated** | **≈162** |
| W2 64×320 slice, repaired + CTS, 200 ns (`fabric/`) | 106 mW, 88% of pins annotated | ≈66 |

## Caveats

- **No clock tree.** In the W2 slice the clock tree was 27% of power, so expect roughly +30–40% here.
- **No resizing or repair, no routed parasitics.** A zero-delay SAIF means glitch power is not modelled.
- **Energy per projection is the robust number.** Dynamic energy per transition does not depend much on frequency. If repair leaves the clock at about 7 MHz, average power at the same work is about 0.11 W per engine.
- **Real-time power for the model's ≈0.6 GMAC/s of matrix work:** ≈0.1 W at 162 pJ/MAC, before the clock tree. This is an assumption-labelled extrapolation.
