module rv_k64_array_port(input wire clk,reset,start,step_enable,
input wire signed [8:0] in_data,input wire in_valid,output wire in_ready,
input wire [31:0] activation_scale,output wire busy,out_valid,input wire out_ready,
output wire [31:0] out_data,output wire [8:0] out_column,output wire [4:0] exceptions,
output wire [10:0] array_row,output wire array_read_enable,input wire [1279:0] frozen_index_bits);
wire [8:0] metadata_column;wire [31:0] weight_scale,bias;
fixed_metadata metadata(.column(metadata_column),.weight_scale(weight_scale),.bias(bias));
taalas_projection_affine projection(.*);
endmodule
