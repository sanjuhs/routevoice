# Coverage probe only; this is not routed power or extracted STA.
set w /workspace/rv/overnight-20261014/engine-buffered
set d $w/runs/buf-v4/23-openroad-globalplacement
read_liberty /workspace/rv/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib
read_db $d/rv_k64_array_port.odb
read_sdc $d/rv_k64_array_port.sdc
read_saif -scope tb/dut $w/evidence/array_port-mapped-speech-w9-frozen.saif
report_activity_annotation
report_activity_annotation > $w/evidence/placed-saif-annotation.rpt
