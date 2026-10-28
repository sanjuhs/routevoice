# Lead routed power (local Mac): final routed ODB + nom extracted SPEF + signoff SDC (150 ns) + real-speech gate SAIF (150 ns time base,
# 2 Verilator cell-internal $-named instance blocks removed; see clean_saif.py). TT 25C 3.3V.
read_liberty /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib
read_db /Users/sanju/rvssd/hf-restore/ws/rv/overnight-20261014/finish-1023/w10-route/runs/full/final/odb/rv_k64_array_port.odb
read_sdc /Users/sanju/rvssd/hf-restore/ws/rv/overnight-20261014/finish-1023/w10-route/runs/full/final/sdc/rv_k64_array_port.sdc
read_spef /Users/sanju/rvssd/hf-restore/ws/rv/overnight-20261014/finish-1023/w10-route/runs/full/final/spef/nom/rv_k64_array_port.nom.spef
puts "=== TIMING TT (extracted) ==="
report_worst_slack -max -digits 3
report_worst_slack -min -digits 3
puts "=== DEFAULT ACTIVITY ==="
report_power
read_saif -scope tb/dut /Users/sanju/rvssd/routed-power/activity-150ns.clean.saif
puts "=== ANNOTATION ==="
report_activity_annotation
puts "=== SAIF ACTIVITY ==="
report_power
