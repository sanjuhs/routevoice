# Use as STA_EXTRA_CORNER_TCL_FILE for a SECOND, extracted post-PNR STA run.
# The normal flow remains the default-activity baseline.
puts "W2_DEFAULT_ACTIVITY_POWER_BEGIN $corner_name"
report_power -corner $corner_name -digits 9
puts "W2_DEFAULT_ACTIVITY_POWER_END"
if {![info exists ::env(W2_VCD)]} { error "W2_VCD is required" }
read_vcd -scope tb.dut $::env(W2_VCD)
puts "W2_ACTIVITY_ANNOTATION_BEGIN"
report_activity_annotation
puts "W2_ACTIVITY_ANNOTATION_END"
puts "W2_VCD_ACTIVITY_POWER_BEGIN $corner_name"
report_power -corner $corner_name -digits 9
puts "W2_VCD_ACTIVITY_POWER_END"
# LibreLane's following standard report_power now reflects this activity.
