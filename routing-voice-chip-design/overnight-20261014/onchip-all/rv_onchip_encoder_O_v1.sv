// Immutable behavioral ROM implementation; no runtime weight write port.
// Accepted edge N -> PRE N+3; payload held through backpressure.
// POR cancels pending transaction. Warm reset fences acceptance and ACK.
module rv_onchip_encoder_O_v1 #(parameter ROM_FILE="/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/encoder_O.hex")(
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
  input wire [8:0] req_row,
  output logic [8:0] rsp_row,
  output logic [2559:0] rsp_data
);
  logic [2559:0] rom [0:1919];
  initial $readmemh(ROM_FILE,rom);
  logic busy;
  logic [2:0] remaining;
  wire legal = req_layer<6 && req_row<320;
  wire [31:0] address = 32'(req_layer)*320+32'(req_row);
  assign req_ready = !busy;
  assign idle = !busy;
  assign rsp_valid = busy && remaining == 0;
  always_ff @(posedge clk) begin
    if (por_reset) begin
      busy<=0; remaining<=0; fault<=0; rsp_data<='0;
      rsp_layer<=0;
      rsp_tag<=0;
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
          rsp_row<=req_row;
        end
      end
    end
  end
endmodule
