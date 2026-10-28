// Immutable behavioral ROM implementation; no runtime weight write port.
// Accepted edge N -> PRE N+3; payload held through backpressure.
// POR cancels pending transaction. Warm reset fences acceptance and ACK.
module rv_onchip_encoder_head_v1 #(parameter ROM_FILE="/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/encoder_head.hex")(
  input wire clk, por_reset, warm_reset,
  input wire req_valid,
  output wire req_ready, idle,
  output logic fault,
  output wire rsp_valid,
  input wire rsp_ready,
  input wire [2:0] req_layer,
  output logic [2:0] rsp_layer,
  input wire [31:0] req_tag,
  output logic [31:0] rsp_tag,
  input wire [1:0] req_role,
  output logic [1:0] rsp_role,
  input wire [2:0] req_head,
  output logic [2:0] rsp_head,
  input wire [8:0] req_row,
  output logic [8:0] rsp_row,
  output logic [319:0] rsp_data
);
  logic [319:0] rom [0:46079];
  initial $readmemh(ROM_FILE,rom);
  logic busy;
  logic [2:0] remaining;
  wire legal = req_layer<6 && req_role<3 && req_row<320;
  wire [31:0] address = ((32'(req_layer)*3+32'(req_role))*8+32'(req_head))*320+32'(req_row);
  assign req_ready = !busy;
  assign idle = !busy;
  assign rsp_valid = busy && remaining == 0;
  always_ff @(posedge clk) begin
    if (por_reset) begin
      busy<=0; remaining<=0; fault<=0; rsp_data<='0;
      rsp_layer<=0;
      rsp_tag<=0;
      rsp_role<=0;
      rsp_head<=0;
      rsp_row<=0;
    end else begin
      if (busy && remaining != 0) remaining<=remaining-1'b1;
      if (!warm_reset) begin
        if (rsp_valid && rsp_ready) busy<=0;
        if (req_valid && req_ready) begin
          busy<=1; remaining<=3'd2;
          rsp_data<=legal ? rom[address] : '0;
          if (!legal) fault<=1;
          rsp_layer<=req_layer;
          rsp_tag<=req_tag;
          rsp_role<=req_role;
          rsp_head<=req_head;
          rsp_row<=req_row;
        end
      end
    end
  end
endmodule
