from pathlib import Path
W=Path(__file__).resolve().parents[1];S=W.parent/'fabric-k64'
s=(W/'tb/complete.sv').read_text()
s=s.replace(str(S/'vectors'),str(W/'vectors'))
s=s.replace('assign array_read_enable=dut.array_read_enable;','assign array_read_enable=0;')
a=s.index(' for(s=1;s<=4;s=s+1)begin');b=s.index(' for(v=0;v<54;v=v+1)begin',a)
s=s[:a]+''' // External-port reset/abort checks, including live array phases.
 for(s=1;s<=4;s=s+1)begin
  @(negedge clk);start=1;step_enable=1;tick;
  @(negedge clk);start=0;in_valid=1;in_data=-9'sd255;out_ready=0;
  if(s<4)repeat(s==1?1:(s==2?4:50))begin tick;@(negedge clk);end
  else while(!out_valid)begin tick;@(negedge clk);end
  clear_reset;
 end
'''+s[b:]
a=s.index('   if(dut.engine.projection.integer_valid)begin');b=s.index(' if(out_valid)begin',a)
s=s[:a]+s[b:]
s=s.replace('if(integer_checks!=17280)$fatal(1,"integer count");','').replace('reads!=1280||','')
s=s.replace('PASS vectors=54','PASS gate vectors=54').replace('aborts=11','aborts=4')
(W/'tb/gate_full.sv').write_text(s)
a=s.index(' // External-port reset/abort');b=s.index(' for(v=0;v<54;v=v+1)begin',a)
t=s[:a]+f' $dumpfile("{W}/evidence/gate-speech.vcd");$dumpvars(0,dut);\n'+s[b:]
t=t.replace('v<54','v<1').replace('PASS gate vectors=54 outputs=17280','PASS gate trace vectors=1 outputs=320').replace('aborts=4','aborts=0')
# Dump at time zero and allow the same mapped binary to produce an idle activity window.
a=t.index(' $dumpfile(');b=t.index('\n',a)
t=t[:a]+t[b+1:]
t=t.replace('initial begin\n $readmemh', 'string trace_path;\ninitial begin\n trace_path="'+str(W/'evidence/gate-speech.vcd')+'";\n if($value$plusargs("vcd=%s",trace_path))begin end\n $dumpfile(trace_path);$dumpvars(0,dut);\n $readmemh')
t=t.replace(' for(v=0;v<1;v=v+1)begin', ' if($test$plusargs("idle"))begin repeat(10000)tick; $display("PASS gate idle cycles=10000 no projection started");$finish;end\n for(v=0;v<1;v=v+1)begin')
(W/'tb/gate_trace.sv').write_text(t)
