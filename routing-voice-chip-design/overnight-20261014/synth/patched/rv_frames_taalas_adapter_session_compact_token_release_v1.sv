// SOURCE PREPARATION ONLY. Fixed F500 source -> fixed F500 compact token.
// Numerical/token/lifecycle/physical qualification remains pending.
module rv_frames_taalas_adapter_session_compact_token_release_v1 #(parameter integer FRAMES=500)(
 input wire  clk,
 input wire  reset,
 input wire  step_enable,
 input wire  start_valid,
 output wire  start_ready,
 input wire [31:0] start_tag,
 input wire [15:0] start_token,
 input wire [6:0] start_position,
 input wire [8:0] start_frames,
 input wire  e_producers_idle,
 input wire  h_producers_idle,
 input wire  row_transfer_enable,
 output wire  done_valid,
 input wire  done_ready,
 output wire [31:0] done_tag,
 output wire [31:0] done_fault,
 output wire [14:0] best_token,
 output wire [31:0] best_logit,
 output wire  is_eos,
 output wire  owner_lock,
 output wire  epoch_commit,
 output wire  epoch_abort,
 output wire [3:0] debug_join_phase,
 output wire [3:0] debug_embedding_phase,
 output wire  debug_embedding_valid,
 output wire  debug_embedding_accept,
 output wire [31:0] debug_embedding_value,
 output wire [8:0] debug_embedding_index,
 output wire  out_valid,
 output wire  out_ready,
 output wire [31:0] out_tag,
 output wire [31:0] out_value,
 output wire [8:0] out_index,
 output wire  out_tentative,
 output wire  debug_body_done,
 output wire  debug_head_done,
 input wire  compact_setup_valid,
 output wire  compact_setup_ready,
 input wire [31:0] compact_setup_session,
 input wire [255:0] compact_setup_image_id,
 output wire [15:0] compact_setup_fault,
 output wire  compact_session_valid,
 output wire [31:0] compact_session_id,
 output wire [6:0] compact_committed_count,
 input wire  compact_fixed_idle,
 output wire  compact_fixed_req_valid,
 input wire  compact_fixed_req_ready,
 output wire [31:0] compact_fixed_req_tag,
 output wire [2:0] compact_fixed_req_layer,
 output wire [1:0] compact_fixed_req_role,
 output wire  compact_fixed_req_region,
 output wire [11:0] compact_fixed_req_word,
 input wire  compact_fixed_rsp_valid,
 output wire  compact_fixed_rsp_ready,
 input wire [31:0] compact_fixed_rsp_tag,
 input wire [2:0] compact_fixed_rsp_layer,
 input wire [1:0] compact_fixed_rsp_role,
 input wire  compact_fixed_rsp_region,
 input wire [11:0] compact_fixed_rsp_word,
 input wire [255:0] compact_fixed_rsp_data,
 input wire  compact_memory_idle,
 output wire  compact_mem_valid,
 input wire  compact_mem_ready,
 output wire  compact_mem_write,
 output wire  compact_mem_region,
 output wire [2:0] compact_mem_layer,
 output wire [2:0] compact_mem_phase,
 output wire [6:0] compact_mem_position,
 output wire [3:0] compact_mem_packet,
 output wire [12:0] compact_mem_word,
 output wire [31:0] compact_mem_session,
 output wire [31:0] compact_mem_attempt,
 output wire [15:0] compact_mem_sequence,
 output wire [255:0] compact_mem_data,
 input wire  compact_response_valid,
 output wire  compact_response_ready,
 input wire  compact_response_write,
 input wire  compact_response_region,
 input wire [2:0] compact_response_layer,
 input wire [2:0] compact_response_phase,
 input wire [6:0] compact_response_position,
 input wire [3:0] compact_response_packet,
 input wire [12:0] compact_response_word,
 input wire [31:0] compact_response_session,
 input wire [31:0] compact_response_attempt,
 input wire [15:0] compact_response_sequence,
 input wire [255:0] compact_response_data,
 output wire  compact_attempt_lock,
 output wire  compact_history_lock,
 output wire  compact_prepared,
 output wire [31:0] compact_attempt,
 output wire [4:0] compact_phase,
 output wire  compact_layer_release,
 output wire [3:0] compact_record_acks,
 input wire  learned_idle,
 input wire  learned_valid,
 output wire  learned_ready,
 output wire  learned_want,
 input wire [31:0] learned_tag,
 input wire [2:0] learned_layer,
 input wire [8:0] learned_index,
 input wire [127:0] learned_values,
 output wire [2:0] learned_expected_layer,
 output wire [8:0] learned_expected_index,
 output wire  kv_idle,
 output wire  kv_valid,
 output wire  kv_ready,
 output wire [31:0] kv_tag,
 output wire [31:0] kv_value,
 output wire [2:0] kv_layer,
 output wire [2:0] kv_head,
 output wire [15:0] kv_index,
 output wire  kv_want,
 output wire [2:0] kv_expected_head,
 output wire [15:0] kv_expected_index,
 input wire  memory_idle,
 output wire  req_valid,
 input wire  req_ready,
 output wire [31:0] req_tag,
 output wire [2:0] req_layer,
 output wire [2:0] req_role,
 output wire [2:0] req_tile,
 output wire  req_region,
 output wire [13:0] req_word,
 input wire  rsp_valid,
 output wire  rsp_ready,
 input wire [31:0] rsp_tag,
 input wire [2:0] rsp_layer,
 input wire [2:0] rsp_role,
 input wire [2:0] rsp_tile,
 input wire  rsp_region,
 input wire [13:0] rsp_word,
 input wire [255:0] rsp_data,
 output wire [3:0] debug_token_phase,
 output wire [2:0] debug_layer,
 output wire [6:0] debug_position,
 output wire  debug_row_read,
 output wire  debug_row_write,
 output wire [8:0] debug_row_index,
 output wire [31:0] debug_row_value,
 output wire  debug_export_capture,
 output wire  debug_child_commit,
 output wire [6:0] debug_child_terms,
 output wire [4:0] debug_phase,
 output wire [4:0] debug_ff_phase,
 output wire [4:0] debug_skip_phase,
 output wire [4:0] debug_qkv_phase,
 output wire [4:0] debug_cross_query_phase,
 output wire [2:0] debug_self_phase,
 output wire [2:0] debug_cross_phase,
 output wire [3:0] debug_self_o_phase,
 output wire [3:0] debug_cross_o_phase,
 output wire  debug_branch_write,
 output wire [1:0] debug_branch_role,
 output wire [1:0] debug_branch_mask,
 output wire [8:0] debug_branch_index,
 output wire [63:0] debug_branch_values,
 output wire  debug_residual_write,
 output wire [1:0] debug_residual_role,
 output wire [8:0] debug_residual_index,
 output wire [31:0] debug_residual_a,
 output wire [31:0] debug_residual_b,
 output wire [31:0] debug_residual_value,
 output wire  debug_source_accept,
 output wire [1:0] debug_source_role,
 output wire [8:0] debug_source_index,
 output wire [31:0] debug_source_value,
 output wire [31:0] debug_source_skip,
 output wire [31:0] debug_source_learned,
 output wire  debug_quant_valid,
 output wire [2:0] debug_quant_domain,
 output wire [10:0] debug_quant_base,
 output wire [63:0] debug_quant_codes,
 output wire [31:0] debug_quant_scale,
 output wire [7:0] debug_quant_zero,
 output wire  debug_current_valid,
 output wire [1:0] debug_current_role,
 output wire [8:0] debug_current_index,
 output wire [31:0] debug_current_value,
 output wire  debug_query_valid,
 output wire [8:0] debug_query_index,
 output wire [31:0] debug_query_value,
 output wire  debug_context_valid,
 output wire  debug_context_role,
 output wire [8:0] debug_context_index,
 output wire [31:0] debug_context_value,
 output wire  debug_ff_store,
 output wire [1:0] debug_ff_store_kind,
 output wire [10:0] debug_ff_store_index,
 output wire [31:0] debug_ff_store_value,
 output wire  debug_final_normalized,
 output wire [8:0] debug_final_index,
 output wire [31:0] debug_final_value,
 output wire  e_index_request_valid,
 input wire  e_index_request_ready,
 output wire [31:0] e_index_request_tag,
 output wire [6:0] e_index_request_group,
 output wire [8:0] e_index_request_row,
 input wire  e_index_response_valid,
 output wire  e_index_response_ready,
 input wire [31:0] e_index_response_tag,
 input wire [6:0] e_index_response_group,
 input wire [8:0] e_index_response_row,
 input wire [1023:0] e_index_response_data,
 output wire  e_book_request_valid,
 input wire  e_book_request_ready,
 output wire [31:0] e_book_request_tag,
 output wire [23:0] e_book_request_page,
 input wire  e_book_response_valid,
 output wire  e_book_response_ready,
 input wire [31:0] e_book_response_tag,
 input wire [23:0] e_book_response_page,
 input wire [3:0] e_book_response_beat,
 input wire [255:0] e_book_response_data,
 output wire  h_index_request_valid,
 input wire  h_index_request_ready,
 output wire [31:0] h_index_request_tag,
 output wire [6:0] h_index_request_group,
 output wire [8:0] h_index_request_row,
 input wire  h_index_response_valid,
 output wire  h_index_response_ready,
 input wire [31:0] h_index_response_tag,
 input wire [6:0] h_index_response_group,
 input wire [8:0] h_index_response_row,
 input wire [1023:0] h_index_response_data,
 input wire [31:0] h_book_job_tag,
 input wire [7:0] h_load_start_valid,
 output wire [7:0] h_load_start_ready,
 input wire [191:0] h_load_tags,
 input wire [7:0] h_load_valid,
 output wire [7:0] h_load_ready,
 input wire [2047:0] h_load_data,
 input wire [191:0] h_load_data_tags,
 input wire [31:0] h_load_data_beats,
 output wire [7:0] h_loading,
 output wire [31:0] h_load_beats,
 input wire [7:0] h_commit_valid,
 output wire [7:0] h_commit_ready,
 input wire [191:0] h_commit_tags,
 output wire [191:0] h_requested_tags,
 output wire [191:0] h_active_tags,
 output wire [3:0] h_debug_phase,
 output wire [6:0] h_debug_group,
 output wire [8:0] h_debug_row,
 output wire [2:0] h_debug_head_phase,
 output wire  h_debug_logit_valid,
 output wire  h_debug_logit_accept,
 output wire [255:0] h_debug_logits,
 output wire [4:0] h_debug_column,
 output wire [2:0] kv_expected_layer,
 output wire [2:0] layer_release_layer,
 output wire [31:0] layer_release_tag,
 output wire [31:0] layer_release_session,
 output wire [31:0] layer_release_attempt,
 output wire [6:0] layer_release_position,
 input wire  source_fresh_idle,
 input wire  source_fresh_valid,
 output wire  source_fresh_ready,
 input wire [31:0] source_fresh_tag,
 input wire [14:0] source_fresh_word,
 input wire [255:0] source_fresh_data,
 output wire  source_debug_alias_transferred,
 output wire [14:0] source_debug_fresh_accepted,
 output wire [14:0] source_debug_fresh_ACKs,
 input wire  source_memory_idle,
 output wire  source_mem_valid,
 input wire  source_mem_ready,
 output wire  source_mem_write,
 output wire [31:0] source_mem_session,
 output wire [31:0] source_mem_generation,
 output wire [2:0] source_mem_region,
 output wire [2:0] source_mem_layer,
 output wire  source_mem_role,
 output wire [31:0] source_mem_tag,
 output wire [31:0] source_mem_word,
 output wire [255:0] source_mem_data,
 input wire [31:0] source_response_session,
 input wire [31:0] source_response_generation,
 input wire  source_response_valid,
 output wire  source_response_ready,
 input wire  source_response_write,
 input wire [2:0] source_response_region,
 input wire [2:0] source_response_layer,
 input wire  source_response_role,
 input wire [31:0] source_response_tag,
 input wire [31:0] source_response_word,
 input wire [255:0] source_response_data,
 output wire [31:0] source_position_session,
 output wire [31:0] source_position_generation,
 input wire [31:0] source_position_response_session,
 input wire [31:0] source_position_response_generation,
 input wire  source_position_idle,
 output wire  source_position_valid,
 input wire  source_position_ready,
 output wire [31:0] source_position_tag,
 output wire [17:0] source_position_word,
 input wire  source_position_response_valid,
 output wire  source_position_response_ready,
 input wire [31:0] source_position_response_tag,
 input wire [17:0] source_position_response_word,
 input wire [63:0] source_position_response_data,
 output wire [31:0] source_fixed_session,
 output wire [31:0] source_fixed_generation,
 input wire [31:0] source_fixed_response_session,
 input wire [31:0] source_fixed_response_generation,
 input wire  source_fixed_idle,
 output wire  source_fixed_valid,
 input wire  source_fixed_ready,
 output wire [31:0] source_fixed_tag,
 output wire [2:0] source_fixed_layer,
 output wire  source_fixed_role,
 output wire [8:0] source_fixed_row,
 input wire  source_fixed_response_valid,
 output wire  source_fixed_response_ready,
 input wire [31:0] source_fixed_response_tag,
 input wire [2:0] source_fixed_response_layer,
 input wire  source_fixed_response_role,
 input wire [8:0] source_fixed_response_row,
 input wire [2559:0] source_fixed_response_data,
 output wire [31:0] source_global_scale,
 output wire [7:0] source_global_zero,
 output wire [31:0] source_debug_code_reads,
 output wire [31:0] source_debug_K_ACKs,
 output wire [31:0] source_debug_V_ACKs,
 output wire [31:0] source_debug_coefficient_reads,
 input wire source_start_valid,output wire source_start_ready,
 input wire [31:0]source_start_tag,source_start_position_scale,
 input wire [7:0]source_start_position_zero,input wire [11:0]source_start_position_offset,
 output wire source_session_valid,source_ready,source_owner_lock,
 output wire [31:0]source_session_tag,source_generation,source_token_epoch,
 input wire source_release_valid,output wire source_release_ready,input wire [31:0]source_release_tag,
 output wire source_error_valid,input wire source_error_ready,output wire [31:0]source_error,
 output wire [31:0]source_mem_epoch,source_fixed_epoch,
 input wire [31:0]source_response_epoch,source_fixed_response_epoch,
 output wire [3:0]source_owner_phase,
 output wire [4:0]source_phase,source_projection_phase,output wire [3:0]source_setup_phase,
 output wire source_codes_lock,source_projection_role,
 output wire bridge_packet_pending,bridge_packet_valid,bridge_accept,
 output wire [31:0]bridge_value,bridge_generation,bridge_epoch,
 output wire [2:0]bridge_layer,bridge_head,output wire [15:0]bridge_index,
 output wire source_memory_pending,source_fixed_pending,source_position_pending,
 output wire [18:0]bridge_layer_scalars,output wire [15:0]bridge_layer_packets,
 output wire [2:0]bridge_layers_released,output wire token_warm_abort
);
 localparam EMPTY=0,PSTART=1,SETUP=2,CODES=3,GSTART=4,GRUN=5,GACCEPT=6,RETAIN=7,GRELEASE=8,PDRAIN=9,PERROR=10,PEND=11; // moved up for strict elaboration (overnight synth check)
 localparam integer RV_VALUES=FRAMES*320, RV_WORDS=FRAMES*40, RV_CODEWORDS=FRAMES*10;
 localparam integer RV_BATCHES=(FRAMES+7)/8, RV_LAST_BATCH=(RV_BATCHES-1)*8, RV_PAD_ROWS=RV_BATCHES*8-FRAMES;

 initial begin if(FRAMES<4||FRAMES>508||FRAMES%4!=0) $fatal(1,"Unsupported static FRAMES geometry"); end

 wire ps,pgready,psession,psrelease,pd,presult,prelease;
 wire [31:0]psession_tag,pdone_tag,pdone_generation,pfault,presult_tag,presult_generation;
 wire [2:0]presult_layer;
 wire pmvalid,pmready,ppvalid,ppready,pfvalid,pfready,pfresh;
 wire consumer_ready,consumer_valid,consumer_role;wire [31:0]consumer_generation,consumer_tag,consumer_word;
 wire [255:0]consumer_data;
 wire token_ready,token_done_valid,token_owner;wire [31:0]token_done_fault;
 rv_frames_taalas_decoder_token_compact_joinable_q1 #(.FRAMES(FRAMES)) token(
  .clk(clk),
  .reset(reset),
  .step_enable(step_enable),
  .start_valid(start_valid&&start_ready),
  .start_ready(token_ready),
  .start_tag(start_tag),
  .start_token(start_token),
  .start_position(start_position),
  .start_frames(start_frames),
  .e_producers_idle(e_producers_idle),
  .h_producers_idle(h_producers_idle),
  .row_transfer_enable(row_transfer_enable),
  .warm_abort_valid(token_warm_abort),
  .warm_abort_tag(token_tag),
  .kv_expected_layer(kv_expected_layer),
  .layer_release_layer(layer_release_layer),
  .layer_release_tag(layer_release_tag),
  .layer_release_session(layer_release_session),
  .layer_release_attempt(layer_release_attempt),
  .layer_release_position(layer_release_position),
  .done_valid(token_done_valid),
  .done_ready(token_done_accept),
  .done_tag(done_tag),
  .done_fault(token_done_fault),
  .best_token(best_token),
  .best_logit(best_logit),
  .is_eos(is_eos),
  .owner_lock(token_owner),
  .epoch_commit(epoch_commit),
  .epoch_abort(epoch_abort),
  .debug_join_phase(debug_join_phase),
  .debug_embedding_phase(debug_embedding_phase),
  .debug_embedding_valid(debug_embedding_valid),
  .debug_embedding_accept(debug_embedding_accept),
  .debug_embedding_value(debug_embedding_value),
  .debug_embedding_index(debug_embedding_index),
  .out_valid(out_valid),
  .out_ready(out_ready),
  .out_tag(out_tag),
  .out_value(out_value),
  .out_index(out_index),
  .out_tentative(out_tentative),
  .debug_body_done(debug_body_done),
  .debug_head_done(debug_head_done),
  .compact_setup_valid(compact_setup_valid),
  .compact_setup_ready(compact_setup_ready),
  .compact_setup_session(compact_setup_session),
  .compact_setup_image_id(compact_setup_image_id),
  .compact_setup_fault(compact_setup_fault),
  .compact_session_valid(compact_session_valid),
  .compact_session_id(compact_session_id),
  .compact_committed_count(compact_committed_count),
  .compact_fixed_idle(compact_fixed_idle),
  .compact_fixed_req_valid(compact_fixed_req_valid),
  .compact_fixed_req_ready(compact_fixed_req_ready),
  .compact_fixed_req_tag(compact_fixed_req_tag),
  .compact_fixed_req_layer(compact_fixed_req_layer),
  .compact_fixed_req_role(compact_fixed_req_role),
  .compact_fixed_req_region(compact_fixed_req_region),
  .compact_fixed_req_word(compact_fixed_req_word),
  .compact_fixed_rsp_valid(compact_fixed_rsp_valid),
  .compact_fixed_rsp_ready(compact_fixed_rsp_ready),
  .compact_fixed_rsp_tag(compact_fixed_rsp_tag),
  .compact_fixed_rsp_layer(compact_fixed_rsp_layer),
  .compact_fixed_rsp_role(compact_fixed_rsp_role),
  .compact_fixed_rsp_region(compact_fixed_rsp_region),
  .compact_fixed_rsp_word(compact_fixed_rsp_word),
  .compact_fixed_rsp_data(compact_fixed_rsp_data),
  .compact_memory_idle(compact_memory_idle),
  .compact_mem_valid(compact_mem_valid),
  .compact_mem_ready(compact_mem_ready),
  .compact_mem_write(compact_mem_write),
  .compact_mem_region(compact_mem_region),
  .compact_mem_layer(compact_mem_layer),
  .compact_mem_phase(compact_mem_phase),
  .compact_mem_position(compact_mem_position),
  .compact_mem_packet(compact_mem_packet),
  .compact_mem_word(compact_mem_word),
  .compact_mem_session(compact_mem_session),
  .compact_mem_attempt(compact_mem_attempt),
  .compact_mem_sequence(compact_mem_sequence),
  .compact_mem_data(compact_mem_data),
  .compact_response_valid(compact_response_valid),
  .compact_response_ready(compact_response_ready),
  .compact_response_write(compact_response_write),
  .compact_response_region(compact_response_region),
  .compact_response_layer(compact_response_layer),
  .compact_response_phase(compact_response_phase),
  .compact_response_position(compact_response_position),
  .compact_response_packet(compact_response_packet),
  .compact_response_word(compact_response_word),
  .compact_response_session(compact_response_session),
  .compact_response_attempt(compact_response_attempt),
  .compact_response_sequence(compact_response_sequence),
  .compact_response_data(compact_response_data),
  .compact_attempt_lock(compact_attempt_lock),
  .compact_history_lock(compact_history_lock),
  .compact_prepared(compact_prepared),
  .compact_attempt(compact_attempt),
  .compact_phase(compact_phase),
  .compact_layer_release(compact_layer_release),
  .compact_record_acks(compact_record_acks),
  .learned_idle(learned_idle),
  .learned_valid(learned_valid),
  .learned_ready(learned_ready),
  .learned_want(learned_want),
  .learned_tag(learned_tag),
  .learned_layer(learned_layer),
  .learned_index(learned_index),
  .learned_values(learned_values),
  .learned_expected_layer(learned_expected_layer),
  .learned_expected_index(learned_expected_index),
  .kv_idle(kv_idle),
  .kv_valid(kv_valid),
  .kv_ready(kv_ready),
  .kv_tag(kv_tag),
  .kv_value(kv_value),
  .kv_layer(kv_layer),
  .kv_head(kv_head),
  .kv_index(kv_index),
  .kv_want(kv_want),
  .kv_expected_head(kv_expected_head),
  .kv_expected_index(kv_expected_index),
  .memory_idle(memory_idle),
  .req_valid(req_valid),
  .req_ready(req_ready),
  .req_tag(req_tag),
  .req_layer(req_layer),
  .req_role(req_role),
  .req_tile(req_tile),
  .req_region(req_region),
  .req_word(req_word),
  .rsp_valid(rsp_valid),
  .rsp_ready(rsp_ready),
  .rsp_tag(rsp_tag),
  .rsp_layer(rsp_layer),
  .rsp_role(rsp_role),
  .rsp_tile(rsp_tile),
  .rsp_region(rsp_region),
  .rsp_word(rsp_word),
  .rsp_data(rsp_data),
  .debug_token_phase(debug_token_phase),
  .debug_layer(debug_layer),
  .debug_position(debug_position),
  .debug_row_read(debug_row_read),
  .debug_row_write(debug_row_write),
  .debug_row_index(debug_row_index),
  .debug_row_value(debug_row_value),
  .debug_export_capture(debug_export_capture),
  .debug_child_commit(debug_child_commit),
  .debug_child_terms(debug_child_terms),
  .debug_phase(debug_phase),
  .debug_ff_phase(debug_ff_phase),
  .debug_skip_phase(debug_skip_phase),
  .debug_qkv_phase(debug_qkv_phase),
  .debug_cross_query_phase(debug_cross_query_phase),
  .debug_self_phase(debug_self_phase),
  .debug_cross_phase(debug_cross_phase),
  .debug_self_o_phase(debug_self_o_phase),
  .debug_cross_o_phase(debug_cross_o_phase),
  .debug_branch_write(debug_branch_write),
  .debug_branch_role(debug_branch_role),
  .debug_branch_mask(debug_branch_mask),
  .debug_branch_index(debug_branch_index),
  .debug_branch_values(debug_branch_values),
  .debug_residual_write(debug_residual_write),
  .debug_residual_role(debug_residual_role),
  .debug_residual_index(debug_residual_index),
  .debug_residual_a(debug_residual_a),
  .debug_residual_b(debug_residual_b),
  .debug_residual_value(debug_residual_value),
  .debug_source_accept(debug_source_accept),
  .debug_source_role(debug_source_role),
  .debug_source_index(debug_source_index),
  .debug_source_value(debug_source_value),
  .debug_source_skip(debug_source_skip),
  .debug_source_learned(debug_source_learned),
  .debug_quant_valid(debug_quant_valid),
  .debug_quant_domain(debug_quant_domain),
  .debug_quant_base(debug_quant_base),
  .debug_quant_codes(debug_quant_codes),
  .debug_quant_scale(debug_quant_scale),
  .debug_quant_zero(debug_quant_zero),
  .debug_current_valid(debug_current_valid),
  .debug_current_role(debug_current_role),
  .debug_current_index(debug_current_index),
  .debug_current_value(debug_current_value),
  .debug_query_valid(debug_query_valid),
  .debug_query_index(debug_query_index),
  .debug_query_value(debug_query_value),
  .debug_context_valid(debug_context_valid),
  .debug_context_role(debug_context_role),
  .debug_context_index(debug_context_index),
  .debug_context_value(debug_context_value),
  .debug_ff_store(debug_ff_store),
  .debug_ff_store_kind(debug_ff_store_kind),
  .debug_ff_store_index(debug_ff_store_index),
  .debug_ff_store_value(debug_ff_store_value),
  .debug_final_normalized(debug_final_normalized),
  .debug_final_index(debug_final_index),
  .debug_final_value(debug_final_value),
  .e_index_request_valid(e_index_request_valid),
  .e_index_request_ready(e_index_request_ready),
  .e_index_request_tag(e_index_request_tag),
  .e_index_request_group(e_index_request_group),
  .e_index_request_row(e_index_request_row),
  .e_index_response_valid(e_index_response_valid),
  .e_index_response_ready(e_index_response_ready),
  .e_index_response_tag(e_index_response_tag),
  .e_index_response_group(e_index_response_group),
  .e_index_response_row(e_index_response_row),
  .e_index_response_data(e_index_response_data),
  .e_book_request_valid(e_book_request_valid),
  .e_book_request_ready(e_book_request_ready),
  .e_book_request_tag(e_book_request_tag),
  .e_book_request_page(e_book_request_page),
  .e_book_response_valid(e_book_response_valid),
  .e_book_response_ready(e_book_response_ready),
  .e_book_response_tag(e_book_response_tag),
  .e_book_response_page(e_book_response_page),
  .e_book_response_beat(e_book_response_beat),
  .e_book_response_data(e_book_response_data),
  .h_index_request_valid(h_index_request_valid),
  .h_index_request_ready(h_index_request_ready),
  .h_index_request_tag(h_index_request_tag),
  .h_index_request_group(h_index_request_group),
  .h_index_request_row(h_index_request_row),
  .h_index_response_valid(h_index_response_valid),
  .h_index_response_ready(h_index_response_ready),
  .h_index_response_tag(h_index_response_tag),
  .h_index_response_group(h_index_response_group),
  .h_index_response_row(h_index_response_row),
  .h_index_response_data(h_index_response_data),
  .h_book_job_tag(h_book_job_tag),
  .h_load_start_valid(h_load_start_valid),
  .h_load_start_ready(h_load_start_ready),
  .h_load_tags(h_load_tags),
  .h_load_valid(h_load_valid),
  .h_load_ready(h_load_ready),
  .h_load_data(h_load_data),
  .h_load_data_tags(h_load_data_tags),
  .h_load_data_beats(h_load_data_beats),
  .h_loading(h_loading),
  .h_load_beats(h_load_beats),
  .h_commit_valid(h_commit_valid),
  .h_commit_ready(h_commit_ready),
  .h_commit_tags(h_commit_tags),
  .h_requested_tags(h_requested_tags),
  .h_active_tags(h_active_tags),
  .h_debug_phase(h_debug_phase),
  .h_debug_group(h_debug_group),
  .h_debug_row(h_debug_row),
  .h_debug_head_phase(h_debug_head_phase),
  .h_debug_logit_valid(h_debug_logit_valid),
  .h_debug_logit_accept(h_debug_logit_accept),
  .h_debug_logits(h_debug_logits),
  .h_debug_column(h_debug_column)
 );
 rv_frames_taalas_adapter_cross_session_f500 #(.FRAMES(FRAMES)) producer(
  .clk(clk),
  .reset(producer_reset),
  .step_enable(step_enable),
  .start_valid(source_state==PSTART),
  .start_ready(ps),
  .start_tag(source_tag),
  .start_position_scale(position_scale),
  .start_position_zero(position_zero),
  .start_position_offset(position_offset),
  .generation_valid(source_state==GSTART&&!raw_bad),
  .generation_ready(pgready),
  .generation_source(source_tag),
  .generation_sequence(generation),
  .generation_layer(generation_layer),
  .session_valid(psession),
  .session_tag(psession_tag),
  .session_release_valid(source_release),
  .session_release_ready(psrelease),
  .session_release_tag(source_tag),
  .fresh_idle(source_fresh_idle),
  .fresh_valid(source_fresh_valid),
  .fresh_ready(pfresh),
  .fresh_tag(source_fresh_tag),
  .fresh_word(source_fresh_word),
  .fresh_data(source_fresh_data),
  .debug_alias_transferred(source_debug_alias_transferred),
  .debug_fresh_accepted(source_debug_fresh_accepted),
  .debug_fresh_ACKs(source_debug_fresh_ACKs),
  .memory_idle(source_memory_idle&&!memory_pending),
  .mem_valid(pmvalid),
  .mem_ready(source_mem_valid&&source_mem_ready),
  .mem_write(source_mem_write),
  .mem_session(source_mem_session),
  .mem_generation(source_mem_generation),
  .mem_region(source_mem_region),
  .mem_layer(source_mem_layer),
  .mem_role(source_mem_role),
  .mem_tag(source_mem_tag),
  .mem_word(source_mem_word),
  .mem_data(source_mem_data),
  .response_session(source_response_session),
  .response_generation(source_response_generation),
  .response_valid(!producer_reset&&source_response_valid&&memory_match),
  .response_ready(pmready),
  .response_write(source_response_write),
  .response_region(source_response_region),
  .response_layer(source_response_layer),
  .response_role(source_response_role),
  .response_tag(source_response_tag),
  .response_word(source_response_word),
  .response_data(source_response_data),
  .position_session(source_position_session),
  .position_generation(source_position_generation),
  .position_response_session(source_position_response_session),
  .position_response_generation(source_position_response_generation),
  .position_idle(source_position_idle&&!position_pending),
  .position_valid(ppvalid),
  .position_ready(source_position_valid&&source_position_ready),
  .position_tag(source_position_tag),
  .position_word(source_position_word),
  .position_response_valid(!producer_reset&&source_position_response_valid&&position_match),
  .position_response_ready(ppready),
  .position_response_tag(source_position_response_tag),
  .position_response_word(source_position_response_word),
  .position_response_data(source_position_response_data),
  .fixed_session(source_fixed_session),
  .fixed_generation(source_fixed_generation),
  .fixed_response_session(source_fixed_response_session),
  .fixed_response_generation(source_fixed_response_generation),
  .fixed_idle(source_fixed_idle&&!fixed_pending),
  .fixed_valid(pfvalid),
  .fixed_ready(source_fixed_valid&&source_fixed_ready),
  .fixed_tag(source_fixed_tag),
  .fixed_layer(source_fixed_layer),
  .fixed_role(source_fixed_role),
  .fixed_row(source_fixed_row),
  .fixed_response_valid(!producer_reset&&source_fixed_response_valid&&fixed_match),
  .fixed_response_ready(pfready),
  .fixed_response_tag(source_fixed_response_tag),
  .fixed_response_layer(source_fixed_response_layer),
  .fixed_response_role(source_fixed_response_role),
  .fixed_response_row(source_fixed_response_row),
  .fixed_response_data(source_fixed_response_data),
  .done_valid(pd),
  .done_ready(source_state==GACCEPT&&!raw_bad&&source_quiet),
  .done_tag(pdone_tag),
  .done_generation(pdone_generation),
  .done_fault(pfault),
  .global_scale(source_global_scale),
  .global_zero(source_global_zero),
  .result_valid(presult),
  .result_tag(presult_tag),
  .result_generation(presult_generation),
  .result_layer(presult_layer),
  .consumer_generation(generation),
  .consumer_valid(consumer_request),
  .consumer_ready(consumer_ready),
  .consumer_role(demand_role),
  .consumer_tag(source_tag),
  .consumer_word(demand_word),
  .consumer_response_generation(consumer_generation),
  .consumer_response_valid(consumer_valid),
  .consumer_response_ready(consumer_accept),
  .consumer_response_role(consumer_role),
  .consumer_response_tag(consumer_tag),
  .consumer_response_word(consumer_word),
  .consumer_response_data(consumer_data),
  .release_valid(generation_release),
  .release_ready(prelease),
  .release_tag(source_tag),
  .release_generation(generation),
  .owner_lock(source_owner_lock),
  .debug_phase(source_phase),
  .debug_setup_phase(source_setup_phase),
  .debug_codes_lock(source_codes_lock),
  .debug_projection_phase(source_projection_phase),
  .debug_role(source_projection_role),
  .debug_code_reads(source_debug_code_reads),
  .debug_K_ACKs(source_debug_K_ACKs),
  .debug_V_ACKs(source_debug_V_ACKs),
  .debug_coefficient_reads(source_debug_coefficient_reads)
 );
 reg [3:0]source_state;
 reg [31:0]source_tag,position_scale,generation,source_fault,token_tag,last_token_tag;
 reg [7:0]position_zero;reg [11:0]position_offset;
 reg [2:0]generation_layer,layers_released;
 reg token_live,reset_drain;
 reg memory_pending,fixed_pending,position_pending;
 reg [31:0]m_session,m_generation,m_epoch,m_tag,m_word;
 reg [2:0]m_region,m_layer;reg m_role,m_write;
 reg [31:0]f_session,f_generation,f_epoch,f_tag;reg [2:0]f_layer;reg f_role;reg [8:0]f_row;
 reg [31:0]p_session,p_generation,p_tag;reg [17:0]p_word;
 reg packet_pending,packet_valid;reg [255:0]packet;
 reg [31:0]packet_session,packet_generation,packet_epoch,packet_word;
 reg [2:0]packet_layer,packet_head,lane;reg packet_role;reg [15:0]packet_base;
 reg [18:0]layer_scalars;reg [15:0]layer_packets;
 wire producer_reset=reset||source_state==PDRAIN||source_state==PERROR;
 wire source_draining=source_state==EMPTY||source_state==PDRAIN||source_state==PERROR;
 wire memory_match=memory_pending&&source_response_session==m_session&&source_response_generation==m_generation&&source_response_epoch==m_epoch&&source_response_tag==m_tag&&source_response_word==m_word&&source_response_region==m_region&&source_response_layer==m_layer&&source_response_role==m_role&&source_response_write==m_write;
 wire fixed_match=fixed_pending&&source_fixed_response_session==f_session&&source_fixed_response_generation==f_generation&&source_fixed_response_epoch==f_epoch&&source_fixed_response_tag==f_tag&&source_fixed_response_layer==f_layer&&source_fixed_response_role==f_role&&source_fixed_response_row==f_row;
 wire position_match=position_pending&&source_position_response_session==p_session&&source_position_response_generation==p_generation&&source_position_response_tag==p_tag&&source_position_response_word==p_word;
 wire memory_bad=source_response_valid&&!memory_match;
 wire fixed_bad=source_fixed_response_valid&&!fixed_match;
 wire position_bad=source_position_response_valid&&!position_match;
 wire physical_quiet=source_memory_idle&&source_fixed_idle&&source_position_idle&&!source_response_valid&&!source_fixed_response_valid&&!source_position_response_valid&&!memory_pending&&!fixed_pending&&!position_pending;
 wire source_quiet=physical_quiet&&source_fresh_idle&&!source_fresh_valid&&!packet_pending&&!packet_valid&&!consumer_valid;
 wire source_expected=source_state>=CODES&&source_state<=GRELEASE;
 wire session_bad=source_expected&&(!psession||psession_tag!=source_tag);
 wire generation_bad=(source_state==RETAIN||source_state==GRELEASE)&&(!presult||presult_tag!=source_tag||presult_generation!=generation||presult_layer!=generation_layer);
 wire demand=token_live&&kv_want&&source_state==RETAIN&&!packet_pending&&!packet_valid;
 wire demand_role=kv_expected_index>=16'((40+FRAMES*40));
 wire [15:0]demand_element=kv_expected_index-(demand_role?16'((40+FRAMES*40)):16'd40);
 wire [8:0]demand_frame=9'(demand_element/16'd40);
 wire [5:0]demand_channel=6'(demand_element%16'd40);
 wire [31:0]demand_word={23'd0,demand_frame}*32'd40+{29'd0,kv_expected_head}*32'd5+{26'd0,demand_channel}/32'd8;
 wire demand_bad=demand&&(kv_expected_layer!=generation_layer||{29'b0,kv_expected_head}>=8||kv_expected_index<40||{16'b0,kv_expected_index}>=((40+FRAMES*80))||{23'b0,demand_frame}>=(FRAMES)||demand_word>=(RV_WORDS)||demand_channel[2:0]!=0||layer_scalars!={16'd0,kv_expected_head}*19'((FRAMES*80))+(demand_role?19'(RV_WORDS):19'd0)+{3'd0,demand_element});
 wire packet_bad=consumer_valid&&(!packet_pending||consumer_tag!=packet_session||consumer_generation!=packet_generation||packet_epoch!=token_tag||consumer_role!=packet_role||consumer_word!=packet_word);
 wire scalar_bad=token_live&&packet_valid&&(!kv_want||kv_expected_layer!=packet_layer||kv_expected_head!=packet_head||kv_expected_index!=packet_base+{13'd0,lane});
 // Release identity failure is latched below: feeding the accepted release
 // pulse back through warm_abort would create a combinational acceptance loop.
 wire raw_bad=memory_bad||fixed_bad||position_bad||session_bad||generation_bad||demand_bad||packet_bad||scalar_bad;
 wire child_fault=source_state!=EMPTY&&source_state!=PSTART&&source_state!=PDRAIN&&source_state!=PERROR&&pfault!=0;
 assign token_warm_abort=!reset&&token_live&&token_done_fault==0&&(raw_bad||child_fault||source_fault!=0);
 wire consumer_request=!reset&&demand&&!raw_bad&&source_fault==0;
 wire consumer_accept=!reset&&source_state==RETAIN&&packet_pending&&!packet_valid&&!raw_bad&&source_fault==0;
 wire source_release=!reset&&source_state==CODES&&!token_live&&source_release_valid&&source_release_tag==source_tag&&source_quiet&&!raw_bad&&psrelease;
 wire generation_release=!reset&&source_state==GRELEASE&&source_quiet&&!raw_bad&&prelease;
 wire token_done_accept=done_valid&&done_ready;
 wire token_success_ready=source_state==CODES&&layers_released==6&&source_fault==0;
 assign source_mem_valid=!reset&&!producer_reset&&pmvalid&&!memory_pending&&!raw_bad&&!child_fault&&source_fault==0;
 assign source_fixed_valid=!reset&&!producer_reset&&pfvalid&&!fixed_pending&&!raw_bad&&!child_fault&&source_fault==0;
 assign source_position_valid=!reset&&!producer_reset&&ppvalid&&!position_pending&&!raw_bad&&!child_fault&&source_fault==0;
 assign source_mem_epoch=token_live?token_tag:32'd0;
 assign source_fixed_epoch=token_live?token_tag:32'd0;
 assign source_fresh_ready=!reset&&(source_draining||pfresh);
 assign source_response_ready=!reset&&(source_draining||memory_bad||(memory_pending&&pmready));
 assign source_fixed_response_ready=!reset&&(source_draining||fixed_bad||(fixed_pending&&pfready));
 assign source_position_response_ready=!reset&&(source_draining||position_bad||(position_pending&&ppready));
 assign start_ready=!reset&&source_state==CODES&&source_quiet&&psession&&pgready&&!token_live&&token_ready&&!raw_bad&&source_fault==0&&!source_release_valid;
 assign done_valid=!reset&&token_done_valid&&source_quiet&&!raw_bad&&((token_done_fault!=0)||(token_success_ready&&!child_fault));
 assign done_fault=token_done_fault;
 assign owner_lock=token_owner||token_live;
 assign source_start_ready=!reset&&source_state==EMPTY&&source_quiet&&!token_live;
 assign source_session_valid=!reset&&source_expected&&psession&&!raw_bad&&source_fault==0;
 assign source_session_tag=source_tag;assign source_generation=generation;assign source_token_epoch=token_live?token_tag:0;
 assign source_ready=!reset&&source_state==CODES&&source_quiet&&source_session_valid&&pgready;
 assign source_release_ready=!reset&&source_state==CODES&&!token_live&&source_quiet&&!raw_bad&&psrelease;
 assign source_error_valid=!reset&&source_state==PERROR&&source_quiet;
 assign source_error=source_fault;
 assign kv_idle=!packet_pending&&!packet_valid&&!consumer_valid&&!consumer_request;
 assign kv_valid=!reset&&token_live&&source_state==RETAIN&&packet_valid&&!raw_bad&&source_fault==0;
 assign kv_tag=token_tag;assign kv_layer=packet_layer;assign kv_head=packet_head;assign kv_index=packet_base+{13'd0,lane};assign kv_value=packet[lane*32+:32];
 assign bridge_accept=kv_valid&&kv_ready;
 assign bridge_packet_pending=packet_pending;assign bridge_packet_valid=packet_valid;
 assign bridge_value=kv_value;assign bridge_generation=packet_generation;assign bridge_epoch=packet_epoch;
 assign bridge_layer=kv_layer;assign bridge_head=kv_head;assign bridge_index=kv_index;
 assign source_memory_pending=memory_pending;assign source_fixed_pending=fixed_pending;assign source_position_pending=position_pending;
 assign bridge_layer_scalars=layer_scalars;assign bridge_layer_packets=layer_packets;assign bridge_layers_released=layers_released;
 assign source_owner_phase=source_state;
 always @(posedge clk)begin
  if(reset)begin
   source_state<=PDRAIN;reset_drain<=1;source_tag<=0;position_scale<=0;position_zero<=0;position_offset<=0;generation<=0;generation_layer<=0;
   source_fault<=0;token_live<=0;token_tag<=0;last_token_tag<=0;layers_released<=0;
   memory_pending<=0;fixed_pending<=0;position_pending<=0;
   m_session<=0;m_generation<=0;m_epoch<=0;m_tag<=0;m_word<=0;m_region<=0;m_layer<=0;m_role<=0;m_write<=0;
   f_session<=0;f_generation<=0;f_epoch<=0;f_tag<=0;f_layer<=0;f_role<=0;f_row<=0;
   p_session<=0;p_generation<=0;p_tag<=0;p_word<=0;
   packet_pending<=0;packet_valid<=0;packet<=0;packet_session<=0;packet_generation<=0;packet_epoch<=0;packet_word<=0;
   packet_layer<=0;packet_head<=0;packet_role<=0;packet_base<=0;lane<=0;layer_scalars<=0;layer_packets<=0;
  end else begin
   if(source_mem_valid&&source_mem_ready)begin
    memory_pending<=1;m_session<=source_mem_session;m_generation<=source_mem_generation;m_epoch<=source_mem_epoch;
    m_tag<=source_mem_tag;m_word<=source_mem_word;m_region<=source_mem_region;m_layer<=source_mem_layer;m_role<=source_mem_role;m_write<=source_mem_write;
   end
   if(source_fixed_valid&&source_fixed_ready)begin
    fixed_pending<=1;f_session<=source_fixed_session;f_generation<=source_fixed_generation;f_epoch<=source_fixed_epoch;
    f_tag<=source_fixed_tag;f_layer<=source_fixed_layer;f_role<=source_fixed_role;f_row<=source_fixed_row;
   end
   if(source_position_valid&&source_position_ready)begin
    position_pending<=1;p_session<=source_position_session;p_generation<=source_position_generation;p_tag<=source_position_tag;p_word<=source_position_word;
   end
   if(source_response_valid&&source_response_ready&&memory_match)memory_pending<=0;
   if(source_fixed_response_valid&&source_fixed_response_ready&&fixed_match)fixed_pending<=0;
   if(source_position_response_valid&&source_position_response_ready&&position_match)position_pending<=0;
   if(source_draining&&source_memory_idle&&!source_response_valid)memory_pending<=0;
   if(source_draining&&source_fixed_idle&&!source_fixed_response_valid)fixed_pending<=0;
   if(source_draining&&source_position_idle&&!source_position_response_valid)position_pending<=0;
   if(start_valid&&start_ready)begin
    token_live<=1;token_tag<=start_tag;last_token_tag<=start_tag;layers_released<=0;layer_scalars<=0;layer_packets<=0;
    if(start_tag==0||start_tag<=last_token_tag||start_frames!=9'(FRAMES))begin source_fault<=32'h01000000;source_state<=PDRAIN;end
   end
   if(token_done_accept)token_live<=0;
   if(consumer_request&&consumer_ready)begin
    packet_pending<=1;packet_session<=source_tag;packet_generation<=generation;packet_epoch<=token_tag;
    packet_layer<=generation_layer;packet_head<=kv_expected_head;packet_role<=demand_role;packet_word<=demand_word;packet_base<=kv_expected_index;
   end
   if(consumer_valid&&consumer_accept)begin packet_pending<=0;packet_valid<=1;packet<=consumer_data;lane<=0;layer_packets<=layer_packets+1'b1;end
   if(bridge_accept)begin
    layer_scalars<=layer_scalars+1'b1;
    if(lane==7)begin packet_valid<=0;lane<=0;end else lane<=lane+1'b1;
   end
   if(source_state==PDRAIN)begin
    packet_pending<=0;packet_valid<=0;
    if(source_quiet)source_state<=reset_drain?EMPTY:PERROR;
   end else if(source_state==PERROR)begin
    if(source_error_valid&&source_error_ready&&!token_live)begin source_state<=EMPTY;source_fault<=0;end
   end else if(source_state==EMPTY)begin
    if(source_start_valid&&source_start_ready)begin
     source_tag<=source_start_tag;position_scale<=source_start_position_scale;position_zero<=source_start_position_zero;position_offset<=source_start_position_offset;
     generation<=0;generation_layer<=0;source_fault<=0;reset_drain<=0;source_state<=PSTART;
    end
   end else if(raw_bad||child_fault)begin source_fault<=memory_bad?32'h1:fixed_bad?32'h2:position_bad?32'h4:packet_bad?32'h8:child_fault?32'h10:32'h20;source_state<=PDRAIN;end
   else if(token_live&&token_done_fault!=0&&source_state!=CODES)begin
    // A healthy source is conservatively invalidated if token cancellation
    // occurs while any generation/packet is live. Committed history survives.
    source_fault<=32'h40;source_state<=PDRAIN;
   end else if(compact_layer_release)begin
    if(source_state!=RETAIN||layer_release_tag!=token_tag||layer_release_layer!=generation_layer||layer_release_layer!=layers_released||
       layer_release_session!=compact_session_id||layer_release_attempt!=compact_attempt||layer_release_position!=start_position_latched||
       layer_scalars!=19'((FRAMES*640))||layer_packets!=16'((FRAMES*80))||!source_quiet)begin source_fault<=32'h80;source_state<=PDRAIN;end
    else begin layers_released<=layers_released+1'b1;source_state<=GRELEASE;end
   end else case(source_state)
    PSTART:if(ps)source_state<=SETUP;
    SETUP:if(pgready&&psession&&source_quiet)source_state<=CODES;
    CODES:begin
     if(source_release)source_state<=PEND;
     else if(token_live&&kv_want)begin
      if(kv_expected_layer!=layers_released||kv_expected_head!=0||kv_expected_index!=40||layers_released>=6||generation==32'hffffffff)begin source_fault<=32'h100;source_state<=PDRAIN;end
      else begin generation<=generation+1'b1;generation_layer<=kv_expected_layer;layer_scalars<=0;layer_packets<=0;source_state<=GSTART;end
     end
    end
    GSTART:if(pgready)source_state<=GRUN;
    GRUN:if(pd&&source_quiet)begin
     if(pfault!=0||pdone_tag!=source_tag||pdone_generation!=generation)begin source_fault<=32'h200;source_state<=PDRAIN;end
     else source_state<=GACCEPT;
    end
    GACCEPT:if(pd&&source_quiet)source_state<=RETAIN;
    RETAIN:begin end
    GRELEASE:if(generation_release)source_state<=CODES;
    PEND:if(ps&&source_quiet)source_state<=EMPTY;
    default:begin source_fault<=32'h80000000;source_state<=PDRAIN;end
   endcase
  end
 end
 reg [6:0]start_position_latched;
 always @(posedge clk)begin
  if(reset)start_position_latched<=0;
  else if(start_valid&&start_ready)start_position_latched<=start_position;
 end

endmodule
