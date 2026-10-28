# One selected PVT/RC corner per fresh STA process. Run through run_power.py.
foreach name {W8_LIB_LIST W8_MACRO_LIB W8_NETLIST W8_TOP W8_SDC W8_SPEF W8_VCD W8_OUT_DIR W8_SCOPE} {
 if {![info exists ::env($name)] || $::env($name) eq ""} { error "Missing environment variable $name" }
}
set output_dir $::env(W8_OUT_DIR)
foreach path [split $::env(W8_LIB_LIST) "\n"] {
 if {[string trim $path] ne ""} { read_liberty [string trim $path] }
}
read_liberty $::env(W8_MACRO_LIB)
read_verilog $::env(W8_NETLIST)
link_design $::env(W8_TOP)
read_sdc $::env(W8_SDC)
read_spef $::env(W8_SPEF)
sta::redirect_file_begin $output_dir/units.rpt
report_units
sta::redirect_file_end
report_parasitic_annotation > $output_dir/parasitic-annotation.rpt
report_power -digits 9 > $output_dir/default-power.rpt
read_vcd -scope $::env(W8_SCOPE) $::env(W8_VCD)
report_activity_annotation > $output_dir/activity-annotation.rpt
report_power -digits 9 > $output_dir/activity-power.rpt
# Instance ranking is optional: this local OpenSTA build traps on count > instances.
if {[info exists ::env(W8_HIGHEST_INSTANCES)] && $::env(W8_HIGHEST_INSTANCES) > 0} {
 report_power -highest_power_instances $::env(W8_HIGHEST_INSTANCES) -digits 9 > $output_dir/highest-instances.rpt
}
puts "W8-POWER: reports complete; macro internal energy remains unknown"
exit
