# Standalone routed TT power. No flow io helpers; every input is explicit.
read_liberty $::env(W9_LIB)
read_db $::env(W9_ODB)
read_sdc $::env(W9_SDC)
read_spef $::env(W9_SPEF)
set_propagated_clock [all_clocks]
report_units
puts {=== DEFAULT ACTIVITY POWER ===}
report_power
read_saif -scope tb/dut $::env(W9_SAIF)
puts {=== SAIF ANNOTATION ===}
report_activity_annotation
report_activity_annotation > $::env(W9_PREFIX).annotation.rpt
puts {=== REAL-ACTIVITY POWER ===}
report_power
report_power > $::env(W9_PREFIX).power.rpt
report_power -highest_power_instances 20 > $::env(W9_PREFIX).highest.rpt
report_check_types -max_slew -max_capacitance -max_fanout -violators > $::env(W9_PREFIX).electrical.rpt
report_worst_slack -max
report_worst_slack -min
