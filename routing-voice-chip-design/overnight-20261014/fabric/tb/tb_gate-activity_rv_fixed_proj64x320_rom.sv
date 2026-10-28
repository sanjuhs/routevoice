`timescale 1ns/1ps
`ifndef DUT
`define DUT rv_fixed_proj320_rom
`endif
`ifndef ROWS
`define ROWS 320
`endif
module tb;
localparam ROWS=`ROWS;
reg clk=0; always #100 clk=~clk;
reg rst_n=0,start=0,x_valid=0;
reg signed [8:0] x=0;
wire x_ready,busy,done;
reg [8:0] rd_addr=0;
wire signed [26:0] rd_data;
wire signed [17:0] asum;
wire [8:0] row_addr;
reg [1279:0] imem[0:319];
reg [40959:0] bmem[0:4];
wire [1279:0] idx_row=imem[row_addr];
wire [40959:0] book_row=bmem[row_addr[8:6]];
`DUT dut(.clk(clk),.rst_n(rst_n),.start(start),.x(x),.x_valid(x_valid),.x_ready(x_ready),
.busy(busy),.done(done),.rd_addr(rd_addr),.rd_data(rd_data),.asum(asum),.row_addr(row_addr)
`ifdef EXTERNAL
,.idx_row(idx_row),.book_row(book_row)
`endif
);
reg [8:0] xs[0:32*ROWS-1];
reg [26:0] ys[0:32*320-1];
reg [17:0] sums[0:31];
integer v,k,n,checks=0,cycle=0,t0,stalls=0;
reg [8:0] oldrow;
string filename,tracefile;
reg trace_on=0;
always @(posedge clk) cycle<=cycle+1;
task tick; begin @(posedge clk); #1; end endtask
task begin_vector; begin
 @(negedge clk);start=1;x_valid=0; tick();
 if(!busy || !x_ready || row_addr!=0 || asum!=0) $fatal(1,"bad start");
 t0=cycle; @(negedge clk);start=0;
end endtask
initial begin
 $readmemh("vectors/idx.hex",imem);$readmemh("vectors/book.hex",bmem);
 $sformat(filename,"vectors/x%0d.hex",ROWS);$readmemh(filename,xs);
 $sformat(filename,"vectors/y%0d.hex",ROWS);$readmemh(filename,ys);
 $sformat(filename,"vectors/asum%0d.hex",ROWS);$readmemh(filename,sums);
 if($value$plusargs("vcd=%s",tracefile)) begin
   trace_on=1;$dumpfile(tracefile);

 end
 repeat(3) tick();@(negedge clk);rst_n=1;
 // Abort an actual partially filled pipeline and restart from cold state.
 begin_vector(); x_valid=1;x=-256; repeat(7) begin tick();@(negedge clk);end
 rst_n=0;tick(); if(busy||done||x_ready||asum!=0) $fatal(1,"reset abort failed");
 @(negedge clk);rst_n=1;x_valid=0;
 for(v=4;v<9;v=v+1) begin
   if(trace_on && v==4) $dumpvars(0,tb);
   
   begin_vector();stalls=0;
   for(k=0;k<ROWS;k=k+1) begin
     // Five traced vectors run at one accepted input/cycle. Other vectors stall.
     if((v<4 || v>=9) && (k%17==5)) begin
       oldrow=row_addr;x_valid=0;x=9'sd123;tick();
       if(row_addr!==oldrow || done) $fatal(1,"stall advanced row");
       stalls=stalls+1;@(negedge clk);
     end
     if(!x_ready || row_addr!==k[8:0]) $fatal(1,"bad ready/row v=%0d k=%0d row=%0d",v,k,row_addr);
     x=xs[v*ROWS+k];x_valid=1;
     // start while busy must be ignored.
     start=(k==10);
     tick();if(done) $fatal(1,"early done");@(negedge clk);start=0;
   end
   x_valid=0;tick();
   if(!done || busy || x_ready) $fatal(1,"missing done");
   if(cycle-t0 != ROWS+1+stalls) $fatal(1,"latency %0d",cycle-t0);
   if(asum!==sums[v]) $fatal(1,"asum mismatch v=%0d actual=%0d expected=%0d",v,asum,$signed(sums[v]));
   checks=checks+1;
   for(n=0;n<320;n=n+1) begin
     @(negedge clk);rd_addr=n[8:0];tick();
     if(rd_data!==ys[v*320+n]) $fatal(1,"output mismatch v=%0d n=%0d actual=%0d expected=%0d",v,n,rd_data,$signed(ys[v*320+n]));
     checks=checks+1;
   end
   rd_addr=511;#1;if(rd_data!==0) $fatal(1,"invalid read address");
   tick();if(done) $fatal(1,"done longer than pulse");
   $display("VECTOR_PASS v=%0d outputs=320 asum=1 stalls=%0d",v,stalls);
 end
 $display("W2-STATUS: GATE_ACTIVITY PASS vectors=5 random=5 checks=%0d failures=0 reset_abort=1",checks);
 $finish;
end
initial begin #2000000;$fatal(1,"timeout");end
endmodule
