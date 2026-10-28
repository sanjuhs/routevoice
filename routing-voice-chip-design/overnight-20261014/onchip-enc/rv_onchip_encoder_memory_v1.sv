// Immutable behavioral ROM implementation; no runtime weight write port.
// Accepted edge N -> PRE N+6; payload held through backpressure.
// POR cancels pending transaction. Warm reset fences acceptance and ACK.
module rv_onchip_encoder_memory_v1 #(parameter ROM_FILE="/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-enc/rom/encoder_memory.hex")(
  input wire clk, por_reset, warm_reset,
  input wire req_valid,
  output wire req_ready, idle,
  output logic fault,
  output wire rsp_valid,
  input wire rsp_ready,
  input wire [1:0] req_client,
  output logic [1:0] rsp_client,
  input wire [1:0] req_backing_owner,
  output logic [1:0] rsp_backing_owner,
  input wire [0:0] req_scalar,
  output logic [0:0] rsp_scalar,
  input wire [0:0] req_write,
  output logic [0:0] rsp_write,
  input wire [2:0] req_layer,
  output logic [2:0] rsp_layer,
  input wire [2:0] req_origin,
  output logic [2:0] rsp_origin,
  input wire [3:0] req_region,
  output logic [3:0] rsp_region,
  input wire [31:0] req_tag,
  output logic [31:0] rsp_tag,
  input wire [31:0] req_word,
  output logic [31:0] rsp_word,
  input wire [31:0] req_job,
  output logic [31:0] rsp_job,
  input wire [31:0] req_session,
  output logic [31:0] rsp_session,
  input wire [31:0] req_sequence,
  output logic [31:0] rsp_sequence,
  output logic [255:0] rsp_data
);
  logic [255:0] rom [0:160839];
  initial $readmemh(ROM_FILE,rom);
  logic busy;
  logic [2:0] remaining;
  wire legal = req_client==2 && req_backing_owner==2 && !req_scalar && !req_write && ((req_layer==6 && req_region==12 && req_word<40) || (req_layer<6 && ((req_region==4 && req_word<240) || (req_region==5 && req_word<80) || (req_region==6 && req_word<40) || (req_region==7 && req_word<40) || (req_region==8 && req_word<12800) || (req_region==9 && req_word<640) || (req_region==10 && req_word<12800) || (req_region==11 && req_word<160))));
  wire [31:0] address = req_layer==6 ? 160800+req_word : 32'(req_layer)*26800+req_word+(req_region==4 ? 32'd0 : req_region==5 ? 32'd240 : req_region==6 ? 32'd320 : req_region==7 ? 32'd360 : req_region==8 ? 32'd400 : req_region==9 ? 32'd13200 : req_region==10 ? 32'd13840 : req_region==11 ? 32'd26640 : 32'd0);
  assign req_ready = !busy;
  assign idle = !busy;
  assign rsp_valid = busy && remaining == 0;
  always_ff @(posedge clk) begin
    if (por_reset) begin
      busy<=0; remaining<=0; fault<=0; rsp_data<='0;
      rsp_client<=0;
      rsp_backing_owner<=0;
      rsp_scalar<=0;
      rsp_write<=0;
      rsp_layer<=0;
      rsp_origin<=0;
      rsp_region<=0;
      rsp_tag<=0;
      rsp_word<=0;
      rsp_job<=0;
      rsp_session<=0;
      rsp_sequence<=0;
    end else begin
      if (busy && remaining != 0) remaining<=remaining-1'b1;
      if (!warm_reset) begin
        if (rsp_valid && rsp_ready) busy<=0;
        if (req_valid && req_ready) begin
          busy<=1; remaining<=3'd5;
          rsp_data<=legal ? rom[address] : '0;
          if (!legal) fault<=1;
          rsp_client<=req_client;
          rsp_backing_owner<=req_backing_owner;
          rsp_scalar<=req_scalar;
          rsp_write<=req_write;
          rsp_layer<=req_layer;
          rsp_origin<=req_origin;
          rsp_region<=req_region;
          rsp_tag<=req_tag;
          rsp_word<=req_word;
          rsp_job<=req_job;
          rsp_session<=req_session;
          rsp_sequence<=req_sequence;
        end
      end
    end
  end
endmodule
