# Exact activity annotation check only: no report_power or timing analysis.
if {[catch {
    foreach name {W8_LIB_LIST W8_MACRO_LIB W8_NETLIST W8_TOP W8_VCD W8_OUT_DIR} {
        if {![info exists ::env($name)] || $::env($name) eq ""} {
            error "Missing environment variable $name"
        }
    }
    foreach path [split $::env(W8_LIB_LIST) "\n"] {
        if {[string trim $path] ne ""} { read_liberty [string trim $path] }
    }
    read_liberty $::env(W8_MACRO_LIB)
    read_verilog $::env(W8_NETLIST)
    link_design $::env(W8_TOP)
    report_activity_annotation > $::env(W8_OUT_DIR)/before-vcd.rpt
    read_vcd -scope tb/dut $::env(W8_VCD)
    report_activity_annotation > $::env(W8_OUT_DIR)/activity-annotation.rpt
    puts "W8-ANNOTATION-ONLY: complete; no power or timing result requested"
} failure]} {
    puts stderr "W8-ANNOTATION-ONLY: ERROR $failure"
    exit 2
}
exit 0
