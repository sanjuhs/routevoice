// SOURCE ONLY: observes actual start/DONE/token/release acceptance; never drives them.
struct GreedyObserver {
 prod::Harness& p;Top& t;enc::Services& e;
 uint32_t job,session,source;unsigned publications=0;bool active=false,source_ack=false,encoder_ack=false;
 uint64_t learned_begin_offers=0,learned_begin_ACKs=0;
 uint64_t begin=0,rb=0,cb=0,mb=0,eb=0,lb=0,ei0=0,eb0=0,hi0=0,hs0=0,sr=0,sf=0,sg=0,ss=0,sfresh=0;
 unsigned oldterms=0;bool held=false;std::array<uint64_t,7> held_token{};
 GreedyObserver(prod::Harness&h,enc::Services&ep,uint32_t j):p(h),t(h.t),e(ep),job(j),session(h.session_counter),source(h.producer.sid){}
 void capture(){
  if(t.reset)return;
  // Acceptance is observed on the consumer's active common edge only.
  if(t.start_valid&&t.start_ready){
   p.check(t.producer_clock_enable&&!active,"actual RTL start acceptance while clock enabled");
   const unsigned pos=t.start_position;
   p.check(pos==p.accepted_starts&&pos==publications&&pos==p.committed_terms,"actual RTL position selects next expected row");
   p.check(pos<p.tokens.size(),"unexpected additional actual token: oracle disagreement, never EOS/cap success");
   p.check(t.start_frames==RV_FRAMES&&t.start_token==p.feedback&&t.start_token==p.tokens.at(pos),"actual BOS/winner feedback versus expected input");
   p.token=pos;p.mode=0;p.fault=0;p.embedded=p.headpackets=0;p.headgroup=-1;p.nextpage.fill(0);p.injected=false;p.next=p.received=0;
   p.row_reads.fill(0);p.row_writes.fill(0);p.local_counters();p.compact.begin_attempt();p.previous_layer=0;p.tag=t.start_tag;learned_begin_offers=t.learned_offer_count;learned_begin_ACKs=t.learned_ACK_count;
   begin=p.clocks;rb=p.requests;cb=p.compact.fixed_requests;mb=p.compact.memory_requests;eb=p.epochs;lb=p.layercommits;
   ei0=p.eireq;eb0=p.ebreq;hi0=p.hireq;hs0=p.hstarts;oldterms=p.committed_terms;
   sr=p.producer.requests;sf=p.producer.fixed_requests;sg=p.producer.generations;ss=p.producer.scalars;sfresh=p.producer.fresh_offers;active=true;
  }
  if(t.done_valid&&t.done_ready){
   p.check(t.producer_clock_enable&&active&&t.done_tag==p.tag&&!t.done_fault&&!p.pending()&&t.owner_lock&&p.epochs==eb,"actual decoder DONE acceptance identity/quiet");
   p.check(p.received==320&&p.requests-rb==278400&&p.compact.fixed_requests-cb==78720+39360*p.token&&p.compact.memory_requests-mb==198+66*p.token&&p.layercommits-lb==6&&p.committed_terms==oldterms,"complete actual compact six-layer service");
   for(unsigned l=0;l<6;l++)p.check(p.row_reads[l]==320&&p.row_writes[l]==320&&p.compact.written[l]==11&&p.compact.acked[l]==11&&p.compact.appended[l]==11,"all six original rows and compact records");
   p.check(p.embedded==320&&p.headpackets==4096&&p.eireq-ei0==320&&p.ebreq-eb0==5&&p.hireq-hi0==40960&&p.hstarts-hs0==5120,"complete original embedding and head service");
   p.check(p.producer.requests-sr==6*(RV_FRAMES*180+160)&&p.producer.fixed_requests-sf==6*RV_BATCHES*640&&p.producer.generations-sg==6&&p.producer.scalars-ss==6*RV_FRAMES*640&&p.producer.fresh_offers==sfresh,"six regenerated actual K/V generations and unchanged whole source");
   p.check(t.learned_offer_count-learned_begin_offers==1920&&t.learned_ACK_count-learned_begin_ACKs==1920,"actual whole six-layer scale readout per accepted job");
   p.jobs++;active=false;
   std::cout<<"OBSERVED_TOKEN_DONE position="<<p.token<<" tag="<<p.tag<<" clocks="<<p.clocks-begin<<std::endl;
  }
  std::array<uint64_t,7> token{t.token_job_tag,t.token_session,t.token_decode_tag,t.token_position,t.token_value,t.token_logit,t.token_is_eos};
  if(held)p.check(t.token_valid&&token==held_token,"held RTL winner publication stable");
  held=t.token_valid&&!t.token_ready;held_token=token;
  if(t.token_valid&&t.token_ready){
   p.check(t.producer_clock_enable&&!active&&t.token_job_tag==job&&t.token_session==session&&t.token_position==publications&&t.token_decode_tag==p.tag,"actual winner publication ownership/order");
   p.check(publications<p.winners.size()&&t.token_value==p.winners.at(publications)&&t.token_value==p.feedback&&t.token_logit==p.logits.at(publications*32768+t.token_value)&&bool(t.token_is_eos)==(t.token_value==2),"actual published winning token/full-vocabulary score/EOS");
   p.check(p.committed_terms==publications+1&&t.compact_committed_count==publications+1,"publication after actual history commit");publications++;
  }
  if(t.source_release_accepted){
   p.check(!source_ack&&!active&&t.source_release_tag==source&&!p.pending()&&!t.owner_lock,"matching source release ACK after numerical drain");
   source_ack=true;p.producer.source_releases++;
  }
  if(t.encoder_release_accepted){
   p.check(source_ack&&!encoder_ack&&t.job_source_released&&t.up_release_tag==e.tag&&t.up_result_valid&&t.up_encoder_backing_lease_held&&!t.up_encoder_release_rejected,"actual matching retained encoder release ACK");encoder_ack=true;e.releases++;
  }
 }
 void finish(){
  p.check(t.job_done_valid&&t.job_done_tag==job&&t.job_done_session==session&&t.job_done_eos&&t.job_done_reason==0&&!t.job_recovery_required&&!t.job_child_fault&&!t.job_transport_fault&&!t.job_source_fault&&!t.job_done_abort,"actual complete autonomous job EOS status");
  p.check(source_ack&&encoder_ack&&t.job_source_released&&t.job_encoder_released&&!active&&publications==p.jobs&&p.jobs==p.winners.size()&&p.epochs==p.jobs&&p.layercommits==6*p.jobs&&p.logitchecks==32768*p.jobs&&t.job_done_count==p.jobs,"expected output comparison after actual EOS, never scheduling length");
 }
};
