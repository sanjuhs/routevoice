# W5 measured timing slice — 14 October 2026

A real-programmed 64-row × 32-lane slice passes the tested TT and SS hot read protocols. This is a separate-array/receiver lumped-capacitance measurement; full-macro timing and energy remain unmeasured.

The slice is tile 17, original rows 1088–1151, lanes 32–63. Across all 200 real 64×32 banks, it contains the maximum connected-drain population (50/64) at original lane 58 bit 3. That column also has the largest extracted incident bitline capacitance in this slice, 36.53484 fF. Selection by drain population is a load-risk proxy; full-matrix worst-case timing is not proven. Packed-image hash and all 409,600 W2b RTL choices match. All 8,192 extracted bit transistors match the intended real mask, device width and length. Selected KLayout FEOL/BEOL/connectivity/off-grid DRC has zero markers. This is graph comparison, not independent foundry LVS.

Eight local rows [0,1,6,7,15,31,47,63] are read at each corner. The maximum-load bit alternates 1→0→1→0 then remains 1 for the last four reads. All 64 physical rows and their parasitics are present. Each case checks 1,024 bits. Startup row 0 is excluded only from the seven-read energy average.

| Corner | Period ns | Capture after period start ns | Raw/restored failures | Latest sampled settled point after evaluate ns | Mean energy/32-lane read pJ | Mean energy/index pJ |
|---|---:|---:|---:|---:|---:|---:|
| typical 3.3V 25°C | 25 | 17.5 | 0/0 | 1.578 | 54.585 | 1.7058 |
| ss 2.97V 125°C | 25 | 17.5 | 0/0 | 2.424 | 44.405 | 1.3877 |
| typical 3.3V 25°C | 20 | 12.5 | 0/0 | 1.572 | 54.585 | 1.7058 |
| ss 2.97V 125°C | 20 | 12.5 | 0/0 | 2.424 | 44.405 | 1.3876 |

Read evaluation starts 2.5 ns after period start. Raw criteria are 70/30% VDD and restored criteria 90/10% VDD. The settling figure is a sampled point after the last threshold violation within the observed evaluation window, at 0.25 ns maximum transient step; it is not signed-off maximum delay. Energy integrates net ideal-source power for array+physical precharge/keeper/inverter strip, WL and PC sources and 10 fF output loads.

The actual ARRAY-PORT engine needs 1,280 index reads, not 4,160. It takes 4,160 integer or 4,163 FP32 cycles including load, accumulate and output. A 20 ns integrated period would yield 25.6 µs of index-read service and 83.26 µs engine duration; 25 ns yields 32 µs and 104.075 µs. The bounded slice passes the 20 ns test, but this cannot establish the complete macro meets the 20 ns capture edge or that the whole recognizer runs in real time.

Not included: 320-lane wordline fanout, physical decoder/PC/WL drivers, separate-layout join wires, distributed resistance, bank selection/latches, complete top-level control/PDN, statistical variation and whole-workload activity. The parent integrated geometry has different routing capacitance and must be characterized separately. Do not scale these measured slice energies into a measured macro/chip number.

Exact commands and retained failures: [COMMANDS.md](COMMANDS.md). Machine-readable results: [results.json](results.json). Source-reading scope: [READING.md](READING.md).

A subsequent physically joined bank0 layout was also measured. See [joined-bank0-v2/RESULTS.md](joined-bank0-v2/RESULTS.md) for its actual routing capacitance, DRC/device-graph checks and separate TT/SS measurements. It uses a different real image region; comparisons are not a same-image routing delta.
