// Source-only full-token runtime service. No FP32 history fallback exists here.
// All RAM mutations occur on physical write acceptance, before the actual ACK.
// The host must call drive, evaluate combinationally, capture, clock, then retire.
// Cold reset invalidates metadata but retains RAM and both actual pending queues.
#pragma once
#include <array>
#include <cstdint>
#include <cstring>
#include <vector>

template<class Host> struct CompactServices {
 struct Fixed {
  bool active=false; unsigned delay=0,layer=0,role=0,region=0,word=0;
  uint32_t tag=0; std::array<uint32_t,8>data{};
 } fixed, fixed_extra, last_fixed, next_fixed;
 struct Memory {
  bool active=false,write=false,region=false;unsigned delay=0,layer=0,phase=0,position=0,packet=0,word=0,sequence=0;
  uint32_t session=0,attempt=0;std::array<uint32_t,8>data{};
 } memory,memory_extra,last_memory,next_memory;
 Host& h;
 // 6 * 66 * 11 + 6 * 11 real256b packets: 139392+2112 bytes.
 std::vector<uint32_t> committed=std::vector<uint32_t>(4356*8,0xcdcdcdcd),shadow=std::vector<uint32_t>(66*8,0xedededed);
 std::array<unsigned,6>written{},acked{},appended{};
 std::array<std::array<unsigned,4>,6>meta_reads{},coefficient_reads{};
 uint64_t fixed_requests=0,fixed_responses=0,fixed_extras=0,memory_requests=0,memory_responses=0,memory_extras=0;
 uint64_t source_reads=0,shadow_writes=0,shadow_reads=0,append_writes=0,packet_value_checks=0,committed_checks=0;
 uint64_t fixed_drain_waits=0,memory_drain_waits=0,cold_resets=0;
 bool take_fixed=false,take_fixed_extra=false,send_fixed=false;
 bool take_memory=false,take_memory_extra=false,send_memory=false;
 bool injected_fixed=false,injected_memory=false,attempt_bound=false;
 uint32_t expected_session=0,expected_attempt=0;
 struct InitializedCell{bool written=false,acknowledged=false;uint32_t session=0,attempt=0;unsigned position=0;};
 std::array<InitializedCell,4356> committed_initialized{};
 std::array<InitializedCell,66> shadow_initialized{};
 uint32_t publication_session=0;bool publication_session_bound=false;
 unsigned published_prefix=0;
 uint64_t backend_requests=0,backend_replies=0,initialized_read_checks=0,initialized_commit_checks=0;
 uint64_t memory_accept_clock=0;bool backend_response_seen=false;
 void observe_memory(){
  auto&t=h.t;h.check(h.mode==0&&!memory_extra.active,"onboard history nominal mode0 only; no fabricated extra backend reply");
  h.check(!t.history_fault,"actual onboard history storage fault");
  if(t.history_por_reset){h.check(t.reset&&!pending()&&h.committed_terms==0,"initial-only history POR authority");return;}
  h.check(bool(t.compact_memory_idle)==!memory.active,"actual history queue idle versus original observer");
  h.check(bool(t.compact_mem_ready)==(!t.reset&&!memory.active),"selector-independent actual history readiness");
  h.check(bool(t.compact_response_valid)==memory.active,"actual history captured response valid versus original observer");
  if(memory.active){
   h.check(h.clocks>=memory_accept_clock+1,"actual history reply not before N+1 PREedge");
   if(!backend_response_seen){h.check(h.clocks==memory_accept_clock+1,"first actual history reply exactly N+1 PREedge");backend_response_seen=true;}
   const auto&m=memory;
   h.check(t.compact_response_write==m.write&&t.compact_response_region==m.region&&t.compact_response_layer==m.layer&&t.compact_response_phase==m.phase&&t.compact_response_position==m.position&&t.compact_response_packet==m.packet&&t.compact_response_word==m.word&&t.compact_response_session==m.session&&t.compact_response_attempt==m.attempt&&t.compact_response_sequence==m.sequence,"actual history full held response envelope versus captured original request");
   for(unsigned lane=0;lane<8;lane++)h.equal(t.compact_response_data[lane],m.data[lane],"actual history held opaque payload versus comparison-only original mirror");
  }
 }
 void bind_initialized_attempt(){
  const auto&t=h.t;h.check(t.compact_session_valid,"actual compact session before initialized attempt");
  if(!publication_session_bound||publication_session!=t.compact_session_id){
   h.check(h.committed_terms==0,"new session cannot adopt old committed prefix");publication_session=t.compact_session_id;publication_session_bound=true;published_prefix=0;
  }
  h.check(published_prefix==h.committed_terms,"actual initialized publication prefix before attempt");
  shadow_initialized.fill(InitializedCell{});
 }
 void initialized_read(const Memory&m,unsigned address){
  const auto&c=m.region?shadow_initialized.at(address):committed_initialized.at(address);
  h.check(c.written&&c.acknowledged&&c.session==m.session&&c.position==m.position,"actual history read before initialized matching-session write/ACK");
  if(m.region)h.check(c.attempt==m.attempt,"shadow read from another attempt");
  else h.check(publication_session_bound&&publication_session==m.session&&m.position<published_prefix,"committed read from unpublished or previous-session prefix");
  initialized_read_checks++;
 }
 void initialized_ack(const Memory&m){
  unsigned address=m.region?m.layer*11+m.packet:(m.position*6+m.layer)*11+m.packet;
  auto&c=m.region?shadow_initialized.at(address):committed_initialized.at(address);
  h.check(c.written&&!c.acknowledged&&c.session==m.session&&c.attempt==m.attempt&&c.position==m.position,"actual initialized write ACK identity/order");c.acknowledged=true;
 }
 explicit CompactServices(Host& host):h(host){}

 static bool same(const Memory&a,const Memory&b){
  return a.write==b.write&&a.region==b.region&&a.layer==b.layer&&a.phase==b.phase&&a.position==b.position&&a.packet==b.packet&&a.word==b.word&&a.sequence==b.sequence&&a.session==b.session&&a.attempt==b.attempt;
 }
 bool pending()const{return fixed.active||fixed_extra.active||memory.active||memory_extra.active;}
 void begin_attempt(){
  h.check(!pending(),"compact previous physical queue not drained");
  written.fill(0);acked.fill(0);appended.fill(0);
  for(auto&v:meta_reads)v.fill(0);for(auto&v:coefficient_reads)v.fill(0);
  attempt_bound=false;injected_fixed=injected_memory=false;bind_initialized_attempt();
 }
 void cold_reset(){
  // Never restore a checkpoint, clear memory payload or erase queued replies.
  // New session setup remains blocked by truthful idle until these queues drain.
  begin_metadata_only();cold_resets++;
 }
 void begin_metadata_only(){written.fill(0);acked.fill(0);appended.fill(0);attempt_bound=false;}
 void inject_old_fixed(){
  h.check(fixed.active&&!fixed_extra.active&&last_fixed.active,"need retired old and separately pending current compact fixed reply");
  h.check(last_fixed.tag!=fixed.tag,"old fixed counter must differ");
  fixed_extra=last_fixed;fixed_extra.delay=0;fixed.delay=12;injected_fixed=true;
 }
 void inject_old_memory(){
  h.check(memory.active&&!memory_extra.active&&last_memory.active,"need retired old and separately pending current compact memory reply");
  h.check(!same(last_memory,memory),"stale memory header must differ");
  memory_extra=last_memory;memory_extra.delay=0;memory.delay=12;injected_memory=true;
 }
 void drive(){
  auto&t=h.t;
  t.compact_fixed_req_ready=!fixed.active&&!fixed_extra.active&&(!h.mode||h.rnd()%4);
  // Mutable history signals are actual RTL backend outputs (0).
  t.compact_fixed_idle=!fixed.active&&!fixed_extra.active;
  // Mutable history signals are actual RTL backend outputs (1).
  const auto&f=fixed_extra.active?fixed_extra:fixed;
  t.compact_fixed_rsp_valid=f.active&&!f.delay;
  t.compact_fixed_rsp_tag=f.tag;t.compact_fixed_rsp_layer=f.layer;t.compact_fixed_rsp_role=f.role;
  t.compact_fixed_rsp_region=f.region;t.compact_fixed_rsp_word=f.word;
  for(unsigned i=0;i<8;i++)t.compact_fixed_rsp_data[i]=f.data[i];
  // Mutable history signals are actual RTL backend outputs (2).
 }
 uint32_t expected_record_word(unsigned position,unsigned layer,unsigned packet,unsigned word){
  unsigned row=position*6+layer;
  if(packet<10){
   uint32_t v=0;for(unsigned b=0;b<4;b++)v|=uint32_t(h.selfcodes.at(row*320+packet*32+word*4+b))<<(8*b);
   return v;
  }
  if(word==0)return h.selfparams.at(row*2);
  if(word==1)return (position<<8)|h.selfparams.at(row*2+1);
  return 0;
 }
 void capture(){
  auto&t=h.t;observe_memory();
  take_fixed=!t.reset&&t.compact_fixed_rsp_valid&&t.compact_fixed_rsp_ready;
  take_fixed_extra=take_fixed&&fixed_extra.active;
  send_fixed=!t.reset&&t.compact_fixed_req_valid&&t.compact_fixed_req_ready;
  take_memory=!t.reset&&t.producer_clock_enable&&t.compact_response_valid&&t.compact_response_ready;
  take_memory_extra=take_memory&&memory_extra.active;
  send_memory=!t.reset&&t.producer_clock_enable&&t.compact_mem_valid&&t.compact_mem_ready;
  if(t.reset){h.check(!send_fixed&&!send_memory&&!t.epoch_commit,"cold reset request/publication isolation");return;}
  if((h.injected||injected_fixed||injected_memory)&&fixed.active){
   h.check(!t.done_valid&&!t.epoch_commit&&!t.start_ready,"compact fixed pending queue escaped drain");fixed_drain_waits++;
  }
  if((h.injected||injected_fixed||injected_memory)&&memory.active){
   h.check(!t.done_valid&&!t.epoch_commit&&!t.start_ready,"compact memory pending queue escaped drain");memory_drain_waits++;
  }
  if(send_fixed){
   h.check(!fixed.active&&!fixed_extra.active&&t.compact_attempt_lock,"compact fixed ownership");
   next_fixed={true,h.mode?h.rnd()%5:0,t.compact_fixed_req_layer,t.compact_fixed_req_role,t.compact_fixed_req_region,t.compact_fixed_req_word,t.compact_fixed_req_tag,{}};
   auto&f=next_fixed;
   h.check(f.layer<6&&f.role<4&&f.word<(f.region?80:3200),"compact original four-role fixed bounds");
   unsigned bank=f.layer*4+f.role;
   if(f.region){for(unsigned j=0;j<8;j++)f.data[j]=h.sm.at(bank*640+f.word*8+j);meta_reads[f.layer][f.role]++;}
   else{std::memcpy(f.data.data(),h.sw.data()+bank*102400+f.word*32,32);coefficient_reads[f.layer][f.role]++;}
   fixed_requests++;
  }
  if(send_memory){
   h.check(!memory.active&&!memory_extra.active&&t.compact_attempt_lock,"compact mutable ownership");
   next_memory={true,bool(t.compact_mem_write),bool(t.compact_mem_region),h.mode?h.rnd()%5:0,
    t.compact_mem_layer,t.compact_mem_phase,t.compact_mem_position,t.compact_mem_packet,t.compact_mem_word,t.compact_mem_sequence,
    t.compact_mem_session,t.compact_mem_attempt,{}};
   auto&m=next_memory;memory_accept_clock=h.clocks;backend_response_seen=false;backend_requests++;
   h.check(m.layer<6&&m.position<66&&m.packet<11&&m.session==t.compact_session_id,"compact physical coordinates/session");
   if(!attempt_bound){attempt_bound=true;expected_session=m.session;expected_attempt=m.attempt;}
   h.check(m.session==expected_session&&m.attempt==expected_attempt&&m.attempt==t.compact_attempt,"compact captured attempt identity");
   unsigned address=m.region?m.layer*11+m.packet:(m.position*6+m.layer)*11+m.packet;
   h.check(m.word==address,"original compact packet word mapping");
   auto&ram=m.region?shadow:committed;
   if(m.write){
    h.check(m.position==h.token&&m.position==h.committed_terms,"write only unpublished current position");
    h.check((m.region&&m.phase==1)||(!m.region&&m.phase==3),"compact write phase");
    for(unsigned j=0;j<8;j++){
     uint32_t data=t.compact_mem_data[j];
     h.equal(data,expected_record_word(h.token,m.layer,m.packet,j),"actual original full-domain compact record word");packet_value_checks++;
     ram.at(address*8+j)=data; // Physical mutation happens before its ACK.
     m.data[j]=data;
    }
    if(m.region){h.check(m.packet==written[m.layer]&&acked[m.layer]==m.packet,"shadow packet read/ACK before reuse");written[m.layer]++;shadow_writes++;}
    else{h.check(acked[m.layer]==11&&m.packet==appended[m.layer],"append before complete acknowledged record");append_writes++;}
    auto&cell=m.region?shadow_initialized.at(address):committed_initialized.at(address);
    cell={true,false,m.session,m.attempt,m.position};
   }else{
    initialized_read(m,address);
    h.check((m.region&&m.phase==2)||(!m.region&&m.phase==0),"compact read phase");
    if(m.region){h.check(m.position==h.token&&acked[m.layer]==11,"copy before current record acknowledged");shadow_reads++;}
    else{h.check(m.position<h.committed_terms,"reconstruct from unpublished/future compact row");source_reads++;}
    for(unsigned j=0;j<8;j++)m.data[j]=ram.at(address*8+j);
   }
   memory_requests++;
  }
  if(t.compact_layer_release){
   unsigned l=t.debug_layer;
   h.check(l<6&&written[l]==11&&acked[l]==11&&t.compact_record_acks==11,"layer barrier lacks eleven actual shadow ACKs");
  }
  // Only real current responses update host validity counts. Stale extra
  // packets remain separately conserved and never replace the queued current.
  if(take_memory&&!take_memory_extra&&t.compact_session_valid&&memory.session==expected_session&&memory.attempt==expected_attempt&&h.t.compact_attempt_lock){
   if(memory.write)initialized_ack(memory);
   if(memory.write&&memory.region&&memory.phase==1){h.check(memory.packet==acked[memory.layer],"shadow acknowledgment order");acked[memory.layer]++;}
   if(memory.write&&!memory.region&&memory.phase==3){h.check(memory.packet==appended[memory.layer],"append acknowledgment order");appended[memory.layer]++;}
  }
 }
 void retire(){
  if(take_fixed){if(take_fixed_extra){fixed_extra.active=false;fixed_extras++;}else{last_fixed=fixed;last_fixed.active=true;fixed.active=false;}fixed_responses++;}
  if(take_memory)backend_replies++;
  if(take_memory){if(take_memory_extra){memory_extra.active=false;memory_extras++;}else{last_memory=memory;last_memory.active=true;memory.active=false;}memory_responses++;}
  if(fixed.active&&fixed.delay)fixed.delay--;if(fixed_extra.active&&fixed_extra.delay)fixed_extra.delay--;
  if(memory.active&&memory.delay)memory.delay--;if(memory_extra.active&&memory_extra.delay)memory_extra.delay--;
  if(send_fixed)fixed=next_fixed;if(send_memory)memory=next_memory;
 }
 void verify_committed_prefix(unsigned count,const std::vector<uint32_t>& before){
  h.check(before.size()==committed.size(),"compact prefix snapshot size");
  for(unsigned i=0;i<count*6*11*8;i++){h.check(committed[i]==before[i],"warm fault changed published compact prefix");committed_checks++;}
 }
 void accept_commit(){
  auto&t=h.t;
  h.check(t.done_valid&&t.done_ready&&t.done_fault==0&&t.compact_prepared&&!pending(),"compact commit before joint quiet terminal");
  h.check(t.compact_committed_count==h.committed_terms&&h.committed_terms==h.token,"compact count before actual accepted commit");
  h.check(publication_session_bound&&publication_session==t.compact_session_id&&published_prefix==h.committed_terms,"initialized prefix publication ownership");
  for(unsigned l=0;l<6;l++){
   for(unsigned packet=0;packet<11;packet++){const auto&c=committed_initialized.at((h.token*6+l)*11+packet);h.check(c.written&&c.acknowledged&&c.session==publication_session&&c.attempt==expected_attempt&&c.position==h.token,"history publication before all actual initialized append ACKs");initialized_commit_checks++;}
   h.check(written[l]==11&&acked[l]==11&&appended[l]==11,"incomplete compact six-layer append");
   for(unsigned p=0;p<11;p++)for(unsigned w=0;w<8;w++){
    h.equal(committed.at(((h.token*6+l)*11+p)*8+w),expected_record_word(h.token,l,p,w),"published original compact record");committed_checks++;
   }
  }
  published_prefix++;
 }
 void conservation(){
  h.check(backend_requests==memory_requests&&backend_replies==memory_responses&&backend_requests==backend_replies,"additional actual history backend conservation");
  h.check(!pending()&&fixed_requests+fixed_extras==fixed_responses&&memory_requests+memory_extras==memory_responses,"compact real queues and extras conservation");
 }
};
