set w $::env(W2B_DIR)
read_liberty $w/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib
read_verilog $w/tb/saif_probe_core.v
link_design saif_probe_core
read_saif -scope tb/dut $w/evidence/saif-api-probe.saif
report_activity_annotation
exit
