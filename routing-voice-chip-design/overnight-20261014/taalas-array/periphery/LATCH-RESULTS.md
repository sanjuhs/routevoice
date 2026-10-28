# Standalone physical output latch strip

`handoff-latch128/w5_latch128.{gds,lef,def,nl.v,spice}` is the final routed 128-bit transparent latch block from `runs/latch128b-v1`. Its explicit `capture_gate` controls 128 GF180 `latq_1` cells through one buf20, four buf8 and sixteen buf4. Gate high is transparent; gate low holds. There is no reset. A first completed read must initialize outputs before consumption.

The outline is **450×80 µm = 36,000 µm²**; standard-cell area excluding fill is **7,345.14 µm²**. Ten isolated outlines sum to **0.360000 mm²**, or **0.87890625 µm² per projection selection**, for 1,280 output bits. This arithmetic excludes external routing, placement and capture-gate distribution; ten strips have not been integrated.

Selected official GF180 KLayout FEOL/BEOL/connectivity/offgrid checks report **0 markers**; density and antenna are excluded. Magic reports **0 DRC errors**. Netgen reports **0 total LVS errors**, with all device/net/property/unmatched-pin categories zero. Exported LEF has 259 pins including VDD/VSS. GDS and netlist hashes, exact DRC command and all results are in `latch-results.json`.

The routed gate-netlist functional simulation passes **1,411 checks**: repeated changes while the same gate interval stays open, walking ones/complements over every bit, closed-gate holds against input changes, and 128 random captures with repeated held-input changes. This distinguishes a transparent latch from an edge-triggered replacement. It is a zero-delay library functional simulation, not an analog or SDF timing test.

Extracted nine-corner Liberty/OpenRCX STA reports zero setup/hold violations and zero slew/capacitance violations. Corners are TT 3.30 V 25°C, SS 3.00 V 125°C and FF 3.60 V −40°C, each with min/nom/max wire RC. The declared capture gate has a 20 ns period and 50% duty cycle, input/output delays of 4 ns, 0.25 ns uncertainty and 10 fF output load. Positive-latch time borrowing is included; reported setup slack is zero and worst hold slack is 4.873560 ns. These are **assumed standalone gate-waveform constraints**, not evidence that the unknown macro phase controller or the complete read path meets 20 ns. SS 3.00 V Liberty is not the required SS 2.97 V transistor corner.

The original `runs/latch128-v1` is preserved: a buf20 driving sixteen buf4 caused one maximum-capacitance failure (maxSS 0.214366 pF versus 0.2 pF). Adding the four buf8 intermediate branches removed that measured failure in `latch128b-v1`.

Do not connect `array_read_enable` directly to `capture_gate` without a verified phase and timing contract. Closing must precede precharge-induced input corruption; opening, data settling and hold must satisfy the live W2b representative-capture path. This block supplies actual latch layout but does not complete those obligations. No latch energy or complete macro latency is claimed.

Reproduction from repository root (one thread, nice10, own temporary directory via wrapper):

```sh
bash overnight-20261014/taalas-array/periphery/run.sh latch128b
.venv/bin/python overnight-20261014/taalas-array/periphery/export_latch.py
.venv/bin/python overnight-20261014/taalas-array/periphery/test_latch.py
.venv/bin/python overnight-20261014/taalas-array/periphery/check_latch_drc.py
```

Use a fresh run tag when rerunning to preserve existing evidence: `run.sh latch128b v2`. The saved wrapper gives the exact Nix shell command; `latch-functional.json` and `latch-drc.json` retain expanded tool invocations. Selected extracted STA reports are under `runs/latch128b-v1/53-openroad-stapostpnr/`.
