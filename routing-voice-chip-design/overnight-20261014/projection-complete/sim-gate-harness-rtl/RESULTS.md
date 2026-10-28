# Current gate-trace harness against RTL: PASS

Executed current `tb/gate_trace.sv` unchanged against the source list from `configs/sim-files.f`, replacing only the final testbench entry. No trace generation was enabled; compile records `VM_TRACE=0`. All pre-existing tests, RTL, vector files and bank model remain unchanged.

Native Verilator compile passed in 5.602 s with `-j 2`. Simulation passed in 1.248 s: one vector, 320 exact output comparisons, 11,843 cycles, no stalls, no reset-abort preamble. This rules out a generic cold-start harness deadlock in this RTL composition; it does not prove the mapped netlist or locate its failure. The disabled gate harness read counter prints zero and is not a read-count check.

At the source level, the first reset edge puts the wrapper in RELEASE. The following edge advances it to DONE. Start is asserted at 40 ns and accepted at 50 ns; on that same edge the wrapper can move DONE→IDLE because pre-edge busy is false, while the engine accepts start and enters LOAD. First activation acceptance is at 70 ns. The lack of the earlier abort preamble does not strand the RTL phase machine.

Evidence: `logs/compile.log`, `logs/run.log`, `result.json`, exact command JSONs, replacement file list and `source-hashes.json`. The supervisor enforced a 120 s total compile/run limit and 22 GiB internal-free-storage floor. No cloud EDA or new analog run occurred. Existing `$dumpfile`/`$dumpvars` statements were retained, but no tracing option was supplied.
