`timescale 1ns/1ps
module tb_source_position_immutable_rom_v1;
  reg clk;
  reg por_reset;
  reg common_reset;
  reg request_valid;
  wire request_ready;
  reg [31:0] request_session;
  reg [31:0] request_generation;
  reg [31:0] request_tag;
  reg [17:0] request_word;
  wire idle;
  wire response_valid;
  reg response_ready;
  wire [31:0] response_session;
  wire [31:0] response_generation;
  wire [31:0] response_tag;
  wire [17:0] response_word;
  wire [63:0] response_data;
  wire request_rejected;
  reg monitor_armed;
  integer legal_count;
  integer invalid_count;
  integer held_count;

  rv_source_position_immutable_rom_v1 #(
    .IMAGE_FILE("/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/onchip-all/rom/positions.hex")
  ) dut (
    .clk(clk), .por_reset(por_reset), .common_reset(common_reset),
    .request_valid(request_valid), .request_ready(request_ready),
    .request_session(request_session), .request_generation(request_generation),
    .request_tag(request_tag), .request_word(request_word),
    .idle(idle), .response_valid(response_valid), .response_ready(response_ready),
    .response_session(response_session), .response_generation(response_generation),
    .response_tag(response_tag), .response_word(response_word),
    .response_data(response_data), .request_rejected(request_rejected)
  );

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  function automatic [63:0] pinned_word(input [17:0] index);
    case (index)
      18'd0: pinned_word = 64'h71838f8084828d67;
      18'd1: pinned_word = 64'ha08f77616a599793;
      18'd1279: pinned_word = 64'h747a666e7f867875;
      18'd1280: pinned_word = 64'h8a86798d8d7b725e;
      18'd163838: pinned_word = 64'h7b7a7a7a797b7b7b;
      18'd163839: pinned_word = 64'h7b7a7d7a797a7b7d;
      default: pinned_word = 64'hxxxxxxxxxxxxxxxx;
    endcase
  endfunction

  task automatic tick;
    begin @(posedge clk); #1; end
  endtask

  task automatic legal_read(input [17:0] index);
    begin
      @(negedge clk);
      request_valid = 1'b1;
      request_session = 32'h10203040;
      request_generation = 32'd0;
      request_tag = 32'h50607080;
      request_word = index;
      response_ready = 1'b0;
      #1;
      if (request_ready !== 1'b1 || request_rejected !== 1'b0 || idle !== 1'b1)
        $fatal(1, "legal offer not accepted");
      tick();
      request_valid = 1'b0;
      if (response_valid !== 1'b0 || idle !== 1'b0 || request_ready !== 1'b0)
        $fatal(1, "reply arrived on accept edge");
      tick();
      if (response_valid !== 1'b0) $fatal(1, "reply arrived before two retire edges");
      tick();
      if (response_valid !== 1'b1 || response_session !== 32'h10203040 ||
          response_generation !== 32'd0 || response_tag !== 32'h50607080 ||
          response_word !== index || response_data !== pinned_word(index))
        $fatal(1, "pinned position reply mismatch");
      request_valid = 1'b1;
      request_word = 18'd0;
      request_tag = 32'hdeadbeef;
      repeat (3) begin
        tick();
        if (response_valid !== 1'b1 || response_data !== pinned_word(index) ||
            response_word !== index || response_tag !== 32'h50607080 ||
            request_ready !== 1'b0 || request_rejected !== 1'b0)
          $fatal(1, "held position reply changed");
        held_count = held_count + 1;
      end
      @(negedge clk);
      request_valid = 1'b0;
      response_ready = 1'b1;
      tick();
      response_ready = 1'b0;
      if (response_valid !== 1'b0 || idle !== 1'b1)
        $fatal(1, "position ACK did not retire");
      legal_count = legal_count + 1;
    end
  endtask

  task automatic invalid_offer;
    begin
      #1;
      if (request_ready !== 1'b0 || request_rejected !== 1'b1 || idle !== 1'b1)
        $fatal(1, "invalid offer not refused");
      tick();
      if (idle !== 1'b1 || response_valid !== 1'b0)
        $fatal(1, "invalid offer changed queue state");
      invalid_count = invalid_count + 1;
    end
  endtask

  always @(posedge clk) begin
    #2;
    if (monitor_armed) begin
      if ((idle !== 1'b0 && idle !== 1'b1) ||
          (response_valid !== 1'b0 && response_valid !== 1'b1) ||
          (request_ready !== 1'b0 && request_ready !== 1'b1) ||
          (idle === 1'b1 && response_valid !== 1'b0))
        $fatal(1, "queue control became unknown or inconsistent");
    end
  end

  initial begin
    monitor_armed = 1'b0;
    legal_count = 0;
    invalid_count = 0;
    held_count = 0;
    por_reset = 1'b1;
    common_reset = 1'b0;
    request_valid = 1'b0;
    request_session = 32'd0;
    request_generation = 32'd0;
    request_tag = 32'd0;
    request_word = 18'd0;
    response_ready = 1'b0;
    #2;
    if (idle !== 1'b1 || response_valid !== 1'b0)
      $fatal(1, "asynchronous POR did not clear queue");
    por_reset = 1'b0;
    monitor_armed = 1'b1;

    legal_read(18'd0);
    legal_read(18'd1);
    legal_read(18'd1279);
    legal_read(18'd1280);
    legal_read(18'd163838);
    legal_read(18'd163839);

    @(negedge clk); request_valid = 1'b1; request_word = 18'd163840;
    invalid_offer();
    @(negedge clk); request_word = 18'd262143;
    invalid_offer();
    @(negedge clk); request_word = 18'bxxxxxxxxxxxxxxxxxx;
    invalid_offer();
    @(negedge clk); request_word = 18'bzzzzzzzzzzzzzzzzzz;
    invalid_offer();
    @(negedge clk); request_word = 18'd0; request_generation = 32'd1;
    invalid_offer();
    @(negedge clk); request_generation = 32'hxxxxxxxx;
    invalid_offer();
    @(negedge clk); request_generation = 32'hzzzzzzzz;
    invalid_offer();
    @(negedge clk); request_generation = 32'd0; request_tag = 32'hxxxxxxxx;
    invalid_offer();
    @(negedge clk); request_tag = 32'd0; request_session = 32'hzzzzzzzz;
    invalid_offer();
    @(negedge clk); request_session = 32'd1; request_valid = 1'bx;
    invalid_offer();
    @(negedge clk); request_valid = 1'bz;
    invalid_offer();
    @(negedge clk); request_valid = 1'b0; request_word = 18'h3ffff;
    #1;
    if (request_ready !== 1'b1 || request_rejected !== 1'b0)
      $fatal(1, "invalid fields must not reject an absent request");

    // Common reset blocks new handshakes but preserves a pending deterministic reply.
    @(negedge clk);
    request_valid = 1'b1;
    request_session = 32'd9;
    request_tag = 32'd7;
    request_word = 18'd1;
    tick();
    request_valid = 1'b0;
    common_reset = 1'b1;
    response_ready = 1'b1;
    tick();
    tick();
    if (response_valid !== 1'b1 || response_data !== pinned_word(18'd1))
      $fatal(1, "common reset lost pending reply");
    tick();
    if (response_valid !== 1'b1 || idle !== 1'b0 || request_ready !== 1'b0)
      $fatal(1, "common reset incorrectly acknowledged reply");
    common_reset = 1'b0;
    tick();
    response_ready = 1'b0;
    if (idle !== 1'b1) $fatal(1, "post-reset ACK failed");

    @(negedge clk); request_valid = 1'b1; request_word = 18'd0;
    tick();
    request_valid = 1'b0;
    #1; por_reset = 1'b1;
    #1;
    if (idle !== 1'b1 || response_valid !== 1'b0 || response_data !== 64'd0)
      $fatal(1, "partial transaction survived POR");
    por_reset = 1'b0;
    if (legal_count != 6 || invalid_count != 11 || held_count != 18)
      $fatal(1, "position test count mismatch");
    $display("POSITION_ROM_SOURCE_CONTROL_PASS legal=%0d invalid=%0d held=%0d", legal_count, invalid_count, held_count);
    $finish;
  end
endmodule
