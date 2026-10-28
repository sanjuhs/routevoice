# Lead power estimate (PRE-ROUTE, PRE-CTS): W9 buf-v4 placed database (fanout <= 16 at synthesis),
# ideal clock (0.15 ns transition, from W9's ideal-prects SDC), placement-estimated wire RC,
# gate-level SAIF of one real-activation projection. No clock-tree power. Not signoff.
set w /workspace/rv/overnight-20261014/engine-buffered
set lib /workspace/rv/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib
read_liberty $lib
read_db $w/runs/buf-v4/23-openroad-globalplacement/rv_k64_array_port.odb
read_sdc $w/evidence/ideal-prects.sdc
set_wire_rc -signal -layer Metal2
set_wire_rc -clock -layer Metal4
estimate_parasitics -placement
puts "=== DESIGN AREA ==="
report_design_area
puts "=== TIMING (ideal clock, placement RC, TT) ==="
report_worst_slack -max -digits 3
report_worst_slack -min -digits 3
report_tns -digits 3
puts "=== DEFAULT ACTIVITY ==="
report_power
if {[info exists ::env(SAIF)]} {
  read_saif -scope tb/dut $::env(SAIF)
  puts "=== ANNOTATION ==="
  report_activity_annotation
  puts "=== SAIF ACTIVITY ==="
  report_power
}
