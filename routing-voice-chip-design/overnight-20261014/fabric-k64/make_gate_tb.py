"""Prepare an external-port-only checker for mapped/routed functional replay."""
from pathlib import Path
W=Path(__file__).resolve().parent
for v in ['array_port','sc_rom']:
 s=(W/'tb'/f'{v}.sv').read_text()
 s=s.replace('assign array_row=dut.array_row;assign array_read_enable=dut.array_read_enable;','assign array_row=0;assign array_read_enable=0;')
 a=s.index(' for(s=1;s<=4;s=s+1)begin');b=s.index(' for(v=0;v<54;v=v+1)begin',a)
 s=s[:a]+''' // Reset with zero, one and multiple accepted activations, then during held output.
 for(s=1;s<=4;s=s+1)begin
  @(negedge clk);start=1;step_enable=1;tick;
  @(negedge clk);start=0;in_valid=1;in_data=-9'sd255;out_ready=0;
  if(s<4)repeat(s==1?1:(s==2?2:50))begin tick;@(negedge clk);end
  else while(!out_valid)begin tick;@(negedge clk);end
  clear_reset;
 end
'''+s[b:]
 a=s.index('   if(dut.projection.integer_valid)begin') if '   if(dut.projection.integer_valid)begin' in s else s.index('if(dut.projection.integer_valid)begin')
 b=s.index(' if(out_valid)begin',a)
 s=s[:a]+s[b:]
 s=s.replace('if(integer_checks!=17280)$fatal(1,"integer count");','')
 if v=='sc_rom':s=s.replace('reads!=1280||','')
 s=s.replace('PASS vectors=54 outputs=17280','PASS gate vectors=54 outputs=17280')
 (W/'tb'/f'gate_{v}.sv').write_text(s)
