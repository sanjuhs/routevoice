// Complete integer projection output plus a tested FP32 scale/bias lane.
// Fixed-index array and per-column scale/bias storage are external interfaces.
module taalas_projection_affine(
 input wire clk, reset, start, step_enable,
 input wire signed [8:0] in_data, input wire in_valid, output wire in_ready,
 input wire [31:0] activation_scale,
 output wire busy, output wire out_valid, input wire out_ready,
 output wire [31:0] out_data, output wire [8:0] out_column,
 output wire [10:0] array_row, output wire array_read_enable,
 input wire [1279:0] frozen_index_bits,
 output wire [8:0] metadata_column,
 input wire [31:0] weight_scale, bias,
 output wire [4:0] exceptions
);
 reg active;
 reg [31:0] scale;
 reg [8:0] columns [0:2];
 wire integer_valid, integer_ready, core_busy;
 wire signed [31:0] integer_result;
 wire begin_vector=start&&!active;
 assign busy=active;
 assign out_column=columns[2];
 taalas_serial_engine engine(
  .clk(clk),.reset(reset),.start(begin_vector),.step_enable(step_enable),
  .in_data(in_data),.in_valid(in_valid),.in_ready(in_ready),.busy(core_busy),
  .out_valid(integer_valid),.out_ready(integer_ready),.out_data(integer_result),
  .out_column(metadata_column),.array_row(array_row),.array_read_enable(array_read_enable),
  .frozen_index_bits(frozen_index_bits));
 taalas_fp32_affine affine(
  .clk(clk),.rst_n(!reset),.in_valid(integer_valid),.in_ready(integer_ready),
  .integer_sum(integer_result),.activation_scale(scale),.weight_scale(weight_scale),.bias(bias),
  .out_valid(out_valid),.out_ready(out_ready),.result(out_data),.exceptions(exceptions));
 always @(posedge clk)begin
  if(reset)begin
   active<=0;scale<=0;columns[0]<=0;columns[1]<=0;columns[2]<=0;
  end else begin
   if(begin_vector)begin active<=1;scale<=activation_scale;end
   if(out_valid&&out_ready&&out_column==319)active<=0;
   if(integer_ready)begin
    columns[0]<=metadata_column;columns[1]<=columns[0];columns[2]<=columns[1];
   end
  end
 end
endmodule
