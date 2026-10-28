# Coverage only on the placed netlist; no extracted power claim.
set w $::env(W2B_DIR)
read_liberty $w/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib
read_verilog $w/runs/array_port-v2/28-openroad-globalplacement/rv_k64_array_port.nl.v
link_design rv_k64_array_port
read_sdc $w/runs/array_port-v2/28-openroad-globalplacement/rv_k64_array_port.sdc
read_saif -scope tb/dut $w/evidence/array_port-mapped-speech.saif
report_activity_annotation > $w/evidence/array_port-placed-saif-annotation.rpt
report_units
exit
