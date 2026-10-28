// SOURCE PROPOSAL ONLY. Caller is the future copied positive prod::Harness.
// No learned_* service signal is assigned; original learned vector remains comparison only.
uint64_t learned_packet_checks=0,learned_word_checks=0;
void learned_observe(){
 check(mode==0&&fault==0,"onboard learned positive mode0; controls separate");
 check(!t.learned_fault,"actual learned backend fault");
 if(t.learned_offer_count!=loffers){
  check(t.learned_offer_count==loffers+1&&t.learned_valid&&!learned_reply.active,"one actual learned offer ticket");
  check(t.learned_owner_live&&t.learned_tag==tag&&t.learned_layer<6&&t.learned_index<320,"actual learned owner/full coordinate");
  learned_reply={true,unsigned(t.learned_layer),unsigned(t.learned_index),0,uint32_t(t.learned_tag),{}};
  for(unsigned j=0;j<4;j++)learned_reply.value[j]=t.learned_values[j];loffers++;
 }
 check(bool(t.learned_valid)==learned_reply.active,"actual learned PRE ticket valid");
 if(learned_reply.active){
  const auto&r=learned_reply;check(t.learned_tag==r.tag&&t.learned_layer==r.layer&&t.learned_index==r.index,"held44 learned envelope");
  for(unsigned j=0;j<4;j++){check(t.learned_values[j]==r.value[j],"held learned payload");check(t.learned_values[j]==learned.at((r.layer*4+j)*320+r.index),"native learned scale row");}
  if(!t.reset&&t.producer_clock_enable&&t.learned_ready){learned_packet_checks++;learned_word_checks+=4;}
 }
}
void learned_observe_retired(){check(t.learned_ACK_count==lretired,"actual learned ACK ticket after original retire");}
void learned_conservation(){
 check(!t.learned_fault&&!t.learned_owner_live&&!t.learned_need_clock&&t.learned_idle&&!t.learned_valid&&!learned_reply.active,"actual learned final ownership/quiet");
 check(loffers==lretired&&loffers==6*320*jobs&&t.learned_offer_count==loffers&&t.learned_ACK_count==lretired&&learned_packet_checks==lretired&&learned_word_checks==4*lretired,"actual learned row counts per actual completed jobs");
 std::cout<<"ONBOARD_LEARNED_CONSERVED offers="<<loffers<<" ACKs="<<lretired<<" native_rows="<<loffers<<" native_words="<<4*loffers<<" owner=0 idle=1 fault=0 host_response_feeds=0\n";
}
