// Native FP32 immutable words. Accepted N -> PRE N+1, held until ACK.
// No runtime write port; no claim of physical ROM area/timing qualification.
module rv_onchip_frontend_v1 #(
 parameter CONV1_WEIGHTS_FILE = "/Users/sanju/.local/state/routevoice-internal-runs/20261014/onchip-front/rom/conv1_weights.hex",
 parameter CONV1_BIAS_FILE = "/Users/sanju/.local/state/routevoice-internal-runs/20261014/onchip-front/rom/conv1_bias.hex",
 parameter CONV2_WEIGHTS_FILE = "/Users/sanju/.local/state/routevoice-internal-runs/20261014/onchip-front/rom/conv2_weights.hex",
 parameter CONV2_BIAS_FILE = "/Users/sanju/.local/state/routevoice-internal-runs/20261014/onchip-front/rom/conv2_bias.hex",
 parameter LINEAR_WEIGHTS_FILE = "/Users/sanju/.local/state/routevoice-internal-runs/20261014/onchip-front/rom/linear_weights.hex"
)(input wire clk, por_reset, warm_reset,
 input wire req_valid, output wire req_ready,
 input wire [1:0] req_client, output logic [1:0] rsp_client,
 input wire [1:0] req_backing_owner, output logic [1:0] rsp_backing_owner,
 input wire  req_scalar, output logic  rsp_scalar,
 input wire  req_write, output logic  rsp_write,
 input wire [2:0] req_layer, output logic [2:0] rsp_layer,
 input wire [2:0] req_origin, output logic [2:0] rsp_origin,
 input wire [3:0] req_region, output logic [3:0] rsp_region,
 input wire [31:0] req_tag, output logic [31:0] rsp_tag,
 input wire [31:0] req_word, output logic [31:0] rsp_word,
 input wire [31:0] req_job, output logic [31:0] rsp_job,
 input wire [31:0] req_session, output logic [31:0] rsp_session,
 input wire [31:0] req_sequence, output logic [31:0] rsp_sequence,
 output wire idle, output logic fault,
 output logic rsp_valid, input wire rsp_ready, output logic [255:0] rsp_data);
 logic [31:0] conv1_weights[0:1023999];
 initial $readmemh(CONV1_WEIGHTS_FILE,conv1_weights);
 logic [31:0] conv1_bias[0:639];
 initial $readmemh(CONV1_BIAS_FILE,conv1_bias);
 logic [31:0] conv2_weights[0:1023999];
 initial $readmemh(CONV2_WEIGHTS_FILE,conv2_weights);
 logic [31:0] conv2_bias[0:319];
 initial $readmemh(CONV2_BIAS_FILE,conv2_bias);
 logic [31:0] linear_weights[0:25599];
 initial $readmemh(LINEAR_WEIGHTS_FILE,linear_weights);
 logic [31:0] selected;
 logic legal_address;
 always_comb begin
 selected=0; legal_address=0;
 case(req_region)
 0: if(req_word < 1024000) begin selected=conv1_weights[req_word]; legal_address=1; end
 1: if(req_word < 640) begin selected=conv1_bias[req_word]; legal_address=1; end
 4: if(req_word < 1024000) begin selected=conv2_weights[req_word]; legal_address=1; end
 5: if(req_word < 320) begin selected=conv2_bias[req_word]; legal_address=1; end
 8: if(req_word < 25600) begin selected=linear_weights[req_word]; legal_address=1; end
 default: ;
 endcase
 end
 wire legal = legal_address && req_client==0 && req_backing_owner==0 && req_scalar && !req_write;
 assign idle=!rsp_valid;
 assign req_ready=!por_reset && !warm_reset && !rsp_valid && (!req_valid || legal);
 always_ff @(posedge clk) begin
   if(por_reset) begin
     rsp_valid<=0; rsp_data<=0; fault<=0;
       rsp_client <= 0;
       rsp_backing_owner <= 0;
       rsp_scalar <= 0;
       rsp_write <= 0;
       rsp_layer <= 0;
       rsp_origin <= 0;
       rsp_region <= 0;
       rsp_tag <= 0;
       rsp_word <= 0;
       rsp_job <= 0;
       rsp_session <= 0;
       rsp_sequence <= 0;
   end else if(!warm_reset) begin
     if(req_valid && !legal) fault<=1;
     if(rsp_valid && rsp_ready) rsp_valid<=0;
     if(req_valid && req_ready) begin
       rsp_valid<=1; rsp_data<={224'd0,selected};
       rsp_client <= req_client;
       rsp_backing_owner <= req_backing_owner;
       rsp_scalar <= req_scalar;
       rsp_write <= req_write;
       rsp_layer <= req_layer;
       rsp_origin <= req_origin;
       rsp_region <= req_region;
       rsp_tag <= req_tag;
       rsp_word <= req_word;
       rsp_job <= req_job;
       rsp_session <= req_session;
       rsp_sequence <= req_sequence;
     end
   end
 end
endmodule
