`timescale 1ns/1ps
// Diagnostic only: exact GF180 cells and a two-FF token, not the projection.
module tb;
reg clk=0;
always #10 clk=~clk;
reg reset=1;
wire release_q, done_q, release_n, any_condition, done_d;
gf180mcu_fd_sc_mcu7t5v0__dffq_1 release_ff(.CLK(clk),.D(reset),.Q(release_q));
gf180mcu_fd_sc_mcu7t5v0__clkinv_1 release_inverse(.I(release_q),.ZN(release_n));
gf180mcu_fd_sc_mcu7t5v0__or4_1 conditions(.A1(1'b0),.A2(1'b1),.A3(1'b0),.A4(1'b0),.Z(any_condition));
gf180mcu_fd_sc_mcu7t5v0__aoi21_1 next_done(.A1(release_n),.A2(any_condition),.B(reset),.ZN(done_d));
gf180mcu_fd_sc_mcu7t5v0__dffq_1 done_ff(.CLK(clk),.D(done_d),.Q(done_q));
reg reference_release, reference_done;
always @(posedge clk) begin
 reference_release <= reset;
 reference_done <= reference_release && !reset;
end
initial begin
 $dumpfile("cascade.vcd"); $dumpvars(0,tb);
 $monitor("t=%0t clk=%b reset=%b release_q=%b done_d=%b done_q=%b reference_release=%b reference_done=%b", $time, clk,reset,release_q,done_d,done_q,reference_release,reference_done);
 #20 reset=0;
 #9;
 if(done_d!==1'b1) $fatal(1,"SETUP FAIL: D must be1 before30ns edge");
 #2;
 if(release_q!==1'b0 || done_q!==1'b1 || reference_done!==1'b1)
  $fatal(1,"CASCADE FAIL: at31ns release=%b done=%b reference=%b",release_q,done_q,reference_done);
 $display("PASS exact GF180 two-FF cascade: done_D=1 before30ns, done_Q=1 after edge");
 $finish;
end
endmodule
