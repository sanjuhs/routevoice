// Three actual producer backing arrays. Retained K/V fixtures are comparison
// oracles only: no oracle data enters the bridge or token request path.
#pragma once
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

template<class Host> struct SessionServices {
 struct Memory {bool active=false,write=false,role=false;unsigned delay=0,region=0,layer=0,word=0;uint32_t sid=0,gen=0,epoch=0,tag=0;std::array<uint32_t,8>data{};} memory,extra,last_memory,first_K,next_memory;
 struct Fixed {bool active=false,role=false;unsigned delay=0,layer=0,row=0;uint32_t sid=0,gen=0,epoch=0,tag=0;std::array<uint32_t,80>data{};} fixed,next_fixed;
 struct Position {bool active=false;unsigned delay=0,word=0;uint32_t sid=0,gen=0,tag=0;uint64_t data=0;} position,next_position;
 struct Fresh {bool active=false;unsigned word=0;uint32_t tag=0;std::array<uint32_t,8>data{};} fresh;
 Host&h;
 std::vector<uint32_t>bankA=std::vector<uint32_t>((RV_VALUES),0x7fc00001),bankB=std::vector<uint32_t>((RV_VALUES),0x7fc00002),encoded,adapter;
 std::vector<uint8_t>bankCodes=std::vector<uint8_t>((RV_VALUES),0xee),goldCodes,positions;
 std::array<std::array<std::vector<uint8_t>,2>,6>weights,metadata;
 uint32_t scale=0,zero=0,pscale=0,pzero=0,sid=0x40000000;unsigned next_fresh=0;
 bool fresh_enable=false,observed_retirement=false,negative=false,have_first_K=false,stale_drain=false;
 bool take_memory=false,take_extra=false,send_memory=false,take_fixed=false,send_fixed=false,take_position=false,send_position=false,take_fresh=false;
 bool held_mem=false,held_fixed=false,held_position=false,held_packet=false;
 Memory held_m;Fixed held_f;Position held_p;std::array<uint32_t,7>held_scalar{};
 uint64_t backend_requests=0,backend_replies=0,backend_initialized_reads=0,backend_initialized_write_ACKs=0;
 uint64_t backend_metadata_requests=0,backend_metadata_replies=0,backend_metadata_packet_checks=0;
 uint64_t backend_fixed_requests=0,backend_fixed_replies=0,backend_fixed_row_checks=0,backend_fixed_byte_checks=0;
 std::array<std::vector<uint8_t>,3>initialized{std::vector<uint8_t>(RV_WORDS),std::vector<uint8_t>(RV_WORDS),std::vector<uint8_t>(RV_CODEWORDS)};
 std::array<std::vector<uint32_t>,3>initialized_session{std::vector<uint32_t>(RV_WORDS),std::vector<uint32_t>(RV_WORDS),std::vector<uint32_t>(RV_CODEWORDS)},initialized_generation{std::vector<uint32_t>(RV_WORDS),std::vector<uint32_t>(RV_WORDS),std::vector<uint32_t>(RV_CODEWORDS)};
 std::vector<uint32_t>actualA=std::vector<uint32_t>(RV_VALUES),actualB=std::vector<uint32_t>(RV_VALUES);std::vector<uint8_t>actualCodes=std::vector<uint8_t>(RV_VALUES);
 uint64_t requests=0,replies=0,extras=0,fixed_requests=0,fixed_replies=0,position_requests=0,position_replies=0,fresh_offers=0,fresh_retired=0;
 uint64_t setups=0,generations=0,KV_releases=0,source_releases=0,code_reads=0,code_writes=0,encoded_writes=0,adapter_writes=0,KV_writes=0;
 uint64_t packets=0,scalars=0,K_checks=0,V_checks=0,V_negative_differences=0,holds=0,stale_waits=0,late_refusals=0,code_invariance=0;
 explicit SessionServices(Host&host):h(host){}
 template<class T>std::vector<T>load(const std::string&p){std::ifstream f(p,std::ios::binary|std::ios::ate);h.check(bool(f),"producer fixture open");auto n=f.tellg();h.check(n>=0&&n%sizeof(T)==0,"producer fixture width");f.seekg(0);std::vector<T>v(n/sizeof(T));f.read((char*)v.data(),n);h.check(bool(f),"producer fixture read");return v;}
 void load_fixture(const std::string&d){
  std::ifstream list(d+"/paths.txt");std::vector<std::string>paths;std::string line;while(std::getline(list,line))paths.push_back(line);h.check(paths.size()==59,"producer retained paths");
  positions=load<uint8_t>(paths[0]);encoded=load<uint32_t>(paths[1]);adapter=load<uint32_t>(paths[2]);goldCodes=load<uint8_t>(paths[3]);scale=load<uint32_t>(paths[4]).at(0);zero=load<uint8_t>(paths[5]).at(0);
  std::ifstream m(d+"/metadata.txt");m>>pscale>>pzero;h.check(bool(m)&&pscale==1012345286&&pzero==123,"original fixed position parameters");
  if(h.real_fixture)h.check(scale==h.real_global_scale&&zero==h.real_global_zero,"hash-bound actual real full-memory DQL domain");
  else h.check(scale==1028805969&&zero==104,"original case0 global parameters");
  for(unsigned l=0;l<6;l++)for(unsigned r=0;r<2;r++){weights[l][r]=load<uint8_t>(paths[11+l*4+r*2]);metadata[l][r]=load<uint8_t>(paths[12+l*4+r*2]);h.check(weights[l][r].size()==102400&&metadata[l][r].size()==1600,"original full cross matrices");}
  h.check(encoded.size()==(RV_VALUES)&&adapter.size()==(RV_VALUES)&&goldCodes.size()==(RV_VALUES)&&positions.size()==1310720,"original F500 producer dimensions");
 }
 bool pending()const{return memory.active||extra.active||fixed.active||position.active||fresh.active;}
 void cold_reset(){fresh_enable=false;observed_retirement=false;held_mem=held_fixed=held_position=held_packet=false;stale_drain=false;}
 uint32_t expected_KV(unsigned layer,unsigned role,unsigned rowmajor_index){unsigned frame=rowmajor_index/320,hidx=(rowmajor_index%320)/40,ch=rowmajor_index%40;return h.kvbanks.at(layer*2+role).at(hidx*(RV_WORDS)+frame*40+ch);}
 void drive(){
  auto&t=h.t;
  fresh.active=t.source_fresh_valid;if(fresh.active){fresh.tag=t.source_fresh_tag;fresh.word=t.source_fresh_word;for(unsigned j=0;j<8;j++)fresh.data[j]=t.source_fresh_data[j];}
  // Mutable source and immutable region5 metadata are RTL-owned. Read-only observers below.
  // Actual fixedbook source idle/ready/response observedonly; position is now RTL-owned and checked below.
  
  
  
  // Fresh signals are read-only observations from actual RTL transfer.
 }
 void capture(){
  auto&t=h.t;
  take_memory=!t.reset&&t.source_response_valid&&t.source_response_ready;take_extra=take_memory&&extra.active;send_memory=!t.reset&&t.source_mem_valid&&t.source_mem_ready;
  take_fixed=!t.reset&&t.source_fixed_response_valid&&t.source_fixed_response_ready;send_fixed=!t.reset&&t.source_fixed_valid&&t.source_fixed_ready;
  h.check(h.mode==0&&!t.onchip_position_rejected,"W1c position deterministic legal mode");
  h.check(bool(t.source_position_idle)==!position.active,"W1c position idle");
  h.check(bool(t.source_position_ready)==(!t.reset&&!t.producer_por_reset&&!position.active),"W1c position queue ready/reset fencing");
  h.check(bool(t.source_position_response_valid)==(position.active&&!position.delay),"W1c position exact PRE N+3 schedule");
  if(t.source_position_response_valid){
   h.check(t.source_position_response_session==position.sid&&t.source_position_response_generation==position.gen&&t.source_position_response_tag==position.tag&&t.source_position_response_word==position.word,"W1c position held reply identity");
   h.check(t.source_position_response_data==position.data,"W1c position original binary mismatch");
  }
  take_position=!t.reset&&t.source_position_response_valid&&t.source_position_response_ready;send_position=!t.reset&&t.source_position_valid&&t.source_position_ready;
  take_fresh=!t.reset&&t.source_fresh_valid&&t.source_fresh_ready; if(take_fresh){h.check(fresh.tag==sid&&fresh.word==next_fresh&&next_fresh<RV_WORDS,"actual ordered held encoded transfer");for(unsigned j=0;j<8;j++)h.check(fresh.data[j]==encoded.at(next_fresh*8+j),"actual encoded transfer versus retained oracle");next_fresh++;fresh_offers++;}
  if(t.reset){h.check(!send_memory&&!send_fixed&&!send_position&&!t.epoch_commit,"new physical ports fenced on common reset");return;}
  if(send_memory){backend_requests++;}
  if(take_memory&&!take_extra){
   const auto&m=memory;h.check(m.active&&!m.delay&&t.producer_clock_enable,"actual captured mode0 producer queue ACK");
   h.check(t.source_response_session==m.sid&&t.source_response_generation==m.gen&&t.source_response_epoch==m.epoch&&t.source_response_tag==m.tag&&t.source_response_word==m.word&&t.source_response_region==m.region&&t.source_response_layer==m.layer&&bool(t.source_response_role)==m.role&&bool(t.source_response_write)==m.write,"actual full captured producer reply identity");
   for(unsigned j=0;j<8;j++)h.check(t.source_response_data[j]==m.data[j],"actual producer reply payload compared to mirror, never supplied by it");backend_replies++;
   if(m.region<3){
    unsigned limit=m.region==2?RV_CODEWORDS:RV_WORDS;h.check(m.word<limit,"full original producer word bounds before observer indexing");
    if(m.write){
     initialized[m.region][m.word]=1;initialized_session[m.region][m.word]=m.sid;initialized_generation[m.region][m.word]=m.gen;backend_initialized_write_ACKs++;
     if(m.region==2){for(unsigned j=0;j<32;j++)actualCodes[m.word*32+j]=uint8_t(t.source_response_data[j/4]>>(8*(j%4)));}
     else{auto&bank=m.region?actualB:actualA;for(unsigned j=0;j<8;j++)bank[m.word*8+j]=t.source_response_data[j];}
    }else{
     h.check(initialized[m.region][m.word]&&initialized_session[m.region][m.word]==m.sid&&initialized_generation[m.region][m.word]==(m.region==2?0u:m.gen),"actual producer read only after matching write ACK in retained session/generation");backend_initialized_reads++;
    }
   }
  }
  if(send_fixed)backend_fixed_requests++;
  if(take_fixed){
   const auto&f=fixed;h.check(f.active&&f.delay==0&&t.producer_clock_enable,"actual owned nominalPRE N+3 fixedbook rowACK");
   h.check(t.source_fixed_response_session==f.sid&&t.source_fixed_response_generation==f.gen&&t.source_fixed_response_epoch==f.epoch&&t.source_fixed_response_tag==f.tag&&t.source_fixed_response_layer==f.layer&&bool(t.source_fixed_response_role)==f.role&&t.source_fixed_response_row==f.row,"all141 actual captured fixedbook identity bits");
   for(unsigned j=0;j<80;j++)h.check(t.source_fixed_response_data[j]==f.data[j],"all320 actual index/book reconstructed coefficient bytes vs native observer");
   backend_fixed_replies++;backend_fixed_row_checks++;backend_fixed_byte_checks+=320;
  }
  if(t.metadata_response_valid&&t.metadata_response_ready){
   const auto&m=memory;h.check(take_memory&&!take_extra&&m.active&&m.delay==0&&m.region==5&&h.t.producer_clock_enable,"actual owned immutable metadata ACK");
   auto get=[&](unsigned off,unsigned width){uint32_t value=0;for(unsigned b=0;b<width;b++){unsigned k=off+b;value|=((t.metadata_response_packet[k/32]>>(k%32))&1u)<<b;}return value;};
   h.check(get(0,32)==m.word&&get(32,32)==m.tag&&get(64,32)==m.epoch&&get(96,32)==m.gen&&get(128,32)==m.sid&&get(160,1)==m.role&&get(161,3)==m.layer&&get(164,3)==m.region&&get(167,1)==m.write,"all168 captured immutable ROM response identity bits");
   for(unsigned j=0;j<8;j++)h.check(get(168+j*32,32)==m.data[j]&&get(168+j*32,32)==t.source_response_data[j],"all256 actual immutable ROM data bits versus original observer/nexus");
   backend_metadata_replies++;backend_metadata_packet_checks++;
  }
  if(t.metadata_request_valid&&t.metadata_request_ready){
   backend_metadata_requests++;
   h.check(send_memory&&t.source_mem_region==5&&!t.source_mem_write,"only actual admitted region5 immutable host request");
   auto get=[&](unsigned off,unsigned width){uint32_t value=0;for(unsigned b=0;b<width;b++){unsigned k=off+b;value|=((t.metadata_request_packet[k/32]>>(k%32))&1u)<<b;}return value;};
   h.check(get(0,32)==t.source_mem_word&&get(32,32)==t.source_mem_tag&&get(64,32)==t.source_mem_epoch&&get(96,32)==t.source_mem_generation&&get(128,32)==t.source_mem_session&&get(160,1)==t.source_mem_role&&get(161,3)==t.source_mem_layer&&get(164,3)==t.source_mem_region&&get(167,1)==t.source_mem_write,"actual full immutable metadata request identity");
   for(unsigned j=0;j<8;j++)h.check(get(168+j*32,32)==t.source_mem_data[j],"actual immutable metadata request full opaque payload");
  }

  bool cancel=t.token_warm_abort||t.source_owner_phase==9||t.source_owner_phase==10;
  if(held_mem&&!cancel){h.check(t.source_mem_valid&&t.source_mem_session==held_m.sid&&t.source_mem_generation==held_m.gen&&t.source_mem_epoch==held_m.epoch&&t.source_mem_tag==held_m.tag&&t.source_mem_word==held_m.word&&t.source_mem_region==held_m.region&&t.source_mem_layer==held_m.layer&&bool(t.source_mem_role)==held_m.role&&bool(t.source_mem_write)==held_m.write,"held new memory request identity");for(unsigned j=0;j<8;j++)h.check(t.source_mem_data[j]==held_m.data[j],"held new memory request data");}
  if(held_fixed&&!cancel)h.check(t.source_fixed_valid&&t.source_fixed_session==held_f.sid&&t.source_fixed_generation==held_f.gen&&t.source_fixed_epoch==held_f.epoch&&t.source_fixed_tag==held_f.tag&&t.source_fixed_layer==held_f.layer&&bool(t.source_fixed_role)==held_f.role&&t.source_fixed_row==held_f.row,"held new fixed identity");
  if(held_position&&!cancel)h.check(t.source_position_valid&&t.source_position_session==held_p.sid&&t.source_position_generation==held_p.gen&&t.source_position_tag==held_p.tag&&t.source_position_word==held_p.word,"held new position identity");
  std::array<uint32_t,7>s{t.kv_tag,t.kv_layer,t.kv_head,t.kv_index,t.kv_value,t.bridge_generation,t.bridge_epoch};
  if(held_packet&&!cancel)h.check(t.kv_valid&&s==held_scalar,"actual bridge packet held until scalar acceptance");
  held_mem=t.source_mem_valid&&!t.source_mem_ready;held_fixed=t.source_fixed_valid&&!t.source_fixed_ready;held_position=t.source_position_valid&&!t.source_position_ready;held_packet=t.kv_valid&&!t.kv_ready;
  if(held_mem){held_m.sid=t.source_mem_session;held_m.gen=t.source_mem_generation;held_m.epoch=t.source_mem_epoch;held_m.tag=t.source_mem_tag;held_m.word=t.source_mem_word;held_m.region=t.source_mem_region;held_m.layer=t.source_mem_layer;held_m.role=t.source_mem_role;held_m.write=t.source_mem_write;for(unsigned j=0;j<8;j++)held_m.data[j]=t.source_mem_data[j];}
  if(held_fixed){held_f.sid=t.source_fixed_session;held_f.gen=t.source_fixed_generation;held_f.epoch=t.source_fixed_epoch;held_f.tag=t.source_fixed_tag;held_f.layer=t.source_fixed_layer;held_f.role=t.source_fixed_role;held_f.row=t.source_fixed_row;}
  if(held_position){held_p.sid=t.source_position_session;held_p.gen=t.source_position_generation;held_p.tag=t.source_position_tag;held_p.word=t.source_position_word;}
  held_scalar=s;holds+=held_mem+held_fixed+held_position+held_packet;
  if(t.source_session_valid&&!observed_retirement){h.check(bankA==encoded&&bankB==adapter&&bankCodes==goldCodes&&actualA==encoded&&actualB==adapter&&actualCodes==goldCodes&&t.source_global_scale==scale&&t.source_global_zero==zero&&t.source_debug_fresh_ACKs==(RV_WORDS),"actual original full-domain setup before destructive K/V writes");observed_retirement=true;setups++;
   if(!h.output_directory.empty()){auto save=[&](const char*n,const auto&v){std::ofstream f(h.output_directory+"/"+n,std::ios::binary);f.write((const char*)v.data(),v.size()*sizeof(v[0]));h.check(bool(f),"actual producer setup payload saved");};/* encoded file is serialized exclusively from matching actual RTL alias ACKs */save("actual-adapter.bin",actualB);save("actual-codes.bin",actualCodes);}}
  if(stale_drain&&memory.active){h.check(!t.done_valid&&!t.start_ready&&!t.source_start_ready&&!t.epoch_commit&&t.source_memory_pending,"genuine current queue retained after stale extra");stale_waits++;}
  if(t.token_warm_abort){h.check(!t.source_mem_valid&&!t.source_fixed_valid&&!t.source_position_valid&&!t.done_valid&&!t.epoch_commit,"same-edge producer fault request/publication fence");}
  if(h.fault==20&&extra.active&&take_extra){h.check(t.debug_join_phase==7&&t.done_ready&&t.token_warm_abort&&!t.done_valid&&!t.epoch_commit,"same-edge held-success source orphan refusal");h.terminal_orphans++;std::cout<<"SOURCE_TERMINAL_ORPHAN accepted=1 epoch_commit=0 clocks="<<h.clocks<<std::endl;}
  if(t.bridge_accept){
   unsigned l=t.kv_layer,head=t.kv_head,i=t.kv_index,role=i>=(40+RV_WORDS),offset=i-(role?(40+RV_WORDS):40),frame=offset/40,ch=offset%40;
   h.check(l==h.layer()&&head<8&&frame<(RV_FRAMES)&&ch<40&&i==40+h.kvcount[head]++&&t.kv_tag==h.tag&&t.bridge_epoch==h.tag&&t.bridge_generation==t.source_generation&&t.source_codes_lock,"actual producer scalar identity/order");
   uint32_t gold=h.kvbanks.at(l*2+role).at(head*(RV_WORDS)+frame*40+ch);
   if(negative&&role&&t.kv_value!=gold){V_negative_differences++;if(V_negative_differences==1)std::cout<<"NEGATIVE_V_LANE_OBSERVED layer="<<l<<" head="<<head<<" index="<<i<<std::endl;}
   else h.check(t.kv_value==gold,role?"producer V scalar equals original oracle":"producer K scalar equals original oracle");
   if(role)V_checks++;else K_checks++;scalars++;h.koffers++;h.kretired++;
   if((ch%8)==7)packets++;
  }
  if(t.compact_layer_release){h.check(t.bridge_layer_scalars==(RV_FRAMES*640)&&t.bridge_layer_packets==(RV_FRAMES*80)&&t.source_generation>0&&!pending()&&t.source_codes_lock,"actual generation held through complete layer release");h.check(bankCodes==goldCodes&&t.source_global_scale==scale&&t.source_global_zero==zero,"retained original global code domain across layers");code_invariance++;}
  if(t.source_owner_phase==6&&!pending()){h.check(t.source_phase==7,"generation count observes actual held child DONE acceptance");h.check(t.source_debug_K_ACKs==(RV_WORDS)&&t.source_debug_V_ACKs==(RV_WORDS)&&t.source_debug_code_reads==(RV_FRAMES*20)&&t.source_debug_coefficient_reads==(RV_BATCHES*640),"full physical K/V generation before consumer publication");generations++;
   if(!h.output_directory.empty()&&h.token==0){
    unsigned l=h.layer();h.check(l<6&&t.source_generation==l+1,"single-token actual K/V dump layer/generation");
    for(unsigned role=0;role<2;role++){
     const auto&bank=role?actualB:actualA;std::vector<uint32_t>headmajor((RV_VALUES));
     for(unsigned head=0;head<8;head++)for(unsigned frame=0;frame<(RV_FRAMES);frame++)for(unsigned ch=0;ch<40;ch++)
      headmajor[head*(RV_WORDS)+frame*40+ch]=bank[frame*320+head*40+ch];
     std::string name=h.output_directory+"/actual-layer"+std::to_string(l)+(role?"-v_cross.bin":"-k_cross.bin");
     std::ofstream f(name,std::ios::binary);f.write((const char*)headmajor.data(),(RV_VALUES*4));h.check(bool(f),"actual complete K/V bank publication saved");
    }
   }
  }
  if(t.source_owner_phase==8&&t.source_phase==8&&!pending())KV_releases++;
  if(send_memory){
   h.check(!memory.active&&!extra.active&&t.source_owner_lock,"new mutable ownership");next_memory={true,bool(t.source_mem_write),bool(t.source_mem_role),h.mode?2+h.rnd()%5:2,t.source_mem_region,t.source_mem_layer,t.source_mem_word,t.source_mem_session,t.source_mem_generation,t.source_mem_epoch,t.source_mem_tag,{}};
   auto&m=next_memory;h.check(m.sid==sid&&m.gen==t.source_generation&&m.epoch==t.source_token_epoch&&m.layer<6,"captured physical source/generation/token identity");
   if(!m.write&&m.region<3){unsigned limit=m.region==2?RV_CODEWORDS:RV_WORDS;h.check(m.word<limit,"full producer read word bounds before initialized observer index");h.check(initialized[m.region][m.word]&&initialized_session[m.region][m.word]==m.sid&&initialized_generation[m.region][m.word]==(m.region==2?0u:m.gen),"accepted producer read only after actual matching write ACK");}
   if(m.write){
    h.check(m.region<3,"three actual producer banks");
    if(m.region==2){h.check(m.gen==0&&m.word<(RV_CODEWORDS),"original codes written only in source setup");for(unsigned j=0;j<32;j++){uint8_t b=t.source_mem_data[j/4]>>(8*(j%4));h.check(b==goldCodes.at(m.word*32+j),"native full-domain code write");bankCodes.at(m.word*32+j)=b;}code_writes++;}
    else{h.check(m.word<(RV_WORDS),"physical FP32 write bounds");auto&bank=m.region?bankB:bankA;bool filling=t.source_phase==12,adapting=t.source_phase==2;
     h.check(filling?m.gen==0&&m.region==0:adapting?m.gen==0&&m.region==1:observed_retirement&&m.gen>0&&m.region==unsigned(m.role)&&t.source_debug_alias_transferred,"actual encoded/adapter/KV lifetime");
     for(unsigned j=0;j<8;j++){uint32_t v=t.source_mem_data[j],gold=filling?encoded.at(m.word*8+j):adapting?adapter.at(m.word*8+j):expected_KV(m.layer,m.role,m.word*8+j);h.check(v==gold,"actual F500 producer value");bank.at(m.word*8+j)=v;}
     if(filling)encoded_writes++;else if(adapting)adapter_writes++;else KV_writes++;
    }
    for(unsigned j=0;j<8;j++)m.data[j]=t.source_mem_data[j];
   }else if(m.region==5){h.check(m.word<80&&m.gen>0,"fixed metadata service bounds");auto&b=metadata[m.layer][m.role];for(unsigned j=0;j<4;j++){for(unsigned k=0;k<4;k++)m.data[j*2]|=uint32_t(b[(m.word*4+j)*5+k])<<(8*k);m.data[j*2+1]=b[(m.word*4+j)*5+4];}}
   else if(m.region==2){h.check(m.word<(RV_CODEWORDS)&&m.gen>0&&t.source_codes_lock,"retained code packet read");for(unsigned j=0;j<32;j++)m.data[j/4]|=uint32_t(bankCodes[m.word*32+j])<<(8*(j%4));code_reads++;}
   else{h.check(m.region<2&&m.word<(RV_WORDS),"actual K/V read backing");auto&bank=m.region?bankB:bankA;for(unsigned j=0;j<8;j++)m.data[j]=bank.at(m.word*8+j);}
   requests++;
  }
  if(send_fixed){h.check(!fixed.active&&t.source_fixed_layer<6&&t.source_fixed_row<320,"full coefficient row ownership");next_fixed={true,bool(t.source_fixed_role),h.mode?2+h.rnd()%5:2,t.source_fixed_layer,t.source_fixed_row,t.source_fixed_session,t.source_fixed_generation,t.source_fixed_epoch,t.source_fixed_tag,{}};auto&f=next_fixed;h.check(f.sid==sid&&f.gen>0&&f.gen==t.source_generation&&f.epoch==h.tag,"fixed layer/generation/epoch binding");auto&b=weights[f.layer][f.role];for(unsigned j=0;j<320;j++)f.data[j/4]|=uint32_t(b[f.row*320+j])<<(8*(j%4));fixed_requests++;}
  if(send_position){h.check(!position.active&&t.source_position_word<163840&&t.source_position_generation==0,"original position coordinate");next_position={true,h.mode?2+h.rnd()%5:2,t.source_position_word,t.source_position_session,t.source_position_generation,t.source_position_tag,0};auto&p=next_position;for(unsigned j=0;j<8;j++)p.data|=uint64_t(positions.at(p.word*8+j))<<(8*j);position_requests++;}
 }
 void retire(){
  if(take_memory){if(take_extra){extra.active=false;extras++;}else{last_memory=memory;if(memory.gen==1&&memory.region==0&&!memory.write&&memory.word==0&&memory.layer==0&&h.t.source_phase==8){first_K=memory;have_first_K=true;}memory.active=false;}replies++;}
  if(take_fixed){fixed.active=false;fixed_replies++;}if(take_position){position.active=false;position_replies++;}if(take_fresh){fresh.active=false;fresh_retired++;}
  if(memory.active&&memory.delay)memory.delay--;if(extra.active&&extra.delay)extra.delay--;if(fixed.active&&fixed.delay)fixed.delay--;if(position.active&&position.delay)position.delay--;
  if(send_memory)memory=next_memory;if(send_fixed)fixed=next_fixed;if(send_position)position=next_position;
 }
 void inject_terminal(){h.check(!pending()&&last_memory.active,"real retired producer reply for held-success orphan");extra=last_memory;extra.delay=0;h.injected=true;late_refusals++;}
 bool stale_target(){auto&t=h.t;return memory.active&&!memory.write&&memory.region==0&&memory.word==0&&memory.layer==0&&memory.gen==7&&t.source_phase==8;}
 void inject_stale(){
  h.check(stale_target()&&have_first_K&&!extra.active&&first_K.sid==memory.sid&&first_K.gen==1&&first_K.epoch!=memory.epoch&&first_K.tag==memory.tag&&first_K.data==memory.data,"real old layer0 packet has identical bytes but stale generation/epoch");
  extra=first_K;extra.delay=0;memory.delay=16;stale_drain=true;h.injected=true;
 }
 bool epoch_target(){auto&t=h.t;return memory.active&&!memory.write&&memory.region==0&&memory.word==0&&memory.layer==0&&t.source_phase==8;}
 void inject_epoch(){h.check(epoch_target()&&!extra.active,"actual pending response for epoch corruption");extra=memory;extra.epoch^=0x80000000u;extra.delay=0;memory.delay=16;stale_drain=true;h.injected=true;}
 void start_source(){
  auto&t=h.t;h.check(!pending()&&!t.owner_lock,"source fresh command begins physically quiet");sid++;next_fresh=0;fresh_enable=true;observed_retirement=false;have_first_K=false;stale_drain=false;
  t.source_start_tag=sid;t.source_start_position_scale=pscale;t.source_start_position_zero=pzero;t.source_start_position_offset=0;t.source_start_valid=1;
  for(unsigned n=0;;n++){h.step(false);if(h.actual_source_ACK)break;h.check(n<500,"source setup actual enabled-edge ACK bound");}t.source_start_valid=0;
  auto begin=h.clocks;while(!t.source_ready){h.step(false);h.check(!t.source_error_valid&&h.clocks-begin<3000000,"bounded actual source setup");}fresh_enable=false;
  auto requests_before=requests,fixed_before=fixed_requests,positions_before=position_requests,fresh_before=fresh_offers;
  h.check(t.source_ready&&!t.owner_lock&&!pending(),"source-ready edge precedes quiet observation");
  h.step(false);
  h.check(t.source_ready&&requests==requests_before&&fixed_requests==fixed_before&&position_requests==positions_before&&fresh_offers==fresh_before&&!pending(),"one explicit quiet setup observation issues no service");
  h.check(observed_retirement&&bankCodes==goldCodes,"original source is retained before first token");
 }
 void fixed_book_conservation(){
  auto&t=h.t;h.check(!pending()&&t.source_fixed_idle&&!t.source_fixed_response_valid&&!t.KV_book_fault&&!t.KV_book_need_clock,"actual fixedbook final queue/clock/fault closure");
  h.check(backend_fixed_requests==backend_fixed_replies&&backend_fixed_replies==backend_fixed_row_checks&&backend_fixed_byte_checks==backend_fixed_row_checks*320,"actual fixedbook wholebyte conservation");
 }
 void metadata_conservation(){
  auto&t=h.t;h.check(!pending()&&t.metadata_memory_idle&&!t.metadata_response_valid&&!t.metadata_ROM_fault&&!t.metadata_ROM_need_clock,"actual immutable ROM final queue/clock/fault closure");
  h.check(backend_metadata_requests==backend_metadata_replies&&backend_metadata_replies==backend_metadata_packet_checks,"actual immutable metadata original and observed packet conservation");
 }
 void backend_conservation(){
  auto&t=h.t;h.check(!pending()&&t.source_memory_idle&&!t.source_response_valid&&!t.producer_memory_fault&&!t.metadata_response_valid,"onboard producer actual final queue/fault/immutable service closure");
  h.check(backend_requests==requests&&backend_replies==replies&&requests==replies&&extras==0,"onboard producer original and observed request/ACK conservation");
  h.check(backend_initialized_write_ACKs==encoded_writes+adapter_writes+code_writes+KV_writes,"all actual mutable writes ACKed before snapshot/publication");
 }
 void conservation(){h.check(!pending()&&requests+extras==replies&&fixed_requests==fixed_replies&&position_requests==position_replies&&fresh_offers==fresh_retired,"all new source physical queues conserved");std::cout<<"SOURCE_GENERATIONS generations="<<generations<<" KV_releases="<<KV_releases<<std::endl;}
 void print(){std::cout<<"SOURCE_SUMMARY setups="<<setups<<" requests="<<requests<<" replies="<<replies<<" extras="<<extras<<" fixed_requests="<<fixed_requests<<" fixed_replies="<<fixed_replies<<" position_requests="<<position_requests<<" position_replies="<<position_replies<<" fresh_offers="<<fresh_offers<<" fresh_retired="<<fresh_retired<<" encoded_writes="<<encoded_writes<<" adapter_writes="<<adapter_writes<<" code_writes="<<code_writes<<" KV_writes="<<KV_writes<<" code_reads="<<code_reads<<" packets="<<packets<<" scalars="<<scalars<<" K_checks="<<K_checks<<" V_checks="<<V_checks<<" holds="<<holds<<" stale_waits="<<stale_waits<<" late_refusals="<<late_refusals<<" code_invariance="<<code_invariance<<" source_releases="<<source_releases<<std::endl;}
};
