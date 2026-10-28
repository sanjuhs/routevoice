// W1 functional immutable ROM backend. No runtime write port.
// Accepted edge N -> held response at PRE N+1, matching mode0 host.
// POR clears the queue; warm reset fences acceptance/ACK and retains its payload.
// Native UINT8/metadata payloads are unchanged. This is not a custom macro PPA proof.
module rv_onchip_decoder_self_v1 #(
  parameter SELF_COEFF_FILE = "/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/self_coeff.hex",
  parameter SELF_META_FILE = "/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/self_meta.hex"
)(
  input wire clk, por_reset, warm_reset,
  input wire req_valid,
  output wire req_ready,
  input wire [31:0] req_tag,
  input wire [2:0] req_layer,
  input wire [1:0] req_role,
  input wire req_region,
  input wire [11:0] req_word,
  output wire idle,
  output logic fault,
  output logic rsp_valid,
  input wire rsp_ready,
  output logic [31:0] rsp_tag,
  output logic [2:0] rsp_layer,
  output logic [1:0] rsp_role,
  output logic rsp_region,
  output logic [11:0] rsp_word,
  output logic [255:0] rsp_data
);
  logic [255:0] self_coeff [0:76799];
  initial $readmemh(SELF_COEFF_FILE, self_coeff);
  logic [255:0] self_meta [0:1919];
  initial $readmemh(SELF_META_FILE, self_meta);
  wire available = !rsp_valid;
  assign req_ready = available;
  assign idle = available;
  logic legal;
  logic [255:0] selected;
  integer unsigned address;
  always_comb begin
    selected = '0;
    address = 0;
    legal = req_layer < 6 && req_word < (req_region ? 80 : 3200);
    if (req_region) begin
      address = (32'(req_layer)*4 + 32'(req_role))*80 + 32'(req_word);
      if (legal) selected = self_meta[address];
    end else begin
      address = (32'(req_layer)*4 + 32'(req_role))*3200 + 32'(req_word);
      if (legal) selected = self_coeff[address];
    end
  end
  always_ff @(posedge clk) begin
    if (por_reset) begin
      rsp_valid <= 0; fault <= 0;
      rsp_tag <= 0; rsp_layer <= 0; rsp_role <= 0;
      rsp_region <= 0; rsp_word <= 0; rsp_data <= 0;

    end else if (!warm_reset) begin
      if (rsp_valid && rsp_ready) rsp_valid <= 0;
      if (req_valid && req_ready) begin
        rsp_valid <= 1;
        rsp_tag <= req_tag; rsp_layer <= req_layer; rsp_role <= req_role;
        rsp_region <= req_region; rsp_word <= req_word; rsp_data <= selected;

        if (!legal) fault <= 1;
      end
    end
  end
endmodule
