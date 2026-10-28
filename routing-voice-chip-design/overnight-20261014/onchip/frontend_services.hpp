namespace front {
template<class T>std::vector<T>read(const std::string&p){std::ifstream f(p,std::ios::binary|std::ios::ate);if(!f)throw std::runtime_error(p);size_t n=f.tellg();if(n%sizeof(T))throw std::runtime_error("fixture size");std::vector<T>v(n/sizeof(T));f.seekg(0);f.read((char*)v.data(),n);return v;}
struct Reply{bool active=false,write=false;unsigned region=0,word=0,delay=0,epoch=0;uint32_t tag=0,data=0;unsigned client=0;};
struct Services{
 Top& t;Reply reply;
 std::array<std::vector<uint32_t>,2>w,bias,x,y,flags;
 std::vector<uint32_t>history,features,qflags,lw,lx,ly,lf,q0flags,prior1;std::array<std::vector<uint32_t>,9>memory;
 uint64_t copier_requests=0,copier_replies=0;
 uint64_t clocks=0,requests=0,replies=0,unsolicited=0,writes=0,committed=0,jobs=0,faults=0,resets=0,held=0,intermediate_checks=0;
 std::array<uint64_t,5>write_counts{},read_counts{};std::array<std::array<uint64_t,9>,5>service{};
 std::array<std::string,5>paths;std::vector<uint32_t>committed1,committed2;uint64_t expected_frames=0,copy_reads=0,copy_writes=0,all_copy_reads=0,all_copy_writes=0,blocked_starts=0,history_checks=0;unsigned selected_case=0;
 std::ofstream actual_features;std::ofstream*actual_feature_output=nullptr;uint64_t feature_packets=0;
 std::array<std::vector<uint8_t>,9>frontend_initialized;bool frontend_pending=false,frontend_reply_seen=false;
 std::array<uint32_t,13>frontend_identity{};uint32_t frontend_expected_value=0;
 uint64_t backend_requests=0,backend_replies=0,backend_initialized_reads=0,backend_due_writes=0,backend_write_ACKs=0,backend_alias_replies=0,external_frontend_requests=0,external_frontend_replies=0;
 std::vector<int16_t>pcm;std::vector<uint32_t>quick0,quick1;std::vector<uint32_t>raw;unsigned sent=1280;bool input_pending=false;uint64_t input_offers=0,input_replies=0,prewrite_count=0;
 unsigned mode=0,fault=0;uint32_t tag=0,rng=0x4c934385,aggregate=0;
 bool injected=false,held_r=false,held_d=false,hold_request=false;std::array<uint32_t,5>old_r{};std::array<uint32_t,6>old_d{};
 Services(Top& model,std::string d,std::string chain,std::string linear,std::string joined,std::string pre):t(model),paths{d,chain,linear,joined,pre}{
  load_case(0);committed1.assign(1280,0);committed2.assign(2560,0);
  memory[0]=w[0];memory[1]=bias[0];memory[2].assign(6400,0xdeadbeef);memory[3].assign(5120,0xdeadbeef);memory[4]=w[1];memory[5]=bias[1];memory[6].assign(7680,0xdeadbeef);memory[7].assign(1280,0xdeadbeef);memory[8]=lw;
  for(unsigned r:{2u,3u,6u,7u})frontend_initialized[r].assign(memory[r].size(),0);
  
 }
 void load_case(unsigned cc){
  check(cc<16,"16 real chronological chunks");
  char chunk[32];std::snprintf(chunk,sizeof(chunk),"/chunk-%03u",cc);
  const auto d=paths[0]+chunk;selected_case=cc;aggregate=0;
  raw=read<uint32_t>(d+"/audio_fp32.bin");
  pcm=read<int16_t>(d+"/pcm16.bin");
  lx=read<uint32_t>(d+"/preprocess.bin");
  lw=read<uint32_t>(paths[0]+"/shared/linear_weights.bin");
  ly=read<uint32_t>(d+"/linear.bin");
  quick0=read<uint32_t>(d+"/quick0.bin");
  quick1=read<uint32_t>(d+"/quick1.bin");
  features=read<uint32_t>(d+"/features.bin");
  w[0]=read<uint32_t>(paths[0]+"/shared/conv1_weights.bin");bias[0]=read<uint32_t>(paths[0]+"/shared/conv1_bias.bin");
  w[1]=read<uint32_t>(paths[0]+"/shared/conv2_weights.bin");bias[1]=read<uint32_t>(paths[0]+"/shared/conv2_bias.bin");
  x[0]=read<uint32_t>(d+"/conv1_input.bin");y[0]=read<uint32_t>(d+"/conv1.bin");
  x[1]=read<uint32_t>(d+"/conv2_input.bin");y[1]=read<uint32_t>(d+"/conv2.bin");
  check(raw.size()==1280&&pcm.size()==1280&&lx.size()==1280&&features.size()==1280,"real PCM/frontend input-output shapes");
  check(lw.size()==25600&&ly.size()==5120&&quick0.size()==5120&&quick1.size()==5120,"real linear/activation shapes");
  for(unsigned c=0;c<320;c++)for(unsigned k=0;k<20;k++)if(k>=4)check(x[0].at(c*20+k)==quick0[(k-4)*320+c],"native chronological Conv1 concat");
  for(unsigned c=0;c<640;c++)for(unsigned k=0;k<12;k++)if(k>=4)check(x[1].at(c*12+k)==quick1[c*8+k-4],"native chronological Conv2 concat");
  for(unsigned c=0;c<320;c++)for(unsigned f=0;f<4;f++)check(features[f*320+c]==y[1].at(c*4+f),"native feature transpose identity");
  // Native payload captures provide values, not an IEEE exception-flag oracle.
  // Original suite remains unchanged; this additive speech suite reports flags.
  lf.assign(5120,0);q0flags.assign(5120,0);qflags.assign(5120,0);
  flags[0].assign(5120,0);flags[1].assign(1280,0);
  prior1.resize(1280);history.resize(2560);
  for(unsigned c=0;c<320;c++)for(unsigned k=0;k<4;k++)prior1[c*4+k]=x[0][c*20+k];
  for(unsigned c=0;c<640;c++)for(unsigned k=0;k<4;k++)history[c*4+k]=x[1][c*12+k];
 }
 void check(bool ok,const char*m){if(!ok)throw std::runtime_error(std::string(m)+" fault="+std::to_string(fault)+" history="+std::to_string(t.up_front_debug_history_phase)+" outer="+std::to_string(t.up_front_debug_outer_phase)+" phase="+std::to_string(t.up_front_debug_phase)+" cphase="+std::to_string(t.up_front_debug_chain_phase)+" qphase="+std::to_string(t.up_front_debug_gelu_phase)+" clocks="+std::to_string(clocks));}
 uint32_t random(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
 static bool frontend_region(unsigned r){return r==2||r==3||r==6||r==7;}
 template<class Wide>static uint32_t packet_bits(const Wide&p,unsigned offset,unsigned count){uint32_t value=0;for(unsigned i=0;i<count;i++)if((p[(offset+i)/32]>>((offset+i)%32))&1u)value|=uint32_t(1)<<i;return value;}
 template<class Wide>static std::array<uint32_t,13>packet_identity(const Wide&p){return{packet_bits(p,432,1),packet_bits(p,431,1),packet_bits(p,430,1),packet_bits(p,428,2),packet_bits(p,426,2),packet_bits(p,423,3),packet_bits(p,420,3),packet_bits(p,416,4),packet_bits(p,384,32),packet_bits(p,352,32),packet_bits(p,320,32),packet_bits(p,288,32),packet_bits(p,256,32)};}
 void frontend_capture(const Reply&expected){
  check(!frontend_pending&&expected.active&&frontend_region(expected.region),"one frontend mutable outstanding route");
  auto q=packet_identity(t.frontend_request_packet);check(q[0]==0&&q[1]==1&&q[2]==unsigned(expected.write)&&q[3]==expected.client&&q[4]==0&&q[7]==expected.region&&q[8]==expected.tag&&q[9]==expected.word,"actual frontend request tap versus original captured request");
  check(expected.word<frontend_initialized[expected.region].size(),"full backend observer extent before index");
  if(expected.write)check(packet_bits(t.frontend_request_packet,0,32)==expected.data,"actual mutable write versus original actual request");
  else{check(frontend_initialized[expected.region][expected.word],"actual frontend mutable read only after due write");backend_initialized_reads++;}
  frontend_identity=q;frontend_expected_value=expected.data;frontend_pending=true;frontend_reply_seen=false;backend_requests++;
 }
 bool frontend_response(){
  if(!t.frontend_response_valid)return false;
  check(frontend_pending&&reply.active&&frontend_region(reply.region),"actual frontend bank response has captured route");
  check(packet_identity(t.frontend_response_packet)==frontend_identity,"all thirteen held backend reply fields");
  check(packet_bits(t.frontend_response_packet,0,32)==frontend_expected_value,"actual mutable reply versus comparison-only original provider");
  for(unsigned i=1;i<8;i++)check(packet_bits(t.frontend_response_packet,32*i,32)==0,"known zero scalar reply padding");
  bool first=!frontend_reply_seen;frontend_reply_seen=true;return first&&reply.write;
 }
 void frontend_commit_due(){
  check(frontend_pending&&reply.active&&reply.write&&frontend_region(reply.region),"due backing write observer context");
  frontend_initialized[reply.region][reply.word]=1;backend_due_writes++;
 }
 void frontend_retire(uint32_t actual_value){
  check(frontend_pending&&frontend_reply_seen&&reply.active,"actual frontend matching ACK observer");
  if(reply.write)backend_write_ACKs++;
  if(reply.client==1){
   check(!reply.write&&reply.region==3&&reply.word==feature_packets%1280&&actual_value==features.at(reply.word),"actual copy alias ACK/order/native value");
   check(actual_feature_output!=nullptr,"actual frontend feature output attached");actual_feature_output->write(reinterpret_cast<const char*>(&actual_value),4);check(bool(*actual_feature_output),"actual alias feature serialization");feature_packets++;backend_alias_replies++;
  }
  frontend_pending=false;frontend_reply_seen=false;backend_replies++;
 }
 void frontend_conservation(){
  check(!frontend_pending&&!t.frontend_need_clock&&t.frontend_bank_idle&&!t.frontend_bank_fault&&!t.frontend_router_fault,"whole frontend backend/route quiet");
  check(backend_requests==backend_replies&&backend_requests>0&&backend_requests+external_frontend_requests==requests&&backend_replies+external_frontend_replies==replies,"additional frontend mutable and immutable service conservation");
  check(backend_due_writes==backend_write_ACKs&&backend_write_ACKs==writes&&backend_alias_replies==copier_replies,"actual due writes/ACK and readonly alias conservation");
 }
 void step(){
  auto bits=random();
  if(!t.reset&&!input_pending&&sent<1280&&(!mode||(bits&48))){input_pending=true;t.up_pcm_tag=tag;t.up_pcm_index=sent;t.up_pcm_value=uint16_t(pcm[sent]);input_offers++;}
  t.up_pcm_valid=input_pending;t.up_pcm_producer_idle=!input_pending&&sent==1280;
  const bool backend_reply=reply.active&&frontend_region(reply.region);
  t.step_enable=!mode||(bits&3);t.external_req_ready=(!reply.active||backend_reply)&&!hold_request&&(!mode||(bits&12));
  // Only immutable host replies drive external fields; mutable queue is comparison-only.
  t.external_idle=!reply.active||backend_reply;t.external_rsp_valid=reply.active&&!backend_reply&&!reply.delay;t.external_rsp_tag=backend_reply?0:reply.tag;t.external_rsp_region=backend_reply?0:reply.region;t.external_rsp_word=backend_reply?0:reply.word;t.external_rsp_write=backend_reply?0:reply.write;t.external_rsp_data[0]=backend_reply?0:reply.data;t.external_rsp_client=backend_reply?0:reply.client;t.external_rsp_backing_owner=t.external_rsp_client==1?0:t.external_rsp_client;t.external_rsp_job=0;t.external_rsp_session=0;t.external_rsp_sequence=0;t.external_rsp_scalar=!backend_reply;t.external_rsp_layer=0;t.external_rsp_origin=0;for(unsigned i=1;i<8;i++)t.external_rsp_data[i]=0;
  t.clk=0;t.eval();check(!t.encoder_bank_fault&&!t.encoder_router_fault,"onboard memory faults during frontend/copy");check(!t.frontend_bank_fault&&!t.frontend_router_fault,"actual frontend bank/router faults");if(t.up_pcm_valid)check(t.up_front_converted_value==raw.at(sent),"actual PCM16 converter versus native source bytes");std::array<uint32_t,5>rq{t.up_mem_tag,t.up_mem_region,t.up_mem_word,t.up_mem_write,t.up_mem_data[0]};
  std::array<uint32_t,6>dn{t.up_front_done_tag,t.up_front_done_fault,t.up_front_done_flags,t.up_front_owner_lock,t.up_front_linear_sealed,t.up_front_conv1_input_sealed};
  if(!t.reset){
   if(held_r&&t.up_front_debug_history_phase!=8)check(t.up_mem_valid&&rq==old_r,"held command");
   if(held_d)check(t.up_front_done_valid&&dn==old_d,"held terminal");
   held_r=t.up_mem_valid&&t.up_mem_client==0&&!t.up_mem_ready;held_d=t.up_front_done_valid&&!t.up_front_done_ready;old_r=rq;old_d=dn;held+=held_r+held_d;
  }else{held_r=held_d=false;check(!t.up_mem_valid&&!t.up_front_done_valid&&!t.up_rsp_ready&&!t.up_pcm_ready&&!t.up_front_commit,"reset isolation");}
  bool accepted_input=t.up_pcm_valid&&t.up_pcm_ready;bool req=t.up_mem_valid&&t.up_mem_ready&&t.up_mem_client==0,copyReq=t.up_mem_valid&&t.up_mem_ready&&t.up_mem_client==1,rsp=t.up_rsp_valid&&t.up_rsp_ready;Reply next;
  const bool due_write=frontend_response();const bool backend_ACK=t.frontend_response_valid&&t.frontend_response_ready;const uint32_t actual_backend_value=packet_bits(t.frontend_response_packet,0,32);
  if(backend_ACK)check(rsp&&backend_reply,"actual bank ACK is the original consumer ACK");
  if(req){
   bool hc=t.up_front_debug_history_phase!=7;bool pre=!hc&&t.up_front_debug_outer_phase==2;unsigned ep=hc?6:pre?5:t.up_front_debug_service_phase,region=t.up_mem_region,address=t.up_mem_word;
   check(!reply.active&&t.up_front_owner_lock&&ep<=6&&t.up_mem_tag==(hc?(tag^0xe0000000):pre?tag:(tag^((ep+1)<<29))),"request identity");
   check(region<9&&address<memory[region].size(),"physical allocation extent");
   bool allowed=hc?(region==2||region==6):pre?(t.up_mem_write&&region==7):ep==0?(t.up_mem_write?region==3:(region==7||region==8)):ep==1?(t.up_mem_write?region==2:region==3):ep==2?(t.up_mem_write?region==3:region<3):ep==3?(t.up_mem_write?region==6:region==3):(t.up_mem_write?region==3:(region==4||region==5||region==6));
   check(allowed,"phase physical service");
   next={true,bool(t.up_mem_write),region,address,mode?random()%4:0,ep,t.up_mem_tag,t.up_mem_write?t.up_mem_data[0]:memory[region][address]};if(!pre&&!hc)service[ep][region]++;requests++;
   if(hc){
    unsigned local=t.up_front_debug_copy_index>=1280?t.up_front_debug_copy_index-1280:t.up_front_debug_copy_index;
    bool second=t.up_front_debug_copy_index>=1280;unsigned stride=second?12:20,offset=second?8:16;
    check(region==(second?6:2)&&address==(local/4)*stride+local%4+(t.up_mem_write?0:offset),"actual history coordinate");
    const auto &committed_history=second?committed2:committed1;uint32_t expected=t.up_front_history_location==0?0:committed_history[local];
    check(next.data==expected,"history copy reads actual prior committed generation");
    if(t.up_mem_write){copy_writes++;all_copy_writes++;}else{copy_reads++;all_copy_reads++;}
    check(t.up_front_history_location==0||t.up_front_history_location==2,"history copy ownership");
    if(!injected&&fault==1&&t.up_mem_write&&t.up_front_debug_copy_index==31){next.tag^=1;injected=true;}
   }else{
    check(t.up_front_history_location==1,"compute requires authoritative prefix");
   if(pre)check(address==prewrite_count&&t.up_mem_data[0]==lx[address],"actual preprocess backing mismatch");
   else check(t.up_front_preprocess_sealed&&prewrite_count==1280&&t.up_front_debug_preprocess_writes==1280,"preprocess source seal before dense read");
   if(!pre&&ep>0)check(t.up_front_linear_sealed&&write_counts[0]==5120,"linear producer seal");
   if(!pre&&ep>=2)check(t.up_front_conv1_input_sealed&&write_counts[1]==5120,"Conv1 input producer seal");
   if(!pre&&ep>=3)check(write_counts[2]==5120,"Conv1 producer retirement");
   if(ep==4)check(write_counts[3]==5120,"Conv2 input producer retirement");
   if(t.up_mem_write){
    if(!pre&&ep==0)check(address==write_counts[0]&&t.up_mem_data[0]==ly[address],"actual linear backing mismatch");
    if(ep==1){unsigned i=write_counts[1];check(address==(i%320)*20+4+i/320&&t.up_mem_data[0]==x[0][address],"actual first activation concat mismatch");}
    if(ep==2){unsigned i=write_counts[2],expected=(4*(i/32)+(i%16)/4)*8+4*((i%32)/16)+i%4;check(address==expected&&t.up_mem_data[0]==y[0][address],"actual Conv1 backing mismatch");}
    if(ep==3){unsigned i=write_counts[3];check(address==(i/8)*12+4+i%8&&t.up_mem_data[0]==x[1][address],"actual second activation concat mismatch");}
    if(ep==4){unsigned i=write_counts[4];check(address==(i%4)*320+i/4&&t.up_mem_data[0]==features[address],"actual feature transpose mismatch");}
    intermediate_checks++;
   }else{
    read_counts[ep]++;
    if(ep==0&&region==7)check(next.data==lx[address],"linear read actual preprocessing backing");
    if(ep==1)check(address==write_counts[1]&&next.data==ly[address],"activation read actual linear backing");
    if(ep==2&&region==2)check(next.data==x[0][address],"Conv1 read actual concat backing");
    if(ep==3)check(address==write_counts[3]&&next.data==y[0][address],"activation read actual Conv1 backing");
    if(ep==4&&region==6)check(next.data==x[1][address],"Conv2 read actual concat backing");
   }
   if(!injected&&fault==2&&!pre&&ep==1&&t.up_mem_write&&region==2&&address==16){next.tag^=1;injected=true;}
   if(!injected&&fault==3&&!pre&&ep==2&&!t.up_mem_write&&region==2&&service[2][2]==11*205+6){next.word^=1;injected=true;}
   }

  }
  if(copyReq){
   check(!reply.active&&t.up_mem_scalar&&!t.up_mem_write&&t.up_mem_region==3&&t.up_mem_word<1280,"actualcopy request extent");
   check(t.up_front_features_lock&&!t.up_front_owner_lock&&t.up_chunk_index==selected_case&&t.up_mem_tag==tag,"actualcopy committed feature lease/tag");
   next={true,false,3,t.up_mem_word,mode?random()%4:0,7,t.up_mem_tag,memory[3].at(t.up_mem_word),1};requests++;copier_requests++;
   check(next.data==features.at(t.up_mem_word),"actual featurecopy byte equality");
  }
  const bool backend_accept=t.frontend_request_valid&&t.frontend_request_ready;const bool expected_backend=(req||copyReq)&&frontend_region(next.region);check(backend_accept==expected_backend,"actual backend acceptance equals original consumer request");
  if(backend_accept){next.delay=0;frontend_capture(next);}else if(req||copyReq)external_frontend_requests++;
  // Actual backing writes occur with acknowledgement, even when its metadata
  // was corrupted. The outer transaction must then reject all such writes.
  if(reply.active&&!reply.delay&&reply.write)memory[reply.region][reply.word]=reply.data;
  t.clk=1;t.eval();t.clk=0;t.eval();check(!t.encoder_bank_fault&&!t.encoder_router_fault,"onboard memory faults during frontend/copy");check(!t.frontend_bank_fault&&!t.frontend_router_fault,"actual frontend bank/router faults");clocks++;
  if(due_write)frontend_commit_due();if(backend_ACK)frontend_retire(actual_backend_value);
  if(accepted_input){check(input_pending,"orphan raw input");input_pending=false;sent++;input_replies++;}
  if(rsp){check(reply.active,"orphan reply");if(!backend_reply)external_frontend_replies++;if(reply.write){writes++;if(reply.epoch==5)prewrite_count++;else if(reply.epoch<5)write_counts[reply.epoch]++;}if(reply.client==1)copier_replies++;reply.active=false;replies++;}
  if(reply.active&&reply.delay)reply.delay--;if(req||copyReq)reply=next;
 }

 void authority(){
  check(t.up_front_frame_count==expected_frames,"original input frame counter");
  if(t.up_front_history_location==0)return;
  for(unsigned c=0;c<320;c++)for(unsigned k=0;k<4;k++)check(memory[2][c*20+k+(t.up_front_history_location==2?16:0)]==committed1[c*4+k],"Conv1 authoritative history changed");
  for(unsigned c=0;c<640;c++)for(unsigned k=0;k<4;k++)check(memory[6][c*12+k+(t.up_front_history_location==2?8:0)]==committed2[c*4+k],"Conv2 authoritative history changed");
  history_checks+=3840;
 }
 void check_complete(){
  check(write_counts==std::array<uint64_t,5>{5120,5120,5120,5120,1280}&&t.up_front_debug_input_writes==5120&&t.up_front_debug_feature_writes==1280,"whole write conservation");
  check(service[0]==std::array<uint64_t,9>{0,0,0,5120,0,0,0,102400,409600}&&service[1]==std::array<uint64_t,9>{0,0,5120,5120,0,0,0,0,0}&&service[2]==std::array<uint64_t,9>{2048000,640,1126400,5120,0,0,0,0,0}&&service[3]==std::array<uint64_t,9>{0,0,0,5120,0,0,5120,0,0}&&service[4]==std::array<uint64_t,9>{0,0,0,1280,1024000,320,563200,0,0},"whole service conservation");
  for(unsigned i=0;i<1280;i++)check(memory[3][i]==features[i],"tentative actual features");
  for(unsigned i=0;i<6400;i++)check(memory[2][i]==x[0][i],"actual Conv1 concat and protected prefix");
  for(unsigned i=0;i<7680;i++)check(memory[6][i]==x[1][i],"actual Conv2 concat and protected prefix");
  check(prewrite_count==1280&&memory[7]==lx,"whole native preprocess backing");std::cout<<"REAL_FLAGS "<<unsigned(t.up_front_done_flags)<<std::endl;
 }

};

}
