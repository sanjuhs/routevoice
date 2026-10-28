// IEEE binary32 output conversion for the existing integer projection.
// Three globally stalled stages, RNE, independent rounding at each operation.
// Weight selection and integer accumulation are outside this module.
module taalas_fp32_affine(
 input wire clk, rst_n,
 input wire in_valid, output wire in_ready,
 input wire signed [31:0] integer_sum,
 input wire [31:0] activation_scale, weight_scale, bias,
 output wire out_valid, input wire out_ready,
 output wire [31:0] result,
 output wire [4:0] exceptions
);
 reg [2:0] valid;
 wire advance = !valid[2] || out_ready;
 assign in_ready = rst_n && advance;
 assign out_valid = rst_n && valid[2];
 wire [32:0] int_rec, as_rec, ws_rec, bias_rec, combined_scale;
 wire [4:0] int_flags, scale_flags, mul_flags, add_flags;
 iNToRecFN #(32,8,24) convert(1'b1,1'b1,integer_sum,3'b000,int_rec,int_flags);
 fNToRecFN #(8,24) as_convert(activation_scale,as_rec);
 fNToRecFN #(8,24) ws_convert(weight_scale,ws_rec);
 fNToRecFN #(8,24) bias_convert(bias,bias_rec);
 mulRecFN #(8,24) combine_scales(1'b1,as_rec,ws_rec,3'b000,combined_scale,scale_flags);
 reg [32:0] int_s0, scale_s0, bias_s0, value_s1, bias_s1, result_s2;
 reg [4:0] flags_s0, flags_s1, flags_s2;
 wire [32:0] scaled, added;
 mulRecFN #(8,24) scale_sum(1'b1,int_s0,scale_s0,3'b000,scaled,mul_flags);
 addRecFN #(8,24) add_bias(1'b1,1'b0,value_s1,bias_s1,3'b000,added,add_flags);
 recFNToFN #(8,24) to_standard(result_s2,result);
 assign exceptions = flags_s2;
 always @(posedge clk) begin
  if (!rst_n) begin
   valid <= 0;
   int_s0 <= 0; scale_s0 <= 0; bias_s0 <= 0;
   value_s1 <= 0; bias_s1 <= 0; result_s2 <= 0;
   flags_s0 <= 0; flags_s1 <= 0; flags_s2 <= 0;
  end else if (advance) begin
   valid <= {valid[1:0],in_valid};
   if (in_valid) begin
    int_s0 <= int_rec; scale_s0 <= combined_scale; bias_s0 <= bias_rec;
    flags_s0 <= int_flags | scale_flags;
   end
   if (valid[0]) begin
    value_s1 <= scaled; bias_s1 <= bias_s0;
    flags_s1 <= flags_s0 | mul_flags;
   end
   if (valid[1]) begin
    result_s2 <= added; flags_s2 <= flags_s1 | add_flags;
   end
  end
 end
endmodule
