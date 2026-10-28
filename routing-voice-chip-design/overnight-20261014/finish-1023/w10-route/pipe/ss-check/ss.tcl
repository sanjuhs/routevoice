source $::env(SCRIPTS_DIR)/openroad/common/io.tcl
read_db /Users/sanju/rvssd/pipe-local/runs/pipe/44-openroad-resizertimingpostgrt/rv_k64_array_port.odb
read_liberty /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__ss_125C_3v00.lib
read_sdc /Users/sanju/rvssd/pipe-local/runs/pipe/44-openroad-resizertimingpostgrt/rv_k64_array_port.sdc
set ::tech [[ord::get_db] getTech]
set ::block [[[ord::get_db] getChip] getBlock]
source $::env(SCRIPTS_DIR)/openroad/common/set_rc.tcl
estimate_parasitics -placement
set_propagated_clock [all_clocks]
puts "SS_WNS [sta::worst_slack -max]"
report_tns
report_checks -path_delay max -group_path_count 5 -format end
report_checks -path_delay max -fields {fanout} -digits 2
