# Run with OpenSTA or OpenROAD -exit after a routed netlist/SDC/SPEF exists.
# Required environment: W2B_LIB, W2B_NETLIST, W2B_TOP, W2B_SDC, W2B_SPEF,
# W2B_VCD and W2B_POWER_PREFIX. One Liberty/PVT/RC view per invocation.
read_liberty $::env(W2B_LIB)
read_verilog $::env(W2B_NETLIST)
link_design $::env(W2B_TOP)
read_sdc $::env(W2B_SDC)
read_spef $::env(W2B_SPEF)
report_power > $::env(W2B_POWER_PREFIX).default.rpt
read_vcd -scope tb/dut $::env(W2B_VCD)
report_activity_annotation > $::env(W2B_POWER_PREFIX).annotation.rpt
report_power > $::env(W2B_POWER_PREFIX).vcd.rpt
report_power -hierarchy > $::env(W2B_POWER_PREFIX).hierarchy.rpt
