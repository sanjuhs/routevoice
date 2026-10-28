`timescale 1ns/1ps
module tb;
reg a=0; wire y;
probe dut(.a(a),.y(y));
initial begin
 $dumpfile("actual-verilator.vcd"); $dumpvars(0,dut);
 #10 a=1; #10 a=0; #10 a=1; #10 a=0; #1 $finish;
end
endmodule
