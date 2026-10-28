// Source-only: actual frontend + encoder, one model and one clock counter.
// Frozen frontend/encoder numerical service checks are in the adjacent headers.
#include "Vrv_allonchip_top_v1.h"
#include "verilated.h"
#include <CommonCrypto/CommonDigest.h>
#include <dlfcn.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <functional>
#include <map>
#include <type_traits>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using Top=Vrv_allonchip_top_v1;
static constexpr unsigned RV_FRAMES=64,RV_VALUES=RV_FRAMES*320,RV_WORDS=RV_FRAMES*40,RV_CODEWORDS=RV_FRAMES*10,RV_BATCHES=(RV_FRAMES+7)/8;
#include "frontend_services.hpp"
#include "encoder_services.hpp"
#include "producer_services.hpp"
#include "greedy_observer.hpp"
static void initialize(Top&t){





/* onboard table owns e_producers_idle initial0 */
/* onboard table owns h_producers_idle initial0 */
t.row_transfer_enable=0;

t.compact_setup_valid=0;
t.compact_setup_session=0;
for(unsigned i=0;i<8;i++)t.compact_setup_image_id[i]=0;









/* backend-owned compact_memory_idle original=0 */
/* backend-owned compact_mem_ready original=0 */
/* backend-owned compact_response_valid original=0 */
/* backend-owned compact_response_write original=0 */
/* backend-owned compact_response_region original=0 */
/* backend-owned compact_response_layer original=0 */
/* backend-owned compact_response_phase original=0 */
/* backend-owned compact_response_position original=0 */
/* backend-owned compact_response_packet original=0 */
/* backend-owned compact_response_word original=0 */
/* backend-owned compact_response_session original=0 */
/* backend-owned compact_response_attempt original=0 */
/* backend-owned compact_response_sequence original=0 */
/* backend-owned compact_response_data */
/* RTL learned_idle observed only; original initial0 removed */
/* RTL learned_valid observed only; original initial0 removed */
/* RTL learned_tag observed only */
/* RTL learned_layer observed only */
/* RTL learned_index observed only */
/* RTL learned_values observed only */










/* onboard table owns e_index_request_ready; initialization is observer-only */
/* onboard table owns e_index_response_valid; initialization is observer-only */
/* onboard table owns e_index_response_tag; initialization is observer-only */
/* onboard table owns e_index_response_group; initialization is observer-only */
/* onboard table owns e_index_response_row; initialization is observer-only */
/* onboard table owns e_index_response_data; initialization is observer-only */
/* onboard table owns e_book_request_ready; initialization is observer-only */
/* onboard table owns e_book_response_valid; initialization is observer-only */
/* onboard table owns e_book_response_tag; initialization is observer-only */
/* onboard table owns e_book_response_page; initialization is observer-only */
/* onboard table owns e_book_response_beat; initialization is observer-only */
/* onboard table owns e_book_response_data; initialization is observer-only */
/* onboard table owns h_index_request_ready; initialization is observer-only */
/* onboard table owns h_index_response_valid; initialization is observer-only */
/* onboard table owns h_index_response_tag; initialization is observer-only */
/* onboard table owns h_index_response_group; initialization is observer-only */
/* onboard table owns h_index_response_row; initialization is observer-only */
/* onboard table owns h_index_response_data; initialization is observer-only */
/* onboard table owns h_book_job_tag; initialization is observer-only */
/* onboard table owns h_load_start_valid; initialization is observer-only */
/* onboard table owns h_load_tags; initialization is observer-only */
/* onboard table owns h_load_valid; initialization is observer-only */
/* onboard table owns h_load_data; initialization is observer-only */
/* onboard table owns h_load_data_tags; initialization is observer-only */
/* onboard table owns h_load_data_beats; initialization is observer-only */
/* onboard table owns h_commit_valid; initialization is observer-only */
/* onboard table owns h_commit_tags; initialization is observer-only */
/* producer backend source_memory_idle initial0 observed-only */
/* producer backend source_mem_ready initial0 observed-only */
/* producer backend source_response_session initial0 observed-only */
/* producer backend source_response_generation initial0 observed-only */
/* producer backend source_response_valid initial0 observed-only */
/* producer backend source_response_write initial0 observed-only */
/* producer backend source_response_region initial0 observed-only */
/* producer backend source_response_layer initial0 observed-only */
/* producer backend source_response_role initial0 observed-only */
/* producer backend source_response_tag initial0 observed-only */
/* producer backend source_response_word initial0 observed-only */
/* producer backend full response data observed-only */
t.source_position_response_session=0;
t.source_position_response_generation=0;
t.source_position_idle=0;
t.source_position_ready=0;
t.source_position_response_valid=0;
t.source_position_response_tag=0;
t.source_position_response_word=0;
t.source_position_response_data=0;










t.source_start_valid=0;
t.source_start_tag=0;
t.source_start_position_scale=0;
t.source_start_position_zero=0;
t.source_start_position_offset=0;


t.source_error_ready=0;
/* producer backend source_response_epoch initial0 observed-only */

 /* onboard table owns e_producers_idle initial1 *//* onboard table owns h_producers_idle initial1 *//* backend-owned compact_memory_idle original=1 *//* RTL learned_idle observed only; original initial1 removed *//* producer backend source_memory_idle initial1 observed-only */t.source_position_idle=1;/* RTL-owned fixedbook idle observedonly */
 t.external_rsp_backing_owner=0;t.external_rsp_job=0;t.external_rsp_session=0;t.external_rsp_sequence=0;

 t.begin_valid=0;t.begin_job_tag=0;t.begin_session=0;t.begin_source_tag=0;t.begin_token_tag_base=0;t.begin_frames=64;t.token_ready=0;t.job_done_ready=0;
 t.learned_por_reset=1;t.frontend_por_reset=1;t.table_por_reset=1;t.producer_por_reset=1;t.history_por_reset=1;t.bank_por_reset=1;t.clk=0;t.reset=1;t.step_enable=1;t.up_start_valid=0;t.up_start_tag=0;
 t.external_idle=1;t.external_req_ready=1;
 t.external_rsp_valid=0;t.external_rsp_client=0;t.external_rsp_scalar=0;t.external_rsp_write=0;t.external_rsp_layer=0;t.external_rsp_origin=0;t.external_rsp_region=0;t.external_rsp_tag=0;t.external_rsp_word=0;
 for(unsigned i=0;i<8;i++)t.external_rsp_data[i]=0;
 t.up_done_ready=0;t.up_pcm_producer_idle=1;t.up_pcm_valid=0;t.up_pcm_tag=0;t.up_pcm_index=0;t.up_pcm_value=0;
 t.up_head_fixed_idle=1;t.up_head_fixed_ready=1;t.up_head_response_valid=0;t.up_head_response_layer=0;t.up_head_response_tag=0;t.up_head_response_role=0;t.up_head_response_head=0;t.up_head_response_row=0;
 for(unsigned i=0;i<10;i++)t.up_head_response_data[i]=0;
 t.up_O_fixed_idle=1;t.up_O_fixed_ready=1;t.up_O_response_valid=0;t.up_O_response_layer=0;t.up_O_response_tag=0;t.up_O_response_row=0;
 for(unsigned i=0;i<80;i++)t.up_O_response_data[i]=0;
}
struct TransferObserver {
 Top&t;enc::Services&e;uint64_t&clocks;std::ofstream&encoded;
 bool pending=false,held=false,response_seen=false,response_held=false;uint64_t due=0,requests=0,replies=0,serialized=0;
 std::array<uint32_t,7>identity{},held_identity{};enc::Packet held_payload{};
 TransferObserver(Top&model,enc::Services&encoder,uint64_t&clock,std::ofstream&output):t(model),e(encoder),clocks(clock),encoded(output){}
 std::array<uint32_t,7>request(){return {t.tr_req_client,t.tr_req_backing_owner,t.tr_req_region,t.tr_req_job,t.tr_req_session,t.tr_req_sequence,t.tr_req_word};}
 void drive(){
  // Only the unused EXTERNAL provider is quiesced. No onboard/backend signal driven.
  t.external_idle=1;t.external_req_ready=1;t.external_rsp_valid=0;
 }
 void capture(){
  enc::require(!t.transfer_fault&&!t.physical_protocol_fault&&!t.encoder_bank_fault&&!t.encoder_router_fault,"actual onboard transfer/shared-port fault");
  if(!t.handoff_complete&&t.transfer_requests)enc::require(t.up_enc_result_valid&&t.up_encoder_backing_lease_held&&t.up_encoder_result_tag==e.tag,"actual final lease held through every transfer/ACK");
  auto current=request();
  if(held)enc::require(t.tr_req_valid&&current==held_identity,"held transfer request identity");
  held=t.tr_req_valid&&!t.tr_req_ready;if(held)held_identity=current;
  if(t.observed_rsp_valid){
   enc::require(pending&&t.physical_pending_transfer,"onboard alias response must have actual retained transfer owner");
   enc::require(t.observed_rsp_client==identity[0]&&t.observed_rsp_backing_owner==identity[1]&&t.observed_rsp_region==identity[2]&&t.observed_rsp_job==identity[3]&&t.observed_rsp_session==identity[4]&&t.observed_rsp_sequence==identity[5]&&t.observed_rsp_word==identity[6]&&!t.observed_rsp_scalar&&!t.observed_rsp_write&&t.observed_rsp_layer==6&&!t.observed_rsp_origin&&t.observed_rsp_tag==identity[5],"actual RTL alias response full identity");
   enc::require(clocks>=due,"actual alias reply before qualified N+2 PREedge");
   if(!response_seen){enc::require(clocks==due,"first actual alias reply exactly N+2 PREedge");response_seen=true;}
   enc::Packet payload{};for(unsigned lane=0;lane<8;lane++){
    payload[lane]=t.observed_rsp_data[lane];
    enc::require(payload[lane]==e.input.encoded.at(identity[6]*8+lane)&&payload[lane]==e.expected_bank[0].at(identity[6])[lane],"actual RTL alias byte versus native and comparison mirror");
   }
   if(response_held)enc::require(payload==held_payload,"held actual alias payload stable");
   response_held=!t.observed_rsp_ready;held_payload=payload;
   enc::require(bool(t.observed_rsp_ready)==bool(t.tr_rsp_ready),"observed matching physical reply accepted by actual transfer consumer");
   if(t.observed_rsp_ready){
    for(auto value:payload)encoded.write(reinterpret_cast<const char*>(&value),4);
    enc::require(bool(encoded),"serialize actual RTL alias ACK data");serialized+=8;pending=false;replies++;
   }
  }else enc::require(!response_held,"held alias reply withdrawn");
  if(t.tr_req_valid&&t.tr_req_ready){
   enc::require(!pending&&current[0]==3&&current[1]==2&&current[2]==0&&current[3]==e.tag&&current[5]==requests+1&&current[6]==requests&&requests<RV_WORDS,"client3 actual backing owner2/region0 sequential transfer");
   enc::require(t.up_enc_result_valid&&t.up_encoder_backing_lease_held&&e.commits==1&&!e.m.active&&!e.h.active&&!e.o.active,"actual qualified encoder final backing before RTL readback");
   identity=current;pending=true;response_seen=false;due=clocks+2;requests++;
  }
 }
};

