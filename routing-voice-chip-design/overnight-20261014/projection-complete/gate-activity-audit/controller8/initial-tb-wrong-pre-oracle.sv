`timescale 1ns/1ps
module controller8(input clk,reset,in_valid,step_enable,busy,array_read_enable,engine_ready,
output in_ready,engine_step,output [7:0] phase_bus);
wire \engine.in_ready ;
wire \engine.in_valid ;
wire \engine.step_enable ;
wire \phase[0] ;
wire \phase[1] ;
wire \phase[2] ;
wire \phase[3] ;
wire \phase[4] ;
wire \phase[5] ;
wire \phase[6] ;
wire \phase[7] ;
wire _00000_ ;
wire _00001_ ;
wire _00002_ ;
wire _00003_ ;
wire _00004_ ;
wire _00005_ ;
wire _00006_ ;
wire _00007_ ;
wire _01571_ ;
wire _01583_ ;
wire _01584_ ;
wire _01585_ ;
wire _01586_ ;
wire _01587_ ;
wire _01588_ ;
wire _01589_ ;
wire _01590_ ;
wire _01644_ ;
assign \engine.in_ready =engine_ready;
assign engine_step=\engine.step_enable ;
assign phase_bus[0]=\phase[0] ;
assign phase_bus[1]=\phase[1] ;
assign phase_bus[2]=\phase[2] ;
assign phase_bus[3]=\phase[3] ;
assign phase_bus[4]=\phase[4] ;
assign phase_bus[5]=\phase[5] ;
assign phase_bus[6]=\phase[6] ;
assign phase_bus[7]=\phase[7] ;
  gf180mcu_fd_sc_mcu7t5v0__clkinv_1 _03944_ (
    .I(\phase[2] ),
    .ZN(_01571_)
  );
  gf180mcu_fd_sc_mcu7t5v0__clkinv_1 _03956_ (
    .I(reset),
    .ZN(_01583_)
  );
  gf180mcu_fd_sc_mcu7t5v0__clkinv_1 _03957_ (
    .I(\phase[0] ),
    .ZN(_01584_)
  );
  gf180mcu_fd_sc_mcu7t5v0__clkinv_1 _03958_ (
    .I(busy),
    .ZN(_01585_)
  );
  gf180mcu_fd_sc_mcu7t5v0__clkinv_1 _03959_ (
    .I(\phase[7] ),
    .ZN(_01586_)
  );
  gf180mcu_fd_sc_mcu7t5v0__and2_1 _03960_ (
    .A1(\phase[3] ),
    .A2(_01583_),
    .Z(_00004_)
  );
  gf180mcu_fd_sc_mcu7t5v0__nor2_1 _03961_ (
    .A1(_01571_),
    .A2(reset),
    .ZN(_00003_)
  );
  gf180mcu_fd_sc_mcu7t5v0__and2_1 _03962_ (
    .A1(\engine.in_ready ),
    .A2(\phase[1] ),
    .Z(in_ready)
  );
  gf180mcu_fd_sc_mcu7t5v0__and2_1 _03963_ (
    .A1(\phase[1] ),
    .A2(in_valid),
    .Z(\engine.in_valid )
  );
  gf180mcu_fd_sc_mcu7t5v0__nand3_1 _03964_ (
    .A1(\engine.in_ready ),
    .A2(\phase[1] ),
    .A3(in_valid),
    .ZN(_01587_)
  );
  gf180mcu_fd_sc_mcu7t5v0__nor2_1 _03965_ (
    .A1(reset),
    .A2(_01587_),
    .ZN(_00002_)
  );
  gf180mcu_fd_sc_mcu7t5v0__and2_1 _03966_ (
    .A1(_01583_),
    .A2(\phase[4] ),
    .Z(_00001_)
  );
  gf180mcu_fd_sc_mcu7t5v0__and2_1 _03967_ (
    .A1(_01583_),
    .A2(\phase[6] ),
    .Z(_00000_)
  );
  gf180mcu_fd_sc_mcu7t5v0__or4_1 _03968_ (
    .A1(\engine.in_ready ),
    .A2(_01585_),
    .A3(array_read_enable),
    .A4(_01586_),
    .Z(_01588_)
  );
  gf180mcu_fd_sc_mcu7t5v0__aoi21_1 _03969_ (
    .A1(_01584_),
    .A2(_01588_),
    .B(reset),
    .ZN(_00007_)
  );
  gf180mcu_fd_sc_mcu7t5v0__or2_1 _03970_ (
    .A1(reset),
    .A2(\phase[5] ),
    .Z(_00005_)
  );
  gf180mcu_fd_sc_mcu7t5v0__nand2_1 _03971_ (
    .A1(\phase[1] ),
    .A2(_01587_),
    .ZN(_01589_)
  );
  gf180mcu_fd_sc_mcu7t5v0__oai31_1 _03972_ (
    .A1(\engine.in_ready ),
    .A2(_01585_),
    .A3(array_read_enable),
    .B(\phase[7] ),
    .ZN(_01590_)
  );
  gf180mcu_fd_sc_mcu7t5v0__aoi21_1 _03973_ (
    .A1(_01589_),
    .A2(_01590_),
    .B(reset),
    .ZN(_00006_)
  );
  gf180mcu_fd_sc_mcu7t5v0__oai21_1 _05000_ (
    .A1(\phase[1] ),
    .A2(\phase[7] ),
    .B(step_enable),
    .ZN(_01644_)
  );
  gf180mcu_fd_sc_mcu7t5v0__clkinv_1 _05001_ (
    .I(_01644_),
    .ZN(\engine.step_enable )
  );
  gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10463_ (
    .CLK(clk),
    .D(_00005_),
    .Q(\phase[0] )
  );
  gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10464_ (
    .CLK(clk),
    .D(_00006_),
    .Q(\phase[1] )
  );
  gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10465_ (
    .CLK(clk),
    .D(_00000_),
    .Q(\phase[2] )
  );
  gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10466_ (
    .CLK(clk),
    .D(_00001_),
    .Q(\phase[3] )
  );
  gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10467_ (
    .CLK(clk),
    .D(_00002_),
    .Q(\phase[4] )
  );
  gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10468_ (
    .CLK(clk),
    .D(_00003_),
    .Q(\phase[5] )
  );
  gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10469_ (
    .CLK(clk),
    .D(_00004_),
    .Q(\phase[6] )
  );
  gf180mcu_fd_sc_mcu7t5v0__dffq_1 _10470_ (
    .CLK(clk),
    .D(_00007_),
    .Q(\phase[7] )
  );
endmodule
module tb;
reg clk=0;always #10 clk=~clk;
reg reset=1,in_valid=0,step_enable=1,busy=0,array_read_enable=0,engine_ready=0;
wire in_ready,engine_step;wire [7:0] phase_bus;
controller8 dut(.*);
initial begin #51;busy=1;engine_ready=1;#9;in_valid=1;end
initial begin
 $dumpfile("cascade.vcd");$dumpvars(0,tb);
 $monitor("t=%0t clk=%b reset=%b phase=%b engine_step=%b in_ready=%b",$time,clk,reset,phase_bus,engine_step,in_ready);
 #20;reset=0;
 #11;if(phase_bus!==8'h80)$fatal(1,"controller8 missed DONE at31ns: %b",phase_bus);
 #20;if(phase_bus!==8'h02)$fatal(1,"controller8 missed IDLE at51ns: %b",phase_bus);
 #20;if(phase_bus!==8'h04)$fatal(1,"controller8 missed PRE at71ns: %b",phase_bus);
 repeat(12)begin @(posedge clk);#1;if(!$onehot(phase_bus))$fatal(1,"controller8 invalid onehot %b",phase_bus);end
 $display("PASS exact mapped controller8 reset RELEASE->DONE->IDLE and 12 further onehot cycles");$finish;
end
endmodule
