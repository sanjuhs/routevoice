# Coverage only: synthesized SC-ROM netlist, no extracted power claim.
set w $::env(W2B_DIR)
read_liberty $w/pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib
read_verilog $w/runs/sc_rom-v2/06-yosys-synthesis/rv_k64_sc_rom.nl.v
link_design rv_k64_sc_rom
read_saif -scope tb/dut $w/evidence/sc_rom-mapped-speech.saif
report_activity_annotation > $w/evidence/sc_rom-synth-saif-annotation.rpt
report_units
exit
