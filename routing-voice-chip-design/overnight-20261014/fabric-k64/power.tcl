# Run with OpenSTA or OpenROAD -exit after a routed netlist/SDC/SPEF exists.
# Required environment: W2B_LIB, W2B_NETLIST, W2B_TOP, W2B_SDC, W2B_SPEF,
# W2B_POWER_PREFIX and either W2B_SAIF or W2B_VCD. One Liberty/PVT/RC view per invocation.
read_liberty $::env(W2B_LIB)
read_verilog $::env(W2B_NETLIST)
link_design $::env(W2B_TOP)
read_sdc $::env(W2B_SDC)
read_spef $::env(W2B_SPEF)
# This OpenSTA report_units command writes stdout and rejects redirection args.
# Preserve the invocation log as the units evidence.
report_units
report_power > $::env(W2B_POWER_PREFIX).default.rpt
if {[info exists ::env(W2B_SAIF)]} {
 read_saif -scope tb/dut $::env(W2B_SAIF)
} else {
 read_vcd -scope tb/dut $::env(W2B_VCD)
}
report_activity_annotation > $::env(W2B_POWER_PREFIX).annotation.rpt
report_power > $::env(W2B_POWER_PREFIX).activity.rpt
report_power -highest_power_instances 20 > $::env(W2B_POWER_PREFIX).highest-instances.rpt
