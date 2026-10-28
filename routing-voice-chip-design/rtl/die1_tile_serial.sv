module die1_tile_serial (input wire clk, input wire rst_n,
input wire in_valid, output wire in_ready,
input wire [71:0] in_data,
output reg out_valid, input wire out_ready,
output reg [167:0] out_data);
reg busy;
reg [3:0] bit_index;
reg [71:0] data_q;
assign in_ready = !busy && (!out_valid || out_ready);
reg signed [20:0] acc0;
wire signed [12:0] plane0 = ((((data_q[0+bit_index] ? 13'sd21 : 13'sd0) + (data_q[9+bit_index] ? (-13'sd12) : 13'sd0)) + ((data_q[18+bit_index] ? (-13'sd15) : 13'sd0) + (data_q[27+bit_index] ? 13'sd4 : 13'sd0))) + (((data_q[36+bit_index] ? (-13'sd27) : 13'sd0) + (data_q[45+bit_index] ? (-13'sd6) : 13'sd0)) + ((data_q[54+bit_index] ? (-13'sd6) : 13'sd0) + (data_q[63+bit_index] ? 13'sd3 : 13'sd0))));
wire signed [20:0] extended0 = {{8{plane0[12]}},plane0};
wire signed [20:0] next0 = bit_index == 8 ? -extended0 : ((acc0 <<< 1) + extended0);
reg signed [20:0] acc1;
wire signed [12:0] plane1 = ((((data_q[0+bit_index] ? 13'sd53 : 13'sd0) + (data_q[9+bit_index] ? (-13'sd25) : 13'sd0)) + ((data_q[18+bit_index] ? 13'sd8 : 13'sd0) + (data_q[27+bit_index] ? (-13'sd27) : 13'sd0))) + (((data_q[36+bit_index] ? (-13'sd28) : 13'sd0) + (data_q[45+bit_index] ? (-13'sd19) : 13'sd0)) + ((data_q[54+bit_index] ? (-13'sd7) : 13'sd0) + (data_q[63+bit_index] ? (-13'sd53) : 13'sd0))));
wire signed [20:0] extended1 = {{8{plane1[12]}},plane1};
wire signed [20:0] next1 = bit_index == 8 ? -extended1 : ((acc1 <<< 1) + extended1);
reg signed [20:0] acc2;
wire signed [12:0] plane2 = ((((data_q[0+bit_index] ? (-13'sd6) : 13'sd0) + (data_q[9+bit_index] ? (-13'sd47) : 13'sd0)) + ((data_q[18+bit_index] ? 13'sd43 : 13'sd0) + (data_q[27+bit_index] ? 13'sd2 : 13'sd0))) + (((data_q[36+bit_index] ? (-13'sd9) : 13'sd0) + (data_q[45+bit_index] ? (-13'sd11) : 13'sd0)) + ((data_q[54+bit_index] ? 13'sd16 : 13'sd0) + (data_q[63+bit_index] ? (-13'sd9) : 13'sd0))));
wire signed [20:0] extended2 = {{8{plane2[12]}},plane2};
wire signed [20:0] next2 = bit_index == 8 ? -extended2 : ((acc2 <<< 1) + extended2);
reg signed [20:0] acc3;
wire signed [12:0] plane3 = ((((data_q[0+bit_index] ? 13'sd26 : 13'sd0) + (data_q[9+bit_index] ? (-13'sd7) : 13'sd0)) + ((data_q[18+bit_index] ? 13'sd25 : 13'sd0) + (data_q[27+bit_index] ? 13'sd40 : 13'sd0))) + (((data_q[36+bit_index] ? (-13'sd42) : 13'sd0) + (data_q[45+bit_index] ? (-13'sd29) : 13'sd0)) + ((data_q[54+bit_index] ? 13'sd79 : 13'sd0) + (data_q[63+bit_index] ? (-13'sd46) : 13'sd0))));
wire signed [20:0] extended3 = {{8{plane3[12]}},plane3};
wire signed [20:0] next3 = bit_index == 8 ? -extended3 : ((acc3 <<< 1) + extended3);
reg signed [20:0] acc4;
wire signed [12:0] plane4 = ((((data_q[0+bit_index] ? (-13'sd29) : 13'sd0) + (data_q[9+bit_index] ? 13'sd17 : 13'sd0)) + ((data_q[18+bit_index] ? (-13'sd10) : 13'sd0) + (data_q[27+bit_index] ? (-13'sd13) : 13'sd0))) + (((data_q[36+bit_index] ? 13'sd100 : 13'sd0) + (data_q[45+bit_index] ? 13'sd4 : 13'sd0)) + ((data_q[54+bit_index] ? 13'sd25 : 13'sd0) + (data_q[63+bit_index] ? 13'sd12 : 13'sd0))));
wire signed [20:0] extended4 = {{8{plane4[12]}},plane4};
wire signed [20:0] next4 = bit_index == 8 ? -extended4 : ((acc4 <<< 1) + extended4);
reg signed [20:0] acc5;
wire signed [12:0] plane5 = ((((data_q[0+bit_index] ? 13'sd28 : 13'sd0) + (data_q[9+bit_index] ? (-13'sd27) : 13'sd0)) + ((data_q[18+bit_index] ? 13'sd2 : 13'sd0) + (data_q[27+bit_index] ? 13'sd3 : 13'sd0))) + (((data_q[36+bit_index] ? 13'sd39 : 13'sd0) + (data_q[45+bit_index] ? (-13'sd25) : 13'sd0)) + ((data_q[54+bit_index] ? (-13'sd6) : 13'sd0) + (data_q[63+bit_index] ? (-13'sd25) : 13'sd0))));
wire signed [20:0] extended5 = {{8{plane5[12]}},plane5};
wire signed [20:0] next5 = bit_index == 8 ? -extended5 : ((acc5 <<< 1) + extended5);
reg signed [20:0] acc6;
wire signed [12:0] plane6 = ((((data_q[0+bit_index] ? 13'sd49 : 13'sd0) + (data_q[9+bit_index] ? (-13'sd5) : 13'sd0)) + ((data_q[18+bit_index] ? (-13'sd17) : 13'sd0) + (data_q[27+bit_index] ? 13'sd31 : 13'sd0))) + (((data_q[36+bit_index] ? (-13'sd2) : 13'sd0) + (data_q[45+bit_index] ? 13'sd24 : 13'sd0)) + ((data_q[54+bit_index] ? (-13'sd6) : 13'sd0) + (data_q[63+bit_index] ? (-13'sd29) : 13'sd0))));
wire signed [20:0] extended6 = {{8{plane6[12]}},plane6};
wire signed [20:0] next6 = bit_index == 8 ? -extended6 : ((acc6 <<< 1) + extended6);
reg signed [20:0] acc7;
wire signed [12:0] plane7 = ((((data_q[0+bit_index] ? (-13'sd25) : 13'sd0) + (data_q[9+bit_index] ? (-13'sd23) : 13'sd0)) + ((data_q[18+bit_index] ? 13'sd10 : 13'sd0) + (data_q[27+bit_index] ? (-13'sd14) : 13'sd0))) + (((data_q[36+bit_index] ? 13'sd6 : 13'sd0) + (data_q[45+bit_index] ? 13'sd13 : 13'sd0)) + ((data_q[54+bit_index] ? (-13'sd4) : 13'sd0) + (data_q[63+bit_index] ? (-13'sd11) : 13'sd0))));
wire signed [20:0] extended7 = {{8{plane7[12]}},plane7};
wire signed [20:0] next7 = bit_index == 8 ? -extended7 : ((acc7 <<< 1) + extended7);
always @(posedge clk) begin
if (!rst_n) begin busy<=0; out_valid<=0; out_data<=0; data_q<=0; bit_index<=0;
acc0<=0;
acc1<=0;
acc2<=0;
acc3<=0;
acc4<=0;
acc5<=0;
acc6<=0;
acc7<=0;
end else begin
if (out_valid && out_ready) out_valid<=0;
if (in_valid && in_ready) begin data_q<=in_data; bit_index<=8; busy<=1; end
if (busy) begin
acc0<=next0;
acc1<=next1;
acc2<=next2;
acc3<=next3;
acc4<=next4;
acc5<=next5;
acc6<=next6;
acc7<=next7;
if (bit_index == 0) begin busy<=0; out_valid<=1;
out_data[0 +: 21]<=next0;
out_data[21 +: 21]<=next1;
out_data[42 +: 21]<=next2;
out_data[63 +: 21]<=next3;
out_data[84 +: 21]<=next4;
out_data[105 +: 21]<=next5;
out_data[126 +: 21]<=next6;
out_data[147 +: 21]<=next7;
end else bit_index<=bit_index-1;
end
end
end
endmodule
