`timescale 1ns/1ps
module rv_source_position_immutable_rom_v1 #(
  parameter IMAGE_FILE = "source_position_163840x64.memh"
) (
  input wire clk,
  input wire por_reset,
  input wire common_reset,
  input wire request_valid,
  output wire request_ready,
  input wire [31:0] request_session,
  input wire [31:0] request_generation,
  input wire [31:0] request_tag,
  input wire [17:0] request_word,
  output wire idle,
  output wire response_valid,
  input wire response_ready,
  output reg [31:0] response_session,
  output reg [31:0] response_generation,
  output reg [31:0] response_tag,
  output reg [17:0] response_word,
  output reg [63:0] response_data,
  output wire request_rejected
);
  localparam [17:0] WORD_COUNT = 18'd163840;
  reg [63:0] image [0:163839];
  reg pending;
  reg [1:0] delay_edges;
  wire known_identity;
  wire legal_offer;
  wire offer;
  wire accept_request;
  wire accept_response;

  initial $readmemh(IMAGE_FILE, image);

  assign known_identity = ((^request_session !== 1'bx) &&
                           (^request_generation !== 1'bx) &&
                           (^request_tag !== 1'bx) &&
                           (^request_word !== 1'bx));
  assign legal_offer = known_identity &&
                       (request_generation === 32'd0) &&
                       (request_word < WORD_COUNT);
  assign offer = (request_valid === 1'b1);
  assign idle = !pending;
  assign request_ready = !por_reset && !common_reset && !pending &&
                         ((request_valid === 1'b0) || (offer && legal_offer));
  assign request_rejected = (request_valid !== 1'b0) &&
                            (request_valid !== 1'b1 || !legal_offer);
  assign response_valid = pending && (delay_edges == 2'd0);
  assign accept_request = offer && request_ready;
  assign accept_response = !por_reset && !common_reset &&
                           (response_valid === 1'b1) &&
                           (response_ready === 1'b1);

  always @(posedge clk or posedge por_reset) begin
    if (por_reset) begin
      pending <= 1'b0;
      delay_edges <= 2'd0;
      response_session <= 32'd0;
      response_generation <= 32'd0;
      response_tag <= 32'd0;
      response_word <= 18'd0;
      response_data <= 64'd0;
    end else begin
      if (accept_response) pending <= 1'b0;
      if (pending && delay_edges != 2'd0) delay_edges <= delay_edges - 2'd1;
      if (accept_request) begin
        pending <= 1'b1;
        delay_edges <= 2'd2;
        response_session <= request_session;
        response_generation <= request_generation;
        response_tag <= request_tag;
        response_word <= request_word;
        response_data <= image[request_word];
      end
    end
  end
endmodule
