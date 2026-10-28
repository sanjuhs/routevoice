`timescale 1ns/1ps
module tb;
reg clk=0;always #10 clk=~clk;
reg reset=1,start=0,step_enable=1,in_valid=0,out_ready=0;
reg signed [8:0] in_data=0;reg [31:0] activation_scale=0;
wire in_ready,busy,out_valid,array_read_enable;wire [31:0] out_data;
wire [8:0] out_column,metadata_column;wire [10:0] array_row;
wire [1279:0] frozen_index_bits;wire [4:0] exceptions;
reg [31:0] as_mem[0:53];
rv_k64_array_port dut(.*);
taalas_index_fabric fabric(.row(array_row),.read_enable(array_read_enable),.frozen_index_bits(frozen_index_bits));
reg [8:0] input_mem[0:69119];reg [31:0] expected_mem[0:17279];
reg [31:0] int_expected[0:17279];
integer integer_checks=0;
integer v,r,c,elapsed,total=0,stalls=0,reads=0,s;
reg [31:0] rng=32'h20260919;reg stalled=0;reg [31:0] held;reg [8:0] held_column;
task tick;begin @(posedge clk);#1;end endtask
task clear_reset;begin
 @(negedge clk);reset=1;start=0;in_valid=0;out_ready=0;tick;
 if(busy||out_valid||in_ready||array_read_enable)$fatal(1,"reset outputs");
 @(negedge clk);reset=0;
end endtask
initial begin
 $readmemh("/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/vectors/integer-all.hex",int_expected);
 $readmemh("/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/vectors/inputs.hex",input_mem);$readmemh("/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/vectors/expected.hex",expected_mem);
 $readmemh("/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/vectors/activation-scales.hex",as_mem);
 tick;@(negedge clk);reset=0;
 for(s=1;s<=0;s=s+1)begin
  start=1;tick;@(negedge clk);start=0;in_valid=1;in_data=-9'sd255;
  while(dut.projection.engine.state!=s)begin tick;@(negedge clk);end
  if(s==4)repeat(3)begin tick;@(negedge clk);end
  clear_reset;
 end
 $dumpfile("/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/evidence/array_port-speech.vcd");$dumpvars(0,dut);
 for(v=0;v<1;v=v+1)begin
  @(negedge clk);start=1;activation_scale=as_mem[v];tick;
  @(negedge clk);start=0;activation_scale=0; // The vector scale must be latched.
  r=0;c=0;elapsed=0;reads=0;stalled=0;
  while(c<320)begin
   rng={rng[30:0],rng[31]^rng[21]^rng[1]^rng[0]};
   in_valid=r<1280&&(v==0||rng[0]||rng[1]);in_data=r<1280?input_mem[v*1280+r]:0;
   step_enable=v==0||rng[2]||rng[3];out_ready=v==0||rng[4];#1;
   if(stalled&&(!out_valid||out_data!==held||out_column!==held_column))$fatal(1,"unstable stalled float output");
   stalled=out_valid&&!out_ready;held=out_data;held_column=out_column;
   if(array_read_enable)reads=reads+1;
   if(dut.projection.integer_valid)begin
 if(dut.projection.integer_result!==int_expected[v*320+dut.metadata_column])$fatal(1,"integer numpy mismatch");
 if(dut.projection.integer_ready)integer_checks=integer_checks+1;
 end
 if(out_valid)begin
    if(out_column!==c||out_data!==expected_mem[v*320+c])$fatal(1,"float mismatch vector=%d column=%d got=%h expected=%h",v,c,out_data,expected_mem[v*320+c]);
    if(out_ready)c=c+1;
   end
   if(in_valid&&in_ready)r=r+1;
   if(stalled||!step_enable||(in_ready&&!in_valid))stalls=stalls+1;
   tick;elapsed=elapsed+1;if(elapsed>33280)$fatal(1,"timeout");
   @(negedge clk);
  end
  if(v==0&&elapsed!=4163)$fatal(1,"expected4163cycles got%d",elapsed);
  if(reads!=1280||r!=1280||busy||out_valid)$fatal(1,"completion accounting");
  if(v==0)$dumpoff;
 total=total+elapsed; $display("vector=%0d cycles=%0d reads=%0d",v,elapsed,reads);
 end
 if(integer_checks!=320)$fatal(1,"integer count");
 $display("PASS trace vectors=1 outputs=320 cycles=%d stalls=%d aborts=0 unstalled_cycles=4163",total,stalls);$finish;
end endmodule
