namespace prod {
#include "taalas_decoder_token_compact_services.hpp"
#include "taalas_adapter_session_compact_token_services_f500_v1.hpp"
template<class T>std::vector<T>read(const std::string&p){std::ifstream f(p,std::ios::binary|std::ios::ate);if(!f)throw std::runtime_error(p);size_t n=f.tellg();if(n%sizeof(T))throw std::runtime_error("fixture size");std::vector<T>v(n/sizeof(T));f.seekg(0);f.read((char*)v.data(),n);if(!f)throw std::runtime_error("fixture read");return v;}
struct Source{bool active=false;unsigned index=0,delay=0;uint32_t tag=0,value=0;};
struct Learned{bool active=false;unsigned layer=0,index=0,delay=0;uint32_t tag=0;std::array<uint32_t,4>value{};};
struct History{bool active=false;unsigned layer=0,pos=0,role=0,channel=0,delay=0;uint32_t tag=0,value=0;};
struct KV{bool active=false;unsigned layer=0,head=0,index=0,delay=0;uint32_t tag=0,value=0;};
struct Reply{bool active=false;unsigned layer=0,role=0,tile=0,region=0,word=0,delay=0;uint32_t tag=0;std::array<uint32_t,8>data{};};
struct Ack{bool active=false;unsigned layer=0,position=0,role=0,channel=0,delay=0;uint32_t tag=0,value=0;};
template<class T>uint32_t bits(const T&v,unsigned off,unsigned width){uint32_t x=0;for(unsigned b=0;b<width;b++){if constexpr(std::is_integral_v<T>)x|=((uint64_t(v)>>(off+b))&1u)<<b;else x|=((v[(off+b)/32]>>((off+b)%32))&1u)<<b;}return x;}
template<class T>void put(T&v,unsigned off,unsigned width,uint32_t x){for(unsigned b=0;b<width;b++){if constexpr(std::is_integral_v<T>){uint64_t m=uint64_t(1)<<(off+b);v=(uint64_t(v)&~m)|(((uint64_t(x)>>b)&1u)<<(off+b));}else{uint32_t m=1u<<((off+b)%32);v[(off+b)/32]=(v[(off+b)/32]&~m)|(((x>>b)&1u)<<((off+b)%32));}}}
struct IndexReply{bool active=false;uint32_t tag=0;unsigned group=0,row=0,delay=0;};
struct EmbedBook{bool active=false;uint32_t tag=0;unsigned page=0,beat=0,delay=0;};
struct HeadBook{unsigned phase=0,page=0,beat=0,delay=0;uint32_t tag=0;};
struct Harness{
 uint32_t real_global_scale=1029015115,real_global_zero=111;bool real_fixture=false;std::string output_directory;
 Top& t;Source src;std::function<void(bool)> transfer_hook;std::function<void()> observation_hook;bool actual_begin_ACK=false,actual_setup_ACK=false,actual_source_ACK=false;
 IndexReply ei,hi;EmbedBook eb;std::array<HeadBook,8>hb{};std::array<unsigned,8>nextpage{};int headgroup=-1;
 std::vector<uint32_t>indices,pages,tokens,winners,logits;unsigned embedded=0,headpackets=0;uint32_t feedback=1,prefix_feedback=2;
 bool ehe=false,hhe=false,ehq=false,hhq=false;std::array<uint32_t,10>eho{},hho{},eqo{},hqo{};
 uint64_t table_index_packets=0,table_index_words=0,table_embedding_packets=0,table_head_packets=0,table_book_words=0;
 uint64_t eireq=0,eirsp=0,ebreq=0,ebbeats=0,hireq=0,hirsp=0,hstarts=0,hbeats=0,hcommits=0,logitchecks=0;Learned learned_reply;KV kv;Reply mem,last_mem,extra_mem;
 #include "learned_observer.hpp"
 SessionServices<Harness> producer{*this};
 CompactServices<Harness> compact{*this};uint32_t session_counter=100;uint64_t extra_replies=0,accepted_starts=0;
 std::vector<uint32_t>learned,inputs,current,selfparams,selfaparam,sm,cm,um,dm;
 std::vector<uint8_t>sw,cw,uw,dw,selfcodes,selfacodes;std::array<std::vector<uint32_t>,12>kvbanks;
 std::map<std::string,std::vector<uint32_t>>value;std::array<std::vector<uint8_t>,4>newcodes;std::array<std::vector<uint32_t>,4>newparams;
 std::array<unsigned,3>branches{},residuals{};std::array<unsigned,4>sources{},ffstores{};std::array<unsigned,6>qcount{},row_reads{},row_writes{},written{},acked{};std::array<unsigned,2>contexts{};std::array<unsigned,8>kvcount{};
 std::array<std::array<unsigned,8>,8>mr{},cr{};
 unsigned token=0,mode=0,fault=0,next=0,hnext=0,ncurrent=0,nquery=0,nfinal=0,received=0,previous_layer=0,committed_terms=0;
 uint32_t tag=0,rng=0x24353ab9;bool injected=false,hold_output=false,held_o=false,held_r=false,held_w=false,held_d=false;
 std::array<uint64_t,7>old_o{},old_r{},old_w{},old_d{};
 uint64_t terminal_preoffers=0,terminal_orphans=0;
 uint64_t& clocks;uint64_t offers=0,retired=0,loffers=0,lretired=0,hoffers=0,hretired=0,koffers=0,kretired=0,requests=0,replies=0,writes=0,acks=0,outputs=0,committed=0,epochs=0,layercommits=0,jobs=0,faults=0,resets=0,holds=0,checks=0,aliaschecks=0,rollbackchecks=0;
 Harness(Top& model,uint64_t& clock,std::string d,std::string sd,std::string cd,std::string fd,std::string hd,std::string pd,bool actual_real=false,std::string out=""):real_fixture(actual_real),output_directory(out),t(model),clocks(clock){
  indices=read<uint32_t>(hd+"/indices.bin");pages=read<uint32_t>(hd+"/pages.bin");tokens=read<uint32_t>(d+"/tokens.bin");winners=read<uint32_t>(d+"/winners.bin");logits=read<uint32_t>(d+"/logits.bin");
  check(indices.size()==1310720&&pages.size()==655360,"immutable table shapes");
  const size_t count=tokens.size();check((real_fixture?count>0&&count<=66:count==2)&&winners.size()==count&&logits.size()==count*32768,"declared token/table shapes");
  if(real_fixture){check(tokens.front()==1,"real first BOS input");for(size_t i=0;i<count;i++){check(tokens[i]<32768&&winners[i]<32768,"real token vocabulary bound");if(i)check(tokens[i]==winners[i-1]&&winners[i-1]!=2,"actual prior winning-token feedback and no early EOS");}}
  inputs=read<uint32_t>(d+"/token-input.bin");learned=read<uint32_t>(d+"/learned.bin");current=read<uint32_t>(d+"/current.bin");
  for(auto n:{"source","self-normalized","self-context","self-output","residual1","cross-normalized","cross-query","cross-context","cross-output","residual2","FF-normalized","FF-up","FF-hidden","FF-output","final-normalized","expected"})value[n]=read<uint32_t>(d+"/"+n+".bin");
  std::array<std::string,4>names={"cross-query","cross-output","FF-up","FF-down"};for(unsigned i=0;i<4;i++){newcodes[i]=read<uint8_t>(d+"/"+names[i]+"-codes.bin");newparams[i]=read<uint32_t>(d+"/"+names[i]+"-parameters.bin");}
  selfparams=read<uint32_t>(d+"/self-parameters.bin");selfaparam=read<uint32_t>(d+"/self-output-parameters.bin");selfcodes=read<uint8_t>(d+"/self-codes.bin");selfacodes=read<uint8_t>(d+"/self-output-codes.bin");
  sw=read<uint8_t>(sd+"/coefficients.bin");sm=read<uint32_t>(sd+"/metadata.bin");cw=read<uint8_t>(cd+"/coefficients.bin");cm=read<uint32_t>(cd+"/metadata.bin");uw=read<uint8_t>(fd+"/up-weights.bin");dw=read<uint8_t>(fd+"/down-weights.bin");um=read<uint32_t>(fd+"/up-metadata.bin");dm=read<uint32_t>(fd+"/down-metadata.bin");
  std::ifstream paths(d+"/KV-paths.txt");std::string p;for(auto&b:kvbanks){check(bool(std::getline(paths,p)),"KV paths");b=read<uint32_t>(p);check(b.size()==RV_VALUES,"KV bank size");}
  check(inputs.size()==count*320&&learned.size()==7680&&current.size()==count*6*960&&sw.size()==2457600&&cw.size()==1228800&&uw.size()==4915200&&dw.size()==2457600,"fixture shapes");
  check(selfparams.size()==count*12&&selfaparam.size()==count*12&&selfcodes.size()==count*1920&&selfacodes.size()==count*1920,"complete self DQL oracle shapes");
  for(unsigned i=0;i<4;i++)check(newparams[i].size()==count*12&&newcodes[i].size()==count*6*(i==3?1280:320),"complete cross/FF DQL oracle shapes");
  for(const auto&x:value)check(x.second.size()==count*6*(x.first=="FF-up"?2560:x.first=="FF-hidden"?1280:320),"value shapes");
  if(real_fixture){std::ifstream policy(pd+"/domain-policy.txt");if(policy){unsigned declared_frames=0;policy>>declared_frames>>real_global_scale>>real_global_zero;check(bool(policy)&&declared_frames==RV_FRAMES&&real_global_zero<=255,"supplied exact real domain policy");std::string extra;check(!(policy>>extra),"no extra domain policy fields");}else check(RV_FRAMES==500,"non-default shape requires explicit domain policy");}producer.load_fixture(pd);
 }
 unsigned layer(){return t.debug_layer;}unsigned position(){return token;}unsigned frames(){return RV_FRAMES;}unsigned index(){return token*6+layer();}
 uint32_t val(std::string name,unsigned i){unsigned size=name=="FF-up"?2560:name=="FF-hidden"?1280:320;return value.at(name).at(index()*size+i);}
 uint32_t rnd(){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
 void check(bool b,const char*m){if(!b)throw std::runtime_error(std::string(m)+" token="+std::to_string(token)+" layer="+std::to_string(layer())+" fault="+std::to_string(fault)+" tokenphase="+std::to_string(t.debug_token_phase)+" childphase="+std::to_string(t.debug_phase)+" clocks="+std::to_string(clocks));}
 void equal(uint32_t got,uint32_t gold,const char*m){check(got==gold,m);checks++;}
 void local_counters(){hnext=ncurrent=nquery=nfinal=0;branches.fill(0);residuals.fill(0);sources.fill(0);ffstores.fill(0);qcount.fill(0);contexts.fill(0);kvcount.fill(0);for(auto&a:mr)a.fill(0);for(auto&a:cr)a.fill(0);}
 void step(bool generate=true){if(transfer_hook)transfer_hook(false);
  generate=generate&&t.debug_join_phase>=1&&t.debug_join_phase<=5;
  if(layer()!=previous_layer){if(!t.reset&&t.debug_join_phase!=6&&t.debug_join_phase!=8&&t.debug_token_phase!=10)check(!kv.active&&!mem.active&&!learned_reply.active,"pending original layer service crossed layer");previous_layer=layer();local_counters();}
  auto r=rnd();t.step_enable=!mode||(r&3);t.req_ready=!mem.active&&!extra_mem.active&&(!mode||(r&12));t.row_transfer_enable=!hold_output&&(!mode||(r&192));
  // Actual learned readout owns offer tickets/payload; host never generates learned replies.
  // K/V is produced by the actual retained-session child; fixtures are observations only.
  // Six learned service fields are actual RTL outputs, observed only.

  const auto& response=extra_mem.active?extra_mem:mem;
  t.rsp_valid=response.active&&!response.delay;t.memory_idle=!mem.active&&!extra_mem.active;t.rsp_tag=response.tag;t.rsp_layer=response.layer;t.rsp_role=response.role;t.rsp_tile=response.tile;t.rsp_region=response.region;t.rsp_word=response.word;for(unsigned i=0;i<8;i++)t.rsp_data[i]=response.data[i];
  producer.drive();compact.drive();table_drive(generate);t.clk=0;t.eval();table_observe();
  actual_begin_ACK=!t.reset&&t.producer_clock_enable&&t.begin_valid&&t.begin_ready;actual_setup_ACK=!t.reset&&t.producer_clock_enable&&t.compact_setup_valid&&t.compact_setup_ready;actual_source_ACK=!t.reset&&t.producer_clock_enable&&t.source_start_valid&&t.source_start_ready;
  if(observation_hook)observation_hook();learned_observe();
  std::array<uint64_t,7>o{t.out_tag,t.out_index,t.out_value,t.out_tentative,0,0,0},rq{t.req_tag,t.req_layer,t.req_role,t.req_tile,t.req_region,t.req_word,0},dn{t.done_tag,t.done_fault,t.owner_lock,t.compact_prepared,t.best_token,t.best_logit,t.is_eos};
  if(!t.reset){
   bool cancel=t.debug_token_phase==10||t.debug_join_phase==8||t.debug_join_phase==6||(fault==10&&injected)||t.token_warm_abort;
   if(held_o&&!cancel)check(t.out_valid&&o==old_o,"held final output");if(held_r&&!cancel)check(t.req_valid&&rq==old_r,"held fixed request");if(held_d&&!cancel)check(t.done_valid&&dn==old_d,"held DONE");held_o=t.out_valid&&!t.out_ready&&t.debug_join_phase==5;held_r=t.req_valid&&!t.req_ready;held_d=t.done_valid&&!t.done_ready;old_o=o;old_r=rq;old_d=dn;holds+=held_o+held_r+held_d;
   if(t.debug_row_read){unsigned i=t.debug_row_index;check(i==row_reads[layer()]&&i<320,"actual layer row read order");equal(t.debug_row_value,val("source",i),"actual interlayer row read-before-overwrite mismatch");row_reads[layer()]++;aliaschecks++;}
   if(t.debug_row_write){unsigned i=t.debug_row_index;check(i==row_writes[layer()]&&i<320&&row_reads[layer()]==320,"next layer overwrite before complete row read");equal(t.debug_row_value,val("expected",i),"actual composed layer output mismatch");row_writes[layer()]++;aliaschecks++;}
   if(t.debug_source_accept){unsigned role=t.debug_source_role,i=t.debug_source_index;check(role<4&&i==sources[role]&&i<320,"actual source order");check(role==0?row_reads[layer()]==320:role==1?residuals[0]==320:role==2?residuals[1]==320:layer()==5&&branches[2]==320,"R read before prior completion");equal(t.debug_source_value,val(role==0?"source":role==1?"residual1":"residual2",i),"actual retained residual source mismatch");equal(t.debug_source_learned,learned.at((layer()*4+role)*320+i),"learned role source");equal(t.debug_source_skip,role==3?val("FF-output",i):0,"final original skip operand");sources[role]++;aliaschecks++;}
   if(t.debug_branch_write){unsigned role=t.debug_branch_role,i=t.debug_branch_index,count=t.debug_branch_mask==3?2:1;check(role<3&&i==branches[role]&&i+count<=320&&t.debug_branch_mask==(role==2?1:3),"branch write order");check(role==0?sources[0]==320:role==1?residuals[0]==320:residuals[1]==320,"branch overwrite before prior residual read");for(unsigned j=0;j<count;j++)equal(uint32_t(t.debug_branch_values>>(32*j)),val(role==0?"self-output":role==1?"cross-output":"FF-output",i+j),"actual branch output mismatch");branches[role]+=count;aliaschecks+=count;}
   if(t.debug_residual_write){unsigned role=t.debug_residual_role,i=t.debug_residual_index;check(role<3&&i==residuals[role]&&i<320&&branches[role]==320&&(role!=2||layer()<5),"residual lifetime/order");equal(t.debug_residual_a,val(role==0?"source":role==1?"residual1":"residual2",i),"actual R read-before-overwrite mismatch");equal(t.debug_residual_b,val(role==0?"self-output":role==1?"cross-output":"FF-output",i),"actual branch read-before-overwrite mismatch");equal(t.debug_residual_value,val(role==0?"residual1":role==1?"residual2":"expected",i),"original residual Add mismatch");residuals[role]++;aliaschecks++;}
   if(t.debug_current_valid){check(ncurrent<960&&t.debug_current_role==ncurrent/320&&t.debug_current_index==ncurrent%320,"actual QKV order");equal(t.debug_current_value,current.at(index()*960+ncurrent),"actual QKV value");ncurrent++;}
   if(t.debug_query_valid){check(nquery<320&&t.debug_query_index==nquery&&residuals[0]==320,"cross query order");equal(t.debug_query_value,val("cross-query",nquery),"cross query value");nquery++;}
   if(t.debug_context_valid){unsigned role=t.debug_context_role,i=t.debug_context_index;check(i==contexts[role]&&i<320,"context order");equal(t.debug_context_value,role?val("cross-context",i):val("self-context",i),"actual attention context");contexts[role]++;}
   if(t.debug_quant_valid){unsigned domain=t.debug_quant_domain,base=t.debug_quant_base,width=domain==5?1280:320;check(domain<6&&base==qcount[domain]*8&&base<width,"original global domain extent");check(domain==0?sources[0]==320:domain==1?contexts[0]==320:domain==2?sources[1]==320:domain==3?contexts[1]==320:domain==4?ffstores[0]==320:ffstores[2]==1280,"global quantizer before whole domain");auto&p=domain<2?(domain?selfaparam:selfparams):newparams[domain-2];unsigned pi=index();equal(t.debug_quant_scale,p.at(pi*2),"global scale");equal(t.debug_quant_zero,p.at(pi*2+1),"global zero");auto&q=domain<2?(domain?selfacodes:selfcodes):newcodes[domain-2];for(unsigned j=0;j<8;j++)equal(uint8_t(t.debug_quant_codes>>(8*j)),q.at(pi*width+base+j),"global original code");qcount[domain]++;}
   if(t.debug_ff_store){unsigned kind=t.debug_ff_store_kind,i=t.debug_ff_store_index,width=kind==1||kind==2?1280:320;check(kind<4&&i==ffstores[kind]&&i<width,"FF stage order");equal(t.debug_ff_store_value,val(kind==0?"FF-normalized":kind==1?"FF-up":kind==2?"FF-hidden":"FF-output",i),"actual FF stage mismatch");ffstores[kind]++;}
   if(t.debug_final_normalized){check(layer()==5&&sources[3]==320&&t.debug_final_index==nfinal&&nfinal<320&&residuals[2]==0,"final fused norm order");equal(t.debug_final_value,val("final-normalized",nfinal),"final fused norm value");nfinal++;}

   if(t.debug_child_commit){
    check(t.debug_token_phase==7&&t.debug_child_terms==position()&&compact.acked[layer()]==11&&compact.written[layer()]==11&&row_reads[layer()]==320&&row_writes[layer()]==320&&ncurrent==960&&nquery==320,"compact layer release before actual whole layer/record");
    for(unsigned d=0;d<6;d++)check(qcount[d]==(d==5?160:40),"six original domains per layer");
    for(unsigned role=0;role<4;role++){unsigned repeats=(role==1||role==2)?1+position():1;check(compact.meta_reads[layer()][role]==80*repeats&&compact.coefficient_reads[layer()][role]==3200*repeats,"actual compact normal plus saved fixed service");}
    for(unsigned role=4;role<6;role++)check(mr[role][0]==80&&cr[role][0]==3200,"original cross service per layer");
    for(unsigned tile=0;tile<8;tile++)check(mr[6][tile]==160&&cr[6][tile]==3200,"FFup tile service");check(mr[7][0]==160&&cr[7][0]==12800,"FFdown service");layercommits++;
   }
   if(t.out_valid&&t.out_ready){check(layer()==5&&received<320&&t.out_tag==tag&&t.out_index==received&&t.out_tentative&&committed_terms==token,"token final output identity");equal(t.out_value,val("expected",received),"six layer final output");if(!output_directory.empty()){std::ofstream actual(output_directory+"/actual-final-rows.bin",std::ios::binary|std::ios::app);uint32_t value=t.out_value;actual.write(reinterpret_cast<const char*>(&value),4);check(bool(actual),"actual final output scalar saved");}received++;outputs++;}
   if(fault==10&&injected&&extra_mem.active&&t.rsp_valid){
    check(t.debug_join_phase==7&&t.done_ready&&t.rsp_ready&&!t.done_valid&&!t.epoch_commit,"same-edge orphan must fence held success and accept real reply");
    terminal_orphans++;
    std::cout<<"TERMINAL_ORPHAN accepted=1 done_valid="<<unsigned(t.done_valid)<<" epoch_commit="<<unsigned(t.epoch_commit)<<" done_ready="<<unsigned(t.done_ready)<<" clocks="<<clocks<<std::endl;
   }
   if(t.epoch_commit){
    check(received==320&&committed_terms==token,"premature compact epoch commit");compact.accept_commit();
    check(t.debug_body_done&&t.debug_head_done&&headpackets==4096,"history publication before vocabulary commit");equal(t.best_token,winners.at(token),"greedy token");equal(t.best_logit,logits.at(token*32768+t.best_token),"greedy score");check(bool(t.is_eos)==(t.best_token==2),"EOS identity");feedback=t.best_token;committed_terms++;epochs++;committed+=320;
    if(!output_directory.empty()){std::ofstream f(output_directory+"/actual-winning-tokens.bin",std::ios::binary|std::ios::app);uint32_t winner=t.best_token;f.write((char*)&winner,4);check(bool(f),"actual winning token publication saved");}
   }
   if(t.epoch_abort)check(committed_terms==token,"aborted compact epoch visible");
  }else{held_o=held_r=held_d=false;check(!t.req_valid&&!t.out_valid&&!t.done_valid&&!t.epoch_commit,"reset output isolation");}
  table_capture();compact.capture();producer.capture();
  bool la=!t.reset&&t.producer_clock_enable&&t.learned_valid&&t.learned_ready,ka=t.kv_valid&&t.kv_ready,ra=t.req_valid&&t.req_ready,ma=t.rsp_valid&&t.rsp_ready,extra=ma&&extra_mem.active;Reply nr;
  if(!t.reset&&t.start_valid&&t.start_ready)accepted_starts++;
  if(ra){check(!mem.active&&t.owner_lock&&t.req_tag==tag&&t.req_layer==layer()&&t.req_role>=4&&t.req_role<8,"fixed ownership");requests++;nr={true,t.req_layer,t.req_role,t.req_tile,t.req_region,t.req_word,mode?rnd()%5:0,t.req_tag,{}};
   unsigned role=nr.role,tile=nr.tile;if(nr.region)mr[role][tile]++;else cr[role][tile]++;
   if(role<6){check(tile==0&&nr.word<(nr.region?80:3200),"unbiased fixed bounds");unsigned bank=role<4?layer()*4+role:layer()*2+role-4;auto&meta=role<4?sm:cm;auto&w=role<4?sw:cw;if(nr.region)for(unsigned j=0;j<8;j++)nr.data[j]=meta.at(bank*640+nr.word*8+j);else std::memcpy(nr.data.data(),w.data()+bank*102400+nr.word*32,32);}
   else{bool down=role==7;check(tile<8&&(!down||tile==0)&&nr.word<(nr.region?160:down?12800:3200),"biased fixed bounds");unsigned rows=down?1280:320,n=down?320:2560;if(nr.region){auto&m=down?dm:um;unsigned off=(layer()*n+tile*320+nr.word*2)*4;for(unsigned j=0;j<8;j++)nr.data[j]=m.at(off+j);}else{auto&w=down?dw:uw;unsigned off=(layer()*rows+nr.word/10)*n+tile*320+(nr.word%10)*32;std::memcpy(nr.data.data(),w.data()+off,32);}}
   if(fault==1&&!injected&&layer()==5&&nr.role==7){nr.layer=4;injected=true;}
  }

  if(transfer_hook)transfer_hook(true);t.clk=1;t.eval();t.clk=0;t.eval();clocks++;
  if(real_fixture&&clocks%1000000==0)std::cout<<"PROGRESS clocks="<<clocks<<" token="<<token<<" layer="<<layer()<<" source_phase="<<unsigned(t.source_phase)<<" token_phase="<<unsigned(t.debug_token_phase)<<std::endl;
  if(la){check(learned_reply.active,"orphan learned");learned_reply.active=false;lretired++;}learned_observe_retired();
  if(ma){if(extra){extra_mem.active=false;extra_replies++;}else{check(mem.active,"orphan original fixed reply");last_mem=mem;last_mem.active=true;mem.active=false;}replies++;}
  table_delays();if(learned_reply.active&&learned_reply.delay)learned_reply.delay--;if(kv.active&&kv.delay)kv.delay--;if(mem.active&&mem.delay)mem.delay--;if(extra_mem.active&&extra_mem.delay)extra_mem.delay--;if(ra)mem=nr;
  compact.retire();producer.retire();
  if(!t.reset&&t.compact_session_valid)check(t.compact_committed_count==committed_terms,"actual compact count publication mismatch");
 }
 bool tables_pending(){if(ei.active||hi.active||eb.active)return true;for(auto b:hb)if(b.phase)return true;return false;}
 void table_drive(bool generate){
  // Original mode0 bookkeeping is reference-only. No table service field is written.
  (void)generate; // Hardware debug/owned state determines actual autonomous offers.
  check(mode==0&&fault==0,"onboard tables positive mode0 only; new actual fault suite separate");
  if(t.table_owner_live&&t.debug_join_phase==5&&t.h_debug_phase==4){
   if(headgroup!=int(t.h_debug_group)){check(!hi.active,"head index crossed group");for(auto b:hb)check(!b.phase,"head book crossed group");if(headgroup>=0)for(auto n:nextpage)check(n==5,"head group page count");headgroup=t.h_debug_group;nextpage.fill(0);}
   for(unsigned i=0;i<8;i++)if(!hb[i].phase&&nextpage[i]<5)hb[i]={1,6540+nextpage[i]*1024+unsigned(headgroup)*8+i,0,0,tag};
  }
 }
 void table_observe(){
  check(!t.table_fault,"actual captured table backend fault");
  const bool enabled=!t.reset&&t.producer_clock_enable,owned=t.table_owner_live;
  check(bool(t.e_index_request_ready)==(enabled&&owned&&!ei.active)&&bool(t.h_index_request_ready)==(enabled&&owned&&!hi.active)&&bool(t.e_book_request_ready)==(enabled&&owned&&!eb.active),"actual table queue/reset/owner READY");
  check(bool(t.e_index_response_valid)==(ei.active&&!ei.delay)&&bool(t.h_index_response_valid)==(hi.active&&!hi.delay)&&bool(t.e_book_response_valid)==eb.active,"actual table PRE N+2/N+1 response order");
  for(unsigned which=0;which<2;which++){
   const auto&b=which?hi:ei;bool valid=which?t.h_index_response_valid:t.e_index_response_valid,ready=which?t.h_index_response_ready:t.e_index_response_ready;
   if(b.active){check((which?t.h_index_response_tag:t.e_index_response_tag)==b.tag&&(which?t.h_index_response_group:t.e_index_response_group)==b.group&&(which?t.h_index_response_row:t.e_index_response_row)==b.row,"actual held141-independent index envelope");}
   if(valid){check(b.active&&b.group<128&&b.row<320,"actual immutable index full bounds");for(unsigned w=0;w<32;w++)equal(which?t.h_index_response_data[w]:t.e_index_response_data[w],indices.at((b.group*320+b.row)*32+w),"actual frozen four-bit index word");if(enabled&&ready){table_index_packets++;table_index_words+=32;}}
  }
  if(eb.active){check(t.e_book_response_tag==eb.tag&&t.e_book_response_page==eb.page&&t.e_book_response_beat==eb.beat,"actual held embedding book envelope");check(eb.page>=6540&&eb.page<11660&&eb.beat<16,"actual embedding book full bounds");for(unsigned w=0;w<8;w++)equal(t.e_book_response_data[w],pages.at(((eb.page-6540)*16+eb.beat)*8+w),"actual embedding UINT8 representative word");if(enabled&&t.e_book_response_ready){table_embedding_packets++;table_book_words+=8;}}
  bool head_pending=false;
  for(unsigned i=0;i<8;i++){
   auto&b=hb[i];unsigned bit=1u<<i;head_pending|=bool(b.phase);
   check(bool(t.h_load_start_valid&bit)==(b.phase==1)&&bool(t.h_load_valid&bit)==(b.phase==2)&&bool(t.h_commit_valid&bit)==(b.phase==3),"actual head mode0 start16beatcommit order");
   if(b.phase){check(t.h_book_job_tag==b.tag&&bits(t.h_load_tags,i*24,24)==b.page&&bits(t.h_load_data_tags,i*24,24)==b.page&&bits(t.h_commit_tags,i*24,24)==b.page,"actual held head book ownership/page");}
   if(b.phase==2){check(b.page>=6540&&b.page<11660&&b.beat<16&&bits(t.h_load_data_beats,i*4,4)==b.beat,"actual head full bounds and beat identity");for(unsigned w=0;w<8;w++)equal(t.h_load_data[i*8+w],pages.at(((b.page-6540)*16+b.beat)*8+w),"actual head UINT8 representative word");if(enabled&&(t.h_load_ready&bit)){table_head_packets++;table_book_words+=8;}}
  }
  check(bool(t.e_producers_idle)==(!ei.active&&!eb.active)&&bool(t.h_producers_idle)==(!hi.active&&!head_pending),"actual table queue quiet conjunction");
 }
 void table_conservation(){
  check(!tables_pending()&&!t.table_fault&&!t.table_owner_live&&!t.table_need_clock&&t.e_producers_idle&&t.h_producers_idle&&!t.e_index_response_valid&&!t.h_index_response_valid&&!t.e_book_response_valid&&!t.h_load_start_valid&&!t.h_load_valid&&!t.h_commit_valid,"actual table final ownership/held reply/quiet closure");
  check(eireq==1600&&eirsp==1600&&hireq==204800&&hirsp==204800&&ebreq==25&&ebbeats==400&&hstarts==25600&&hbeats==409600&&hcommits==25600,"additional F64 fiveEOS immutable table transaction conservation");
  check(table_index_packets==206400&&table_index_words==6604800&&table_embedding_packets==400&&table_head_packets==409600&&table_book_words==3280000,"actual table ACK image checks, never host feeds");
  std::cout<<"ONBOARD_TIED_TABLES_CONSERVED index_requests="<<eireq+hireq<<" index_replies="<<eirsp+hirsp<<" index_packet_checks="<<table_index_packets<<" index_word_checks="<<table_index_words<<" embedding_requests="<<ebreq<<" embedding_beats="<<ebbeats<<" head_starts="<<hstarts<<" head_beats="<<hbeats<<" head_commits="<<hcommits<<" book_word_checks="<<table_book_words<<" idle=1 fault="<<unsigned(t.table_fault)<<" need_clock="<<unsigned(t.table_need_clock)<<" owner="<<unsigned(t.table_owner_live)<<" host_response_feeds=0"<<std::endl;
 }
 void table_capture(){
  if(t.reset){ehe=hhe=ehq=hhq=false;return;}
  if(!t.producer_clock_enable)return; // Backend ACK cannot occur on parked consumer clock.
  std::array<uint32_t,10>eout{t.debug_embedding_index,t.debug_embedding_value},hout{t.h_debug_group,t.h_debug_column},ereq{t.e_index_request_tag,t.e_index_request_group,t.e_index_request_row},hreq{t.h_index_request_tag,t.h_index_request_group,t.h_index_request_row};for(unsigned i=0;i<8;i++)hout[i+2]=t.h_debug_logits[i];
  bool active=t.debug_join_phase>=1&&t.debug_join_phase<=5;
  if(active){if(ehe)check(t.debug_embedding_valid&&eout==eho,"held embedding output");if(hhe)check(t.h_debug_logit_valid&&hout==hho,"held head logits");if(ehq)check(t.e_index_request_valid&&ereq==eqo,"held embedding index request");if(hhq)check(t.h_index_request_valid&&hreq==hqo,"held head index request");}
  ehe=active&&t.debug_embedding_valid&&!t.debug_embedding_accept;hhe=active&&t.h_debug_logit_valid&&!t.h_debug_logit_accept;ehq=active&&t.e_index_request_valid&&!t.e_index_request_ready;hhq=active&&t.h_index_request_valid&&!t.h_index_request_ready;eho=eout;hho=hout;eqo=ereq;hqo=hreq;holds+=ehe+hhe+ehq+hhq;
  if(t.debug_embedding_accept){check(embedded<320&&t.debug_embedding_index==embedded,"actual embedding order");equal(t.debug_embedding_value,inputs.at(token*320+embedded),"actual source embedding");embedded++;}
  if(t.h_debug_logit_accept){check(received==320&&row_writes[5]==320&&committed_terms==token,"head ran before whole tentative body");unsigned group=t.h_debug_group,column=t.h_debug_column;check(group==headpackets/32&&column==headpackets%32,"full vocabulary order");for(unsigned i=0;i<8;i++){unsigned n=(group*8+i)*32+column;equal(t.h_debug_logits[i],logits.at(token*32768+n),"composed full vocabulary logit");logitchecks++;}headpackets++;}
  if(t.e_index_response_valid&&t.e_index_response_ready){check(ei.active,"orphan embedding index");ei.active=false;eirsp++;}
  if(t.h_index_response_valid&&t.h_index_response_ready){check(hi.active,"orphan head index");hi.active=false;hirsp++;}
  if(t.e_book_response_valid&&t.e_book_response_ready){check(eb.active,"orphan embedding book");ebbeats++;if(eb.beat==15)eb.active=false;else{eb.beat++;eb.delay=mode?rnd()%3:0;}}
  if(t.e_index_request_valid&&t.e_index_request_ready){check(!ei.active&&t.e_index_request_tag==tag&&t.e_index_request_group==tokens.at(token)/256&&t.e_index_request_row==embedded,"embedding index request");ei={true,t.e_index_request_tag,t.e_index_request_group,t.e_index_request_row,mode?3+rnd()%4:2};if(fault==4&&!injected&&embedded==7){ei.tag^=1;injected=true;}eireq++;}
  if(t.h_index_request_valid&&t.h_index_request_ready){check(!hi.active&&t.h_index_request_tag==tag&&received==320&&row_writes[5]==320&&committed_terms==token,"head index ownership");hi={true,t.h_index_request_tag,t.h_index_request_group,t.h_index_request_row,mode?3+rnd()%4:2};if(fault==3&&!injected&&hi.group==127){hi.tag^=1;injected=true;}hireq++;}
  if(t.e_book_request_valid&&t.e_book_request_ready){check(!eb.active&&t.e_book_request_tag==tag&&t.e_book_request_page==6540+tokens.at(token)/32+(embedded/64)*1024,"embedding book request");eb={true,t.e_book_request_tag,t.e_book_request_page,0,mode?rnd()%4:0};ebreq++;}
  for(unsigned i=0;i<8;i++){
   auto&b=hb[i];unsigned bit=1u<<i;
   if(t.h_load_start_valid&t.h_load_start_ready&bit){check(b.phase==1,"orphan head book start");b.phase=2;b.delay=mode?rnd()%3:0;hstarts++;}
   if(t.h_load_valid&t.h_load_ready&bit){check(b.phase==2,"orphan head book beat");hbeats++;if(b.beat==15)b.phase=3;else b.beat++;b.delay=mode?rnd()%3:0;}
   if(t.h_commit_valid&t.h_commit_ready&bit){check(b.phase==3,"orphan head book commit");b.phase=0;nextpage[i]++;hcommits++;}
  }
 }
 void table_delays(){if(ei.active&&ei.delay)ei.delay--;if(hi.active&&hi.delay)hi.delay--;if(eb.active&&eb.delay)eb.delay--;for(auto&b:hb)if(b.phase&&b.delay)b.delay--;}
 bool pending(){return learned_reply.active||mem.active||extra_mem.active||tables_pending()||compact.pending()||producer.pending();}
 void drain(bool need_start=true){unsigned n=0;while((need_start?!t.start_ready:t.owner_lock)||pending()){step(false);check(++n<500,"drain timeout");check(!t.done_valid&&!t.out_valid,"cancelled publication");}check(!t.owner_lock,"outer lease release");}
 void setup(){
  t.compact_setup_session=++session_counter;
  const uint32_t image[8]={0x4b35355f,0x978b1858,0x24e03fa6,0xd328f605,0xb31adaea,0xa31e2162,0x5e0eba2f,0x85352d96};
  // MODEL_IMAGE_ID is assigned from the independently pinned RTL literal by
  // the preparation script below; these words are replaced before emission.
  for(unsigned i=0;i<8;i++)t.compact_setup_image_id[i]=image[i];
  t.compact_setup_valid=1;
  for(unsigned n=0;;n++){step(false);if(actual_setup_ACK)break;check(n<500,"compact setup actual enabled-edge ACK bound");}
  t.compact_setup_valid=0;
  check(t.compact_session_valid&&t.compact_session_id==session_counter&&t.compact_setup_fault==0&&t.compact_committed_count==0,"actual compact session setup");drain(false);
 }
 void finish_observed(){
  check(t.job_source_released&&t.job_encoder_released&&producer.source_releases==1,"observed autonomous release completion");producer.conservation();producer.print();compact.conservation();check(loffers==lretired&&koffers==kretired&&requests+extra_replies==replies&&jobs==epochs&&eireq==eirsp&&hireq==hirsp&&ebreq*16==ebbeats&&hstarts*16==hbeats&&hstarts==hcommits,"whole original service conservation");
  std::cout<<"PASS jobs="<<jobs<<" faults="<<faults<<" resets="<<resets<<" starts="<<accepted_starts<<" epochs="<<epochs<<" layer_releases="<<layercommits<<" checks="<<checks<<" logits="<<logitchecks<<" body_requests="<<requests<<" body_replies="<<replies<<" body_extras="<<extra_replies<<" compact_fixed_requests="<<compact.fixed_requests<<" compact_fixed_replies="<<compact.fixed_responses<<" compact_fixed_extras="<<compact.fixed_extras<<" compact_memory_requests="<<compact.memory_requests<<" compact_memory_replies="<<compact.memory_responses<<" compact_memory_extras="<<compact.memory_extras<<" packet_checks="<<compact.packet_value_checks<<" prefix_checks="<<compact.committed_checks<<" fixed_drain_waits="<<compact.fixed_drain_waits<<" memory_drain_waits="<<compact.memory_drain_waits<<" terminal_preoffers="<<terminal_preoffers<<" terminal_orphans="<<terminal_orphans<<" clocks="<<clocks<<std::endl;
 }
};
}
