source $::env(SCRIPTS_DIR)/openroad/common/io.tcl
read_db /Users/sanju/rvssd/pipe-local/runs/pipe/44-openroad-resizertimingpostgrt/rv_k64_array_port.odb
read_liberty /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__ss_125C_3v00.lib
read_sdc /Users/sanju/rvssd/pipe-local/runs/pipe/44-openroad-resizertimingpostgrt/rv_k64_array_port.sdc
set ::tech [[ord::get_db] getTech]
set ::block [[[ord::get_db] getChip] getBlock]
source $::env(SCRIPTS_DIR)/openroad/common/set_rc.tcl
estimate_parasitics -placement
set_propagated_clock [all_clocks]
set n [get_nets -quiet metadata.column*]
puts "COLNETS [llength $n]"
if {[llength $n]} {
report_checks -path_delay max -through $n -group_path_count 3 -format end
report_checks -path_delay max -through $n -fields {net fanout} -digits 2
}
