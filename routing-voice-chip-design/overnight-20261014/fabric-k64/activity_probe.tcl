# Annotation-coverage probe only. No routed parasitics or power result.
set w $::env(W2B_DIR)
read_liberty $w/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib
read_verilog $w/runs/array_port-v2/28-openroad-globalplacement/rv_k64_array_port.nl.v
link_design rv_k64_array_port
read_sdc $w/runs/array_port-v2/28-openroad-globalplacement/rv_k64_array_port.sdc
read_vcd -scope tb/dut $w/evidence/array_port-speech-flat.vcd
report_activity_annotation > $w/evidence/array_port-pre-route-activity-annotation.rpt
exit
