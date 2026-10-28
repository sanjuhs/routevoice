read_db $::env(W9_FANOUT_ODB)
set block [ord::get_db_block]
set out [open $::env(W9_FANOUT_REPORT) w]
puts $out "net\tloads\ttie_driver"
set max_nonclock 0
set max_nonclock_nontie 0
set over 0
foreach net [$block getNets] {
 set count 0
 set tie 0
 foreach iterm [$net getITerms] {
  if {[$iterm getIoType] == "INPUT"} {incr count}
  if {[$iterm getIoType] == "OUTPUT"} {
   set master [[[$iterm getInst] getMaster] getName]
   if {[string match *__tie* $master]} {set tie 1}
  }
 }
 set name [$net getName]
 if {$name == "clk"} {continue}
 if {$count > $max_nonclock} {set max_nonclock $count}
 if {!$tie && $count > $max_nonclock_nontie} {set max_nonclock_nontie $count}
 if {$count > 16} {incr over; puts $out "$name\t$count\t$tie"}
}
close $out
puts "W9-STATUS: placed max_nonclock=$max_nonclock max_nonclock_nontie=$max_nonclock_nontie nets_above_16=$over"
