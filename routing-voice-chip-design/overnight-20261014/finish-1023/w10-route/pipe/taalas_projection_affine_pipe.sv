// Lead change (23 Oct 2026): taalas_projection_affine with ONE elastic pipeline register between the integer
// engine output (accum[column] - correction) and taalas_fp32_affine. It cuts the SS-critical path
// metadata.column -> {accum mux, zero-point, metadata ROM} -> correction -> iNToRecFN -> affine int_s0.
// weight_scale / bias / column travel with the data. Throughput is unchanged (1 output/cycle); latency is +1 cycle.
// Bench-visible probes keep their meaning: integer_valid / integer_ready / integer_result are the ENGINE handshake.
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
 // pipeline stage
 reg p_valid;
 reg signed [31:0] p_data;
 reg [31:0] p_weight_scale, p_bias;
 reg [8:0] p_column;
 wire affine_ready;
 assign integer_ready = !p_valid || affine_ready;
 assign busy=active;
 assign out_column=columns[2];
 taalas_serial_engine engine(
  .clk(clk),.reset(reset),.start(begin_vector),.step_enable(step_enable),
  .in_data(in_data),.in_valid(in_valid),.in_ready(in_ready),.busy(core_busy),
  .out_valid(integer_valid),.out_ready(integer_ready),.out_data(integer_result),
  .out_column(metadata_column),.array_row(array_row),.array_read_enable(array_read_enable),
  .frozen_index_bits(frozen_index_bits));
 taalas_fp32_affine affine(
  .clk(clk),.rst_n(!reset),.in_valid(p_valid),.in_ready(affine_ready),
  .integer_sum(p_data),.activation_scale(scale),.weight_scale(p_weight_scale),.bias(p_bias),
  .out_valid(out_valid),.out_ready(out_ready),.result(out_data),.exceptions(exceptions));
 always @(posedge clk)begin
  if(reset)begin
   active<=0;scale<=0;columns[0]<=0;columns[1]<=0;columns[2]<=0;
   p_valid<=0;p_data<=0;p_weight_scale<=0;p_bias<=0;p_column<=0;
  end else begin
   if(begin_vector)begin active<=1;scale<=activation_scale;end
   if(out_valid&&out_ready&&out_column==319)active<=0;
   if(integer_ready)begin
    p_valid<=integer_valid;
    if(integer_valid)begin p_data<=integer_result;p_weight_scale<=weight_scale;p_bias<=bias;p_column<=metadata_column;end
   end
   if(affine_ready)begin
    columns[0]<=p_column;columns[1]<=columns[0];columns[2]<=columns[1];
   end
  end
 end
endmodule
