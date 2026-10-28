`timescale 1ns/1ps
module tb;reg a=0;wire y;saif_probe_core dut(.*);initial begin $dumpfile("/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/evidence/saif-api-probe.saif");$dumpvars(0,dut);repeat(4)begin #10;a=~a;end #10;$finish;end endmodule
