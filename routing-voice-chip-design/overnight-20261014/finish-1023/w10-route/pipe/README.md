# Engine slow-corner fix: one pipeline register before the FP32 affine (lead, 23 Oct 2026)

## Why
After closure pass 2 (`../closure-lead/final-metrics-pass2.json`), the engine met 150 ns at TT (+56.7 ns) but failed at SS (nom −36.2 ns, max −53.1 ns). The same 30 endpoints failed in both passes, and repair could not shorten them.

Every failing path starts at the column register (`metadata.column`). It then goes through:
- the 320:1 accumulator mux;
- the zero-point and metadata lookups;
- the correction multiply and subtract;
- `iNToRecFN`.

It ends in the first-stage registers of `taalas_fp32_affine`. That is too much logic for one cycle at SS.

## Change
`taalas_projection_affine_pipe.sv` is a copy of `fabric-k64/rtl/taalas_projection_affine.sv`. It adds one elastic valid/ready register between the integer engine output and the affine stage:
- the data, weight scale, bias and column move through the register together;
- `integer_ready` (the engine's ready) is now `!p_valid || affine_ready`;
- throughput is unchanged at one output per cycle;
- each vector takes one more cycle.

The original file is untouched.

## RTL proof
`run-rtl.sh` runs Verilator 5.050 on the bench copy `tb_array_port_pipe.sv`. The bench differs from the original in one line: the vector-0 cycle check is 4,164 instead of 4,163, which is the added cycle.

Result (`rtl-sim.log`):
```
PASS vectors=54 outputs=17280 cycles=300964 stalls=104073 aborts=4
```
- All 17,280 FP32 outputs are bit-exact, and every engine integer result was checked at the handshake.
- The stall and abort tests pass.
- The original design took 300,952 cycles; this one takes 300,964.

## Physical flow
`run-flow.sh` runs the full local LibreLane flow, from synthesis through signoff. It uses the closure-pass-2 settings (`full-pipe-local.json`), with only the RTL file swapped. The run directory is `/Users/sanju/rvssd/pipe-local/runs/pipe` (SSD), and the log is `/Users/sanju/rvssd/pipe-local/flow.log`. Results are added below when the run finishes.
