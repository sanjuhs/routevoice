// W1 functional immutable ROM backend. No runtime write port.
// Accepted edge N -> held response at PRE N+1, matching mode0 host.
// POR clears the queue; warm reset fences acceptance/ACK and retains its payload.
// Native UINT8/metadata payloads are unchanged. This is not a custom macro PPA proof.
module rv_onchip_decoder_body_v1 #(
  parameter CROSS_COEFF_FILE = "/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/cross_coeff.hex",
  parameter CROSS_META_FILE = "/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/cross_meta.hex",
  parameter FF_UP_COEFF_FILE = "/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/ff_up_coeff.hex",
  parameter FF_DOWN_COEFF_FILE = "/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/ff_down_coeff.hex",
  parameter FF_UP_META_FILE = "/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/ff_up_meta.hex",
  parameter FF_DOWN_META_FILE = "/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/ff_down_meta.hex"
)(
  input wire clk, por_reset, warm_reset,
  input wire req_valid,
  output wire req_ready,
  input wire [31:0] req_tag,
  input wire [2:0] req_layer,
  input wire [2:0] req_role,
  input wire req_region,
  input wire [13:0] req_word,
  input wire [2:0] req_tile,
  output logic [2:0] rsp_tile,
  output wire idle,
  output logic fault,
  output logic rsp_valid,
  input wire rsp_ready,
  output logic [31:0] rsp_tag,
  output logic [2:0] rsp_layer,
  output logic [2:0] rsp_role,
  output logic rsp_region,
  output logic [13:0] rsp_word,
  output logic [255:0] rsp_data
);
  logic [255:0] cross_coeff [0:38399];
  initial $readmemh(CROSS_COEFF_FILE, cross_coeff);
  logic [255:0] cross_meta [0:959];
  initial $readmemh(CROSS_META_FILE, cross_meta);
  logic [255:0] ff_up_coeff [0:153599];
  initial $readmemh(FF_UP_COEFF_FILE, ff_up_coeff);
  logic [255:0] ff_down_coeff [0:76799];
  initial $readmemh(FF_DOWN_COEFF_FILE, ff_down_coeff);
  logic [255:0] ff_up_meta [0:7679];
  initial $readmemh(FF_UP_META_FILE, ff_up_meta);
  logic [255:0] ff_down_meta [0:959];
  initial $readmemh(FF_DOWN_META_FILE, ff_down_meta);
  wire available = !rsp_valid;
  assign req_ready = available;
  assign idle = available;
  logic legal;
  logic [255:0] selected;
  integer unsigned address;
  always_comb begin
    selected = '0;
    address = 0;
    legal = req_layer < 6 && req_role >= 4 &&
      ((req_role < 6 && req_tile == 0 && req_word < (req_region ? 80 : 3200)) ||
       (req_role == 6 && req_word < (req_region ? 160 : 3200)) ||
       (req_role == 7 && req_tile == 0 && req_word < (req_region ? 160 : 12800)));
    case (req_role)
      4,5: begin
        if (req_region) begin
          address = (32'(req_layer)*2 + 32'(req_role)-4)*80 + 32'(req_word);
          if (legal) selected = cross_meta[address];
        end else begin
          address = (32'(req_layer)*2 + 32'(req_role)-4)*3200 + 32'(req_word);
          if (legal) selected = cross_coeff[address];
        end
      end
      6: begin
        if (req_region) begin
          address = 32'(req_layer)*1280 + 32'(req_tile)*160 + 32'(req_word);
          if (legal) selected = ff_up_meta[address];
        end else begin
          address = (32'(req_layer)*320 + 32'(req_word)/10)*80 + 32'(req_tile)*10 + 32'(req_word)%10;
          if (legal) selected = ff_up_coeff[address];
        end
      end
      7: begin
        if (req_region) begin
          address = 32'(req_layer)*160 + 32'(req_word);
          if (legal) selected = ff_down_meta[address];
        end else begin
          address = 32'(req_layer)*12800 + 32'(req_word);
          if (legal) selected = ff_down_coeff[address];
        end
      end
      default: ;
    endcase
  end
  always_ff @(posedge clk) begin
    if (por_reset) begin
      rsp_valid <= 0; fault <= 0;
      rsp_tag <= 0; rsp_layer <= 0; rsp_role <= 0;
      rsp_region <= 0; rsp_word <= 0; rsp_data <= 0;
      rsp_tile <= 0;
    end else if (!warm_reset) begin
      if (rsp_valid && rsp_ready) rsp_valid <= 0;
      if (req_valid && req_ready) begin
        rsp_valid <= 1;
        rsp_tag <= req_tag; rsp_layer <= req_layer; rsp_role <= req_role;
        rsp_region <= req_region; rsp_word <= req_word; rsp_data <= selected;
        rsp_tile <= req_tile;
        if (!legal) fault <= 1;
      end
    end
  end
endmodule