static void encoder_terminal(enc::Services&e){
 auto&t=e.t;
 e.check(t.up_enc_done_tag==e.tag&&!t.up_enc_done_fault&&t.up_enc_done_flags==e.input.final_flags,"native encoder terminal tag/flags");
 e.check(t.up_encoder_debug_completed_layers==6&&e.layer_accepts==6&&e.layer_releases==6,"six actual layer barriers");
 e.check(t.up_encoder_debug_final_ACKs==RV_WORDS&&t.up_encoder_debug_initial_words==RV_WORDS&&t.up_encoder_debug_reload_reads==RV_WORDS*5&&t.up_encoder_debug_reload_values==RV_VALUES*5,"complete actual initial/reload/final counts");
 e.check(e.reads[6][19]==RV_WORDS&&e.reads[6][22]==RV_WORDS&&e.writes[6][14]==RV_WORDS&&e.acks[6][14]==RV_WORDS,"final exact Skip owner traffic");
 for(unsigned i=0;i<RV_VALUES;i++)e.check(e.expected_bank[0][i/8][i%8]==e.input.encoded[i],"whole actual encoded final bank");e.jobs++;
}
int main(int argc,char**argv){try{
 Verilated::commandArgs(argc,argv);if(argc!=11)return 2;
 Top t;initialize(t);front::Services f(t,argv[1],"","","","");enc::Services e(t,argv[2]);uint64_t common_clocks=0;
 prod::Harness p(t,common_clocks,argv[4],argv[5],argv[6],argv[7],argv[8],argv[9],true,argv[3]);
 enc::require(p.producer.encoded==e.input.encoded&&p.tokens.size()==5&&p.winners.back()==2,"own full frontend/encoder/producer/EOS contract");
 enc::require(std::string(argv[10])=="positive"||std::string(argv[10])=="fixture","declared full-chain mode");
 if(std::string(argv[10])=="fixture"){enc::require(std::string(argv[10])=="fixture","zero-clock loader mode");enc::Words all;
  for(unsigned chunk=0;chunk<16;chunk++){f.load_case(chunk);all.insert(all.end(),f.features.begin(),f.features.end());}
  enc::require(all==e.input.gold[0].image[19],"whole chronological native frontend equals encoder source reference");
  std::cout<<"COMMON_NUMERIC_FIXTURE_PASS frames="<<RV_FRAMES<<" values="<<all.size()<<" native_final_flags="<<e.input.final_flags<<" clocks=0"<<std::endl;return 0;
 }
 std::ofstream features(std::string(argv[3])+"/actual-frontend-features.bin",std::ios::binary|std::ios::trunc);
 std::ofstream encoded(std::string(argv[3])+"/actual-encoded.bin",std::ios::binary|std::ios::trunc);
 enc::require(bool(features)&&bool(encoded),"fresh actual output files");
 f.actual_feature_output=&features;f.step();f.step();t.learned_por_reset=0;t.frontend_por_reset=0;t.table_por_reset=0;t.producer_por_reset=0;t.history_por_reset=0;t.bank_por_reset=0;t.reset=0;
 for(unsigned n=0;!t.up_start_ready;n++){f.step();enc::require(n<100,"common startup drain");}
 const uint32_t session=0x10000;t.up_start_tag=session;t.up_start_valid=1;e.tag=session;f.step();t.up_start_valid=0;t.up_start_tag=0xbadfeed;
 bool initialized_chunk=false,encoder_active=false,encoder_checked=false;unsigned completed_chunks=0;uint32_t frontend_flags=0;
 uint64_t clock= f.clocks,encoder_begin=0;auto wall=std::chrono::steady_clock::now();
 for(uint64_t n=0;n<1000000000ULL;n++){
  t.eval();
  if(t.up_front_start_valid&&t.up_front_start_ready){
   enc::require(!initialized_chunk&&completed_chunks==t.up_chunk_index&&completed_chunks<16,"chronological frontend acquisition");
   f.load_case(t.up_chunk_index);f.tag=t.up_chunk_tag;f.sent=0;f.input_pending=false;f.prewrite_count=0;
   f.copy_reads=f.copy_writes=0;f.write_counts.fill(0);f.read_counts.fill(0);for(auto&a:f.service)a.fill(0);
   f.authority();initialized_chunk=true;
  }
  bool front_commit=t.up_front_commit;
  if(front_commit){
   enc::require(initialized_chunk&&t.up_front_done_tag==f.tag&&!t.up_front_done_fault&&!f.reply.active&&f.sent==1280&&!f.input_pending,"whole frontend commit identity/drain");
   f.check_complete();f.authority();f.check(t.up_front_history_location==1,"PREFIX authority before commit");
   f.check(f.copy_writes==3840&&f.copy_reads==(completed_chunks?3840:0),"history copy conservation");
  }
  if(t.up_debug_phase>=8&&!encoder_active){
   enc::require(completed_chunks==16&&!f.reply.active&&t.up_published_values==RV_VALUES&&t.up_copy_replies==RV_VALUES,"front-to-encoder publication/drain barrier");
   e.clocks=clock;encoder_begin=clock;encoder_active=true;enc::require(f.feature_packets==RV_VALUES,"whole actual frontend alias ACK serialization");features.flush();enc::require(bool(features),"actual frontend output saved before encoder");
  }
  if(!encoder_active){f.step();clock=f.clocks;}
  else{
   t.step_enable=1;t.up_pcm_valid=0;t.up_pcm_producer_idle=1;
   if(t.up_enc_done_valid&&!encoder_checked){encoder_terminal(e);encoder_checked=true;}
   e.tick();clock=e.clocks;
  }
  if(front_commit){
   frontend_flags|=t.up_front_done_flags;completed_chunks++;f.jobs++;f.committed+=1280;f.expected_frames+=16;
   /* Actual frontend features are serialized exclusively on real client1 bank alias ACKs in front::Services. */
   for(unsigned c=0;c<320;c++)for(unsigned k=0;k<4;k++)f.committed1[c*4+k]=f.memory[2][c*20+16+k];
   for(unsigned c=0;c<640;c++)for(unsigned k=0;k<4;k++)f.committed2[c*4+k]=f.memory[6][c*12+8+k];
   f.check(t.up_front_history_location==2&&t.up_front_features_lock&&t.up_front_frame_count==f.expected_frames,"joint TAIL/feature lease publication");f.authority();initialized_chunk=false;
   std::cout<<"CHUNK_COMMIT chunk="<<completed_chunks-1<<" common_clocks="<<clock<<" history_frames="<<f.expected_frames<<std::endl;
  }
  if(n&&n%5000000==0)std::cout<<"PROGRESS common_clocks="<<clock<<" phase="<<unsigned(t.up_debug_phase)<<" chunks="<<completed_chunks<<" encoder_layer="<<unsigned(t.up_enc_layer)<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-wall).count()<<std::endl;
  enc::require(!t.up_done_fault&&!t.physical_protocol_fault&&!t.transfer_fault,"new bridge/shared-port/controller fault");
  if(t.up_done_valid){
   enc::require(encoder_checked&&completed_chunks==16&&t.up_done_tag==session&&!f.reply.active&&!e.m.active&&!e.h.active&&!e.o.active,"whole common terminal");
   enc::require(e.starts==1&&e.DONEs==1&&e.commits==1&&e.source_words==RV_WORDS&&e.initial_retirements==6&&e.context_retirements==6,"original encoder start/commit/source/retirement conservation");
   const uint32_t combined_flags=t.up_done_flags;enc::require(combined_flags==(frontend_flags|e.input.final_flags),"whole accumulated numerical flags");
   enc::require(e.jobs==1&&e.faults==0&&e.resets==0&&e.starts==e.jobs+e.faults+e.resets&&e.DONEs==e.jobs+e.faults,"original positive start/DONE/job coverage");
   enc::require(!e.stray&&e.requests==e.replies&&e.head_requests==e.head_replies&&e.O_requests==e.O_replies,"original encoder final service conservation");
   enc::require(e.checks==RV_VALUES*41+RV_WORDS*4&&e.requests==6*(RV_FRAMES*940+RV_BATCHES*39840+320)+RV_WORDS*8&&e.head_requests==6*RV_BATCHES*7680&&e.O_requests==6*RV_BATCHES*320,"original encoder whole shape counts");
   constexpr uint64_t front_service=5120+102400+409600+5120+5120+2048000+640+1126400+5120+5120+5120+1280+1024000+320+563200;
   enc::require(f.requests==f.replies&&f.requests-f.copier_requests==16*(front_service+1280+3840)+15*3840&&f.copier_requests==RV_VALUES&&f.copier_replies==RV_VALUES,"whole frontend and copier request/reply conservation");
   enc::require(f.input_offers==16*1280&&f.input_replies==16*1280&&f.jobs==16&&f.committed==RV_VALUES&&f.all_copy_writes==16*3840&&f.all_copy_reads==15*3840,"whole frontend input/history/features conservation");
   enc::require(t.up_accepted_packets==RV_WORDS&&t.up_published_values==RV_VALUES&&t.up_copy_replies==RV_VALUES,"actual SRAM whole extent conservation");
   for(unsigned i=0;i<4;i++){e.tick();clock=e.clocks;enc::require(t.up_done_valid&&t.up_done_tag==session&&t.up_done_flags==combined_flags&&!t.up_done_fault&&t.up_owner_lock,"held common terminal identity/flags");}
   t.up_done_ready=1;e.tick();t.up_done_ready=0;enc::require(t.up_result_valid&&t.up_encoder_backing_lease_held,"actual retained encoded lease");
   features.flush();enc::require(bool(features),"whole actual frontend output persisted");
   // Encoder mirror is comparison-only. Actual encoded output is written below
   // only from matching RTL client3 alias response ACK payloads.
   t.up_start_valid=1;t.up_start_tag=session+1;
   for(unsigned i=0;i<4;i++){enc::require(!t.up_start_ready&&!t.up_enc_start_ready&&t.up_result_valid&&t.up_owner_lock&&t.up_encoder_backing_lease_held,"four blocked starts during actual retained lease");e.tick();e.blocked_starts++;}
   t.up_start_valid=0;
   // Autonomous ownership outputs are observations. Original v9 wrong-release
   // negative remains preserved historical proof; this successor needs its own
   // connected controller wrong-identity/reset/held-release negative qualification.
   const uint64_t encoder_end=e.clocks;common_clocks=e.clocks;
   TransferObserver transfer(t,e,common_clocks,encoded);p.transfer_hook=[&](bool capture){if(capture)transfer.capture();else transfer.drive();};
   p.compact.cold_reset();p.producer.cold_reset();p.committed_terms=0;p.feedback=1;p.hold_output=false;
   p.setup();p.producer.start_source();
   for(unsigned i=0;!t.handoff_complete;i++){p.step(false);enc::require(i<100,"actual retained encoded handoff publication");}
   encoded.flush();enc::require(bool(encoded)&&transfer.serialized==RV_VALUES,"whole actual RTL alias ACK output persisted");
   const uint32_t actual_source_ACKs=t.source_debug_fresh_ACKs;
   enc::require(transfer.requests==RV_WORDS&&transfer.replies==RV_WORDS&&!transfer.pending&&!t.physical_pending&&t.transfer_packets==RV_WORDS&&actual_source_ACKs==RV_WORDS&&p.producer.bankA==e.input.encoded&&p.producer.setups==1,"whole actual shared-port encoded transfer/ACK barrier");
   GreedyObserver observer(p,e,session);p.observation_hook=[&](){observer.capture();};
   t.begin_job_tag=session;t.begin_session=t.compact_session_id;t.begin_source_tag=t.source_session_tag;t.begin_token_tag_base=0x100000;t.begin_frames=64;
   t.token_ready=0;t.job_done_ready=0;t.begin_valid=1;
   for(unsigned n=0;;n++){p.step(false);if(p.actual_begin_ACK)break;enc::require(n<500,"autonomous begin actual enabled-edge ACK bound");}
   t.begin_valid=0;
   // Actual RTL decides BOS, feedback and EOS. Literal history capacity 66 is
   // in the RTL wrapper; fixture token count is used only for comparison.
   const uint64_t autonomous_begin=common_clocks;
   while(!t.job_done_valid){
    t.token_ready=(common_clocks%7)>=4;p.step();
    enc::require(common_clocks-autonomous_begin<700000000,"autonomous job control clock bound");
    enc::require(!t.job_done_abort&&!t.job_recovery_required&&!t.transfer_fault&&!t.physical_protocol_fault&&!t.source_error_valid&&!t.table_fault,"autonomous job fault is not EOS/cap success");
   }
   observer.finish();
   std::array<uint64_t,9> status{t.job_done_tag,t.job_done_session,t.job_done_count,t.job_done_reason,t.job_done_eos,t.job_source_released,t.job_encoder_released,t.job_child_fault,t.job_transport_fault};
   for(unsigned n=0;n<4;n++){p.step(false);observer.finish();enc::require(status==std::array<uint64_t,9>{t.job_done_tag,t.job_done_session,t.job_done_count,t.job_done_reason,t.job_done_eos,t.job_source_released,t.job_encoder_released,t.job_child_fault,t.job_transport_fault},"held full autonomous job status");}
   p.table_conservation();p.finish_observed();enc::require(!t.transfer_live&&!transfer.pending&&!t.physical_pending&&!t.transfer_fault&&!t.physical_protocol_fault&&t.handoff_complete,"whole autonomous transport/producer closure");
   // Check before status ACK/observer removal/reset drain as well as after it:
   // no later fence may conceal a held response, pending bank or transport fault.
   enc::require(t.encoder_bank_idle&&!t.encoder_bank_fault&&!t.encoder_router_fault&&!e.mutable_reply_held&&!transfer.response_held,"pre-status-ACK whole onboard bank/router idle and held-response closure");
   enc::require(e.mutable_requests>0&&e.mutable_requests==e.mutable_replies&&e.mutable_response_packets==e.mutable_requests&&e.mutable_response_checks>=8*e.mutable_response_packets,"pre-status-ACK every onboard mutable request has actual observed reply/all eight lanes checked");
   enc::require(transfer.requests==RV_WORDS&&transfer.replies==RV_WORDS&&transfer.serialized==RV_VALUES&&!transfer.pending,"pre-status-ACK whole actual alias request/reply/serialized coverage");
   t.job_done_ready=1;p.step(false);t.job_done_ready=0;p.observation_hook={};e.clocks=common_clocks;
   // Reenter BOOT: reset real children, drain all provider traffic before new session.
   f.sent=1280;f.input_pending=false;f.clocks=e.clocks;
   for(unsigned i=0;!t.up_start_ready;i++){f.step();enc::require(i<100,"common final reset/drain");}
   enc::require(!t.up_owner_lock&&!t.up_result_valid&&!e.m.active&&!e.h.active&&!e.o.active&&!f.reply.active,"whole post-release group/service quiet");
   enc::require(e.blocked_starts==4&&e.release_refusals==0&&e.releases==1&&e.commits==1,"actual autonomous publication/release counts; old wrong-tag prelude not executed");
   enc::require(t.encoder_bank_idle&&!t.encoder_bank_fault&&!t.encoder_router_fault&&!e.mutable_reply_held&&!transfer.response_held,"whole onboard bank/router idle and held-response closure");
   enc::require(e.mutable_requests>0&&e.mutable_requests==e.mutable_replies&&e.mutable_response_packets==e.mutable_requests&&e.mutable_response_checks>=8*e.mutable_response_packets,"every onboard mutable request has one actual observed reply and all eight lanes checked");
   enc::require(transfer.requests==RV_WORDS&&transfer.replies==RV_WORDS&&transfer.serialized==RV_VALUES&&!transfer.pending,"whole actual alias request/reply/serialized coverage");
   p.check(!p.tables_pending()&&!t.table_fault&&!t.table_owner_live&&!t.table_need_clock,"post-status table ownership/quiet closure");
   p.learned_conservation();f.frontend_conservation();enc::require(f.feature_packets==RV_VALUES&&f.backend_alias_replies==RV_VALUES,"all actual frontend alias packets persisted");
   std::cout<<"ONBOARD_FRONTEND_CONSERVED requests="<<f.backend_requests<<" replies="<<f.backend_replies<<" initialized_reads="<<f.backend_initialized_reads<<" due_writes="<<f.backend_due_writes<<" write_ACKs="<<f.backend_write_ACKs<<" alias_ACKs="<<f.backend_alias_replies<<" serialized_values="<<f.feature_packets<<" idle="<<unsigned(t.frontend_bank_idle)<<" fault="<<unsigned(t.frontend_bank_fault|t.frontend_router_fault)<<" need_clock="<<unsigned(t.frontend_need_clock)<<" host_mutable_response_feeds=0"<<std::endl;
   std::cout<<"ONBOARD_MEMORY_CONSERVED mutable_requests="<<e.mutable_requests<<" mutable_replies="<<e.mutable_replies<<" mutable_response_packets="<<e.mutable_response_packets<<" mutable_response_checks="<<e.mutable_response_checks<<" alias_requests="<<transfer.requests<<" alias_replies="<<transfer.replies<<" alias_serialized_values="<<transfer.serialized<<" bank_idle="<<unsigned(t.encoder_bank_idle)<<" bank_fault="<<unsigned(t.encoder_bank_fault)<<" router_fault="<<unsigned(t.encoder_router_fault)<<std::endl;

   enc::require(t.compact_memory_idle&&!t.compact_response_valid&&!t.history_fault,"actual history final idle/fault/held reply closure");
   enc::require(p.compact.backend_requests==1650&&p.compact.backend_replies==1650&&p.compact.initialized_read_checks==990&&p.compact.initialized_commit_checks==330&&p.compact.published_prefix==5,"additional F64 five-token initialized history coverage; original service checks retained");
   p.producer.backend_conservation();
   p.producer.metadata_conservation();
   p.producer.fixed_book_conservation();
   enc::require(p.producer.backend_fixed_requests==153600&&p.producer.backend_fixed_replies==153600&&p.producer.backend_fixed_row_checks==153600&&p.producer.backend_fixed_byte_checks==49152000,"all F64fiveEOS actual reconstructed fixedrows; original coefficients/checks retained");
   std::cout<<"ONBOARD_SOURCE_KV_BOOK_CONSERVED requests="<<p.producer.backend_fixed_requests<<" replies="<<p.producer.backend_fixed_replies<<" row_checks="<<p.producer.backend_fixed_row_checks<<" byte_checks="<<p.producer.backend_fixed_byte_checks<<" idle="<<unsigned(t.source_fixed_idle)<<" fault="<<unsigned(t.KV_book_fault)<<" need_clock="<<unsigned(t.KV_book_need_clock)<<" host_response_feeds=0"<<std::endl;
   enc::require(p.producer.backend_metadata_requests==4800&&p.producer.backend_metadata_replies==4800&&p.producer.backend_metadata_packet_checks==4800,"all F64 five-token actual immutable ROM packets; original checks retained");
   std::cout<<"ONBOARD_PRODUCER_METADATA_CONSERVED requests="<<p.producer.backend_metadata_requests<<" replies="<<p.producer.backend_metadata_replies<<" actual_packet_checks="<<p.producer.backend_metadata_packet_checks<<" idle="<<unsigned(t.metadata_memory_idle)<<" fault="<<unsigned(t.metadata_ROM_fault)<<" need_clock="<<unsigned(t.metadata_ROM_need_clock)<<" host_response_feeds=0"<<std::endl;
   std::cout<<"ONBOARD_PRODUCER_CONSERVED requests="<<p.producer.backend_requests<<" replies="<<p.producer.backend_replies<<" initialized_reads="<<p.producer.backend_initialized_reads<<" initialized_write_ACKs="<<p.producer.backend_initialized_write_ACKs<<" idle="<<unsigned(t.source_memory_idle)<<" fault="<<unsigned(t.producer_memory_fault)<<std::endl;
   std::cout<<"ONBOARD_HISTORY_CONSERVED requests="<<p.compact.backend_requests<<" replies="<<p.compact.backend_replies<<" initialized_reads="<<p.compact.initialized_read_checks<<" initialized_commit_packets="<<p.compact.initialized_commit_checks<<" published_prefix="<<p.compact.published_prefix<<" idle="<<unsigned(t.compact_memory_idle)<<" fault="<<unsigned(t.history_fault)<<std::endl;
   std::cout<<"CONSERVED frontend_requests="<<f.requests<<" frontend_replies="<<f.replies<<" copier_requests="<<f.copier_requests<<" copier_replies="<<f.copier_replies<<" encoder_requests="<<e.requests<<" encoder_replies="<<e.replies<<" head_requests="<<e.head_requests<<" head_replies="<<e.head_replies<<" O_requests="<<e.O_requests<<" O_replies="<<e.O_replies<<" flags="<<combined_flags<<std::endl;
   std::cout<<"CONTROL_COVERAGE host_token_starts=0 host_winner_feedback=0 host_source_release=0 host_encoder_release=0 history_cap=66 old_wrong_release_test_rerun=0 connected_negative_suite_required=1 host_encoder_mutable_reply_feeds=0 host_encoded_alias_reply_feeds=0"<<std::endl;
   std::cout<<"FOUR_STAGE_GREEDY_FRONTEND_LEARNED_HISTORY_PRODUCER_METADATA_KV_TABLES_ONBOARD_EOS_PASS tokens="<<p.jobs<<" logits="<<p.logitchecks<<" actual_encoded_packets="<<transfer.requests<<" actual_encoded_ACKs="<<actual_source_ACKs<<" host_encoded_feeds=0"<<" frames="<<RV_FRAMES<<" chunks="<<completed_chunks<<" features="<<RV_VALUES<<" encoded_values="<<RV_VALUES<<" encoder_layers="<<e.layer_accepts<<" source_packets="<<e.source_words<<" source_host_feeds=0 common_clocks="<<f.clocks<<" encoder_clocks="<<encoder_end-encoder_begin<<" frontend_checks="<<f.intermediate_checks<<" encoder_write_checks="<<e.checks<<" encoder_read_checks="<<e.read_checks<<std::endl;return 0;
  }
 }
 throw std::runtime_error("common numerical bounded clock limit");
}catch(const std::exception&e){std::cerr<<"FOUR_STAGE_GREEDY_ONBOARD_MEMORY_EOS_FAIL "<<e.what()<<std::endl;return 1;}}
