# W6 bank interface and proof boundary

The bank stores the exact 1280 × 320 encoder block 0 FF project-out K64 index image. Logical row `r` maps directly to physical `WLr`. A programmed Via1 connects the cell drain to its bit line: reading discharges the bit line and makes the restored output 1. `OUT(4*c+b)` is bit `b` of output lane `c`. Four-bit indices still select UINT8 representatives downstream. Activation, product and accumulator precision, scales and zero points are unchanged.

## Physical interface

The GDS top is `PITCH_BANK_R1280` in [bank.gds](r1280-v2/bank.gds). Each 32-lane group has 128 native-pitch bit lines and 128 precharge/keeper/inverter readouts, arranged in eight rows of 16 circuits. For local bit column `bc`, receiver row is `bc % 8` and receiver column is `bc // 8`. Array origins are `(10 + 100*g, 126)` µm. The local bit-line pitch is 0.66 µm, with a 1 µm corridor per 16 lines: mean pitch 0.7225 µm. The topology allows all 1,280 bits to be sensed in parallel, without column-mux subphases.

`PC` is active-low precharge. Hold every WL low during precharge, and avoid overlap between precharge and evaluation. The GDS contains common WL/PC/VDD/VSS wiring, receiver taps and spines, local array ground straps, and Metal2/3/4 bit-line joins. Output access is at the receiver Metal2 pins inside the stack. Output escape, latches and downstream connections have not been routed. There is no qualified macro LEF/Liberty or complete phase controller.

## Sampled protocol and integration risk

The retained 60 ns pilot protocol turns PC off at 14 ns, commands WL at 18 ns, lowers WL at 57.8–58 ns, and returns PC low at 59.8–60 ns. The SPICE harness uses extracted stock drivers; these are not placed in the bank. The assumed output load is 10 fF per receiver. Consult [timing results](timing/RESULTS.md) for the latest cases and their exact loading scope. The local electrical slice does not establish simultaneous full-bank operation or supply integrity. A separate SS sensitivity with full-bank control capacitance and all 1,280 gate loads fails the 60 ns sequence: 63 precharge checks and all 10 phase checks fail, despite correct final data samples. A 120 ns schedule with longer guards passes this SS sensitivity, with 31.688 ns worst sampled settling after WL command; the TT companion was stopped by the disk guard before completion, so no paired TT/SS qualification follows for that sensitivity. The primary local TT result remains valid only within its smaller loading scope. The failed 60 ns sequence is retained; it cannot be used as a qualified bank-wide schedule.

W2b's existing INDEX operation captures representatives after combinational lookup and has no analog completion handshake. In the globally ranked column 1153 SS case, raw/restored settling reaches 23.443 ns after the WL command, and 18 of 160 sampled bit checks fail a 20 ns capture aperture. All final checks pass in that local slice at the tested 60 ns cycle. Interleaving cannot remove this latency failure. A slower clock, earlier read initiation, or a stallable request/completion interface requires separate implementation and verification.

Interleaving can change the initiation interval only after a bank reuse schedule is qualified. It does not remove read latency or the need for correct capture timing. No interleaving or bank replication is implemented or included in the measured footprint.

## Area accounting

Measured area includes cells, analog receivers and local/common joining metal. It excludes placed decoder/WL/PC drivers, phase control, output latches and escape, codebooks, shared products, accumulators, dynamic attention and writable state, and chip infrastructure. Add only components outside the measured footprint.

The 174.17 mm² uniform-model extrapolation does not allocate 98 tensor shapes, padding, extra ports, replication, tied-table transpose access or whole-chip placement. It is not a complete recognizer area or a die-fit result.
