# Lead routed power, engine fix 2 (pipe2): routed ODB + nom extracted SPEF + 150 ns SDC + fresh real-speech gate SAIF
# of the pipe2 synthesized netlist (one projection, 4,165 cycles, 20 ns sim rescaled to 150 ns). TT 25C 3.3V.
read_liberty /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib
read_db /Users/sanju/rvssd/pipe2-local/runs/pipe2/55-odb-cellfrequencytables/rv_k64_array_port.odb
read_sdc /Users/sanju/rvssd/pipe2-local/runs/pipe2/54-openroad-fillinsertion/rv_k64_array_port.sdc
read_spef /Users/sanju/rvssd/pipe2-local/runs/pipe2/56-openroad-rcx/nom/rv_k64_array_port.nom.spef
puts "=== TIMING TT (extracted) ==="
report_worst_slack -max -digits 3
report_worst_slack -min -digits 3
puts "=== DEFAULT ACTIVITY ==="
report_power
read_saif -scope tb/dut /Users/sanju/rvssd/pipe2-local/power/activity-150ns.clean.saif
puts "=== ANNOTATION ==="
report_activity_annotation
puts "=== SAIF ACTIVITY ==="
report_power
