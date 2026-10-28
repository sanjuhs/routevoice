namespace enc {
using Words=std::vector<uint32_t>;using Packet=std::array<uint32_t,8>;
void require(bool ok,const std::string&why){if(!ok)throw std::runtime_error(why);}
Words read(const std::string&p){std::ifstream f(p,std::ios::binary|std::ios::ate);require(bool(f),p);size_t n=f.tellg();require(n%4==0,"word extent");Words w(n/4);f.seekg(0);f.read((char*)w.data(),n);require(bool(f),"short read "+p);return w;}
float fp(uint32_t x){float f;std::memcpy(&f,&x,4);return f;}uint32_t bits(float f){uint32_t x;std::memcpy(&x,&f,4);return x;}
std::string hash(const Words&w){unsigned char d[CC_SHA256_DIGEST_LENGTH];CC_SHA256(w.data(),w.size()*4,d);std::ostringstream s;for(auto v:d)s<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(v);return s.str();}
struct Gold{std::array<Words,23> image;Words weights;std::array<uint32_t,8>domains{};std::array<std::string,4>hashes;uint32_t residual_flags=0;};
struct Inputs{
 std::array<Gold,6>gold;Words encoded,learned,nflags,lflags;uint32_t final_flags=0;
 using Row=void(*)(const float*,const float*,const float*,float*,uint32_t*,int);
 using Quant=void(*)(const float*,float,uint32_t,uint8_t*,int);
 using Parameters=void(*)(float,float,float*,uint32_t*,uint32_t*);
 Inputs(const std::string&dir){
  std::ifstream in(dir+"/inputs.txt");require(bool(in),"manifest");std::string p;
  auto next=[&](){require(bool(in>>p),"manifest field");return p;};
  for(auto&g:gold){g.weights=read(next());for(unsigned r:{7,15,16,17,18,21,20})g.image[r]=read(next());for(unsigned r:{19,8,9,10,14})g.image[r]=read(next());for(auto&x:g.domains)in>>x;for(auto&x:g.hashes)in>>x;require(bool(in),"domains/hashes");}
  encoded=read(next());learned=read(next());nflags=read(next());lflags=read(next());
  void*rowlib=dlopen(next().c_str(),RTLD_NOW);require(rowlib!=nullptr,"pinned row reference library");
  void*qlib=dlopen(next().c_str(),RTLD_NOW);require(qlib!=nullptr,"pinned quantizer reference library");
  auto row=reinterpret_cast<Row>(dlsym(rowlib,"block"));auto quant=reinterpret_cast<Quant>(dlsym(qlib,"quantize_many"));auto parameters=reinterpret_cast<Parameters>(dlsym(qlib,"parameters"));require(row&&quant&&parameters,"reference symbols");
  require(encoded.size()==(RV_VALUES)&&learned.size()==320&&nflags.size()==(RV_FRAMES)&&lflags.size()==(RV_VALUES),"final shape");for(auto v:nflags)final_flags|=v;for(auto v:lflags)final_flags|=v;
  for(unsigned layer=0;layer<6;layer++){
   auto&g=gold[layer];require(g.weights.size()==102400&&g.image[7].size()==2560&&g.image[15].size()==102400&&g.image[16].size()==5120&&g.image[17].size()==102400&&g.image[18].size()==1280,"fixed extents");
   for(unsigned r:{19,8,10,14})require(g.image[r].size()==(RV_VALUES),"native boundary extent");require(g.image[9].size()==(RV_FRAMES*80)&&g.image[20].size()==320&&g.image[21].size()==320,"codes/learned extent");
   Words zeros(320);for(unsigned stage=0;stage<2;stage++){
    unsigned dest=stage?11:0,code=stage?13:2,dom=stage?4:0;g.image[dest].resize((RV_VALUES));g.image[code].resize((RV_FRAMES*80));uint32_t flags=0;
    for(unsigned r=0;r<(RV_FRAMES);r++)row((const float*)g.image[19].data()+r*320,stage?(const float*)g.image[10].data()+r*320:(const float*)zeros.data(),(const float*)g.image[stage?20:21].data(),(float*)g.image[dest].data()+r*320,&flags,stage?0:1);
    float low=0,high=0;for(auto v:g.image[dest]){low=std::min(low,fp(v));high=std::max(high,fp(v));}float scale;uint32_t zero;parameters(low,high,&scale,&zero,&flags);require(bits(scale)==g.domains[dom]&&zero==g.domains[dom+1],"original global domain reference");
    quant((const float*)g.image[dest].data(),scale,zero,(uint8_t*)g.image[code].data(),(RV_VALUES));require(hash(g.image[dest])==g.hashes[stage*2]&&hash(g.image[code])==g.hashes[stage*2+1],"frozen arithmetic reference hash");
   }
   if(layer<5)require(g.image[14]==gold[layer+1].image[19],"native successive boundary identity");
  }
  std::ifstream sums(dir+"/residuals.txt");require(bool(sums),"native residual manifest");
  std::string library;require(bool(std::getline(sums,library)),"sum library");void*slib=dlopen(library.c_str(),RTLD_NOW);require(slib!=nullptr,"pinned strict-C residual Add library");
  using Sum=void(*)(const float*,const float*,float*,uint32_t*);auto sum=reinterpret_cast<Sum>(dlsym(slib,"sum_row"));require(sum,"sum symbol");
  for(unsigned l=0;l<6;l++){require(bool(std::getline(sums,p)),"native residual file");auto&g=gold[l];g.image[22]=read(p);require(g.image[22].size()==(RV_VALUES),"native residual extent");Words computed((RV_VALUES));
   for(unsigned r=0;r<(RV_FRAMES);r++){uint32_t flags=0;sum((const float*)g.image[19].data()+r*320,(const float*)g.image[10].data()+r*320,(float*)computed.data()+r*320,&flags);g.residual_flags|=flags;}
   require(computed==g.image[22],"source-derived separate Add versus retained native residual");
  }
  dlclose(slib);dlclose(rowlib);dlclose(qlib);
 }
};
struct Pending{
 bool active=false,write=false,applied=false,response_seen=false;unsigned layer=0,origin=0,region=0,logical=0,word=0,role=0,head=0;uint32_t tag=0;uint64_t due=0;
 std::array<uint32_t,80>data{};
};
struct Services{
 Inputs input;Top& t;std::array<std::vector<Packet>,3>expected_bank;Pending m,h,o,saved;
 std::array<std::array<uint64_t,23>,7>reads{},writes{},acks{};
 std::array<uint64_t,7>child_requests{},reload_requests{},hr{},orr{};std::array<unsigned,6>workspace{};
 uint64_t clocks=0,requests=0,replies=0,head_requests=0,head_replies=0,O_requests=0,O_replies=0,checks=0,read_checks=0,holds=0;
 uint64_t mutable_response_checks=0,mutable_response_packets=0,mutable_requests=0,mutable_replies=0;bool mutable_reply_held=false;std::array<uint32_t,14>mutable_reply_packet{};
 uint64_t commits=0,jobs=0,faults=0,resets=0,layer_accepts=0,layer_releases=0,release_refusals=0,blocked_starts=0,starts=0,DONEs=0,releases=0;
 uint64_t source_words=0,orphan_offers=0,orphan_replies=0,orphan_queued=0,initial_retirements=0,context_retirements=0;
 uint32_t tag=0,mseq=1,hseq=1,oseq=1;unsigned fault=0,sent=0;
 bool feeding=false,saved_valid=false,stray=false,stray_offered=false,injected=false,wrong_image=false,slow=false;
 uint64_t stray_due=0;std::array<bool,6>retired_input{},retired_context{};
 std::array<bool,3>held{};std::array<std::array<uint32_t,14>,3>old{};
 bool doneheld=false;std::array<uint32_t,7>olddone{};
 Services(Top& model,const std::string&dir):input(dir),t(model){expected_bank[0].resize((RV_WORDS));expected_bank[1].resize((RV_WORDS));expected_bank[2].resize((RV_CODEWORDS));require(bytes()==(RV_VALUES*9),"exact three comparison-mirror allocations; never mutable response feeders");}
 uint64_t bytes(){uint64_t n=0;for(auto&b:expected_bank)n+=b.size()*sizeof(Packet);return n;}
 void check(bool b,const std::string&s){require(b,s+" outer="+std::to_string(t.up_enc_phase)+" layer="+std::to_string(t.up_enc_layer)+" clock="+std::to_string(clocks));}
 unsigned logical(){
  if(t.up_mem_origin==1)return 14;
  if(t.up_enc_layer==6)return t.up_mem_write?14:t.up_mem_origin==3?22:19;
  auto r=t.up_mem_region;
  if(r==0)return (t.up_encoder_debug_layer_phase==6&&t.up_mem_write)||t.up_encoder_debug_layer_phase==10?22:19;
  if(r==1)return t.up_encoder_debug_layer_phase==4?(t.up_encoder_debug_prefix_phase==4?8:0):(t.up_encoder_debug_FF_phase==4?14:11);
  if(r==2)return t.up_encoder_debug_context_codes_retired?13:t.up_encoder_debug_input_codes_retired?9:2;
  const unsigned lookup[12]={0,0,0,0,7,7,21,20,15,16,17,18};check(r>=4&&r<12,"fixed region range");return lookup[r];
 }
 uint32_t expected(unsigned l,unsigned r,unsigned w,unsigned b){return input.gold.at(l).image.at(r).at(w*8+b);}
 Packet actual(Pending&p){Packet d{};if(p.region<3)d=expected_bank[p.region].at(p.word);else{
   unsigned layer=wrong_image&&p.layer==0&&p.region==6?1:p.layer;
   const auto&v=p.layer==6?input.learned:input.gold.at(layer).image.at(p.logical);
   unsigned base=p.layer<6&&p.region==5?240:0;for(unsigned i=0;i<8;i++)d[i]=v.at((p.word+base)*8+i);
  }return d;
 }
 // expected_bank records accepted writes at original due time for comparison only.
 void drive(){
  check(fault==0&&!slow&&!stray,"positive-only onboard host; original negative suites remain separate");
  if(m.active&&clocks>=m.due&&!m.applied){if(m.write)for(unsigned i=0;i<8;i++)expected_bank.at(m.region).at(m.word)[i]=m.data[i];m.applied=true;}
  t.external_idle=(!m.active||m.region<3)&&!stray;t.external_req_ready=(!m.active||m.region<3)&&(!slow||clocks%5!=2);
  t.external_rsp_valid=m.active&&m.region>=3&&clocks>=m.due;t.external_rsp_layer=m.layer;t.external_rsp_origin=m.origin;t.external_rsp_region=m.region;t.external_rsp_tag=m.tag;t.external_rsp_word=m.word;t.external_rsp_write=m.write;t.external_rsp_client=2;t.external_rsp_backing_owner=t.external_rsp_client==1?0:t.external_rsp_client;t.external_rsp_job=0;t.external_rsp_session=0;t.external_rsp_sequence=0;t.external_rsp_scalar=0;
  if(t.external_rsp_valid){auto data=actual(m);for(unsigned i=0;i<8;i++)t.external_rsp_data[i]=m.write?m.data[i]:data[i];
   if(fault==3&&m.layer==0&&m.region==6&&!m.write){t.external_rsp_layer=1;injected=true;}
  }
  stray_offered=stray&&clocks>=stray_due;
  if(stray_offered){t.external_rsp_valid=1;t.external_rsp_layer=saved.layer;t.external_rsp_origin=saved.origin;t.external_rsp_region=saved.region;t.external_rsp_tag=saved.tag;t.external_rsp_word=saved.word;t.external_rsp_write=saved.write;for(unsigned i=0;i<8;i++)t.external_rsp_data[i]=saved.data[i];}
  t.up_head_fixed_idle=!h.active;t.up_head_fixed_ready=!h.active&&(!slow||clocks%7!=4);t.up_head_response_valid=h.active&&clocks>=h.due;
  t.up_head_response_layer=h.layer;t.up_head_response_tag=h.tag;t.up_head_response_role=h.role;t.up_head_response_head=h.head;t.up_head_response_row=h.word;
  if(t.up_head_response_valid){for(unsigned i=0;i<10;i++)t.up_head_response_data[i]=h.data[i];if(fault==4){t.up_head_response_layer=h.layer^1;injected=true;}}
  t.up_O_fixed_idle=!o.active;t.up_O_fixed_ready=!o.active&&(!slow||clocks%7!=3);t.up_O_response_valid=o.active&&clocks>=o.due;
  t.up_O_response_layer=o.layer;t.up_O_response_tag=o.tag;t.up_O_response_row=o.word;
  if(t.up_O_response_valid){for(unsigned i=0;i<80;i++)t.up_O_response_data[i]=o.data[i];if(fault==5){t.up_O_response_layer=o.layer^1;injected=true;}}
  // Actual source packets come only from bridge RTL SRAM; no host feeder.

 }
 void check_layer(){
  unsigned l=t.up_enc_layer;check(l<6,"layer acceptance range");
  const uint64_t rd[23]={(RV_FRAMES*80),0,(RV_FRAMES*160),0,0,0,0,320,(RV_FRAMES*80),(RV_CODEWORDS),0,(RV_FRAMES*80),0,(RV_FRAMES*20),0,(RV_BATCHES*25600),(RV_BATCHES*1280),(RV_BATCHES*12800),(RV_BATCHES*160),(RV_FRAMES*80),(RV_WORDS),(RV_WORDS),(RV_FRAMES*80)};
  const uint64_t wr[23]={(RV_WORDS),0,(RV_CODEWORDS),0,0,0,0,0,(RV_WORDS),(RV_CODEWORDS),0,(RV_WORDS),0,(RV_CODEWORDS),(RV_WORDS),0,0,0,0,(RV_WORDS),0,0,(RV_WORDS)};
  for(unsigned r=0;r<23;r++)check(reads[l][r]==rd[r]&&writes[l][r]==wr[r]&&acks[l][r]==wr[r],"complete layer logical traffic r="+std::to_string(r));
  uint64_t physical=0;for(unsigned r=0;r<23;r++)physical+=rd[r]+wr[r];check(child_requests[l]==physical&&hr[l]==RV_BATCHES*7680&&orr[l]==RV_BATCHES*320&&reload_requests[l]==(l?RV_WORDS:0),"complete layer physical traffic");
  auto&g=input.gold[l];check(t.up_encoder_context_scale==g.domains[2]&&t.up_encoder_context_zero==g.domains[3]&&t.up_encoder_normal_scale==g.domains[4]&&t.up_encoder_normal_zero==g.domains[5]&&t.up_encoder_hidden_scale==g.domains[6]&&t.up_encoder_hidden_zero==g.domains[7]&&t.up_encoder_residual_flags==g.residual_flags,"exact layer original domains and residual flags");
  check(retired_input[l]&&retired_context[l]&&t.up_encoder_debug_layer_final_ACKs==(RV_WORDS),"actual retirement and final ACK barriers");
  for(unsigned i=0;i<(RV_VALUES);i++){check(expected_bank[1][i/8][i%8]==g.image[14][i],"actual complete layer final expected_bank");check(expected_bank[0][i/8][i%8]==g.image[22][i],"sealed presummed source changed during FF");}
 }
 void tick(){
  t.clk=0;drive();t.eval();
  std::array<bool,3>valid{bool(t.up_mem_valid),bool(t.up_head_fixed_valid),bool(t.up_O_fixed_valid)},ready{bool(t.up_mem_ready),bool(t.up_head_fixed_ready),bool(t.up_O_fixed_ready)};
  std::array<std::array<uint32_t,14>,3>pkt{};pkt[0]={t.up_mem_layer,t.up_mem_origin,t.up_mem_region,t.up_mem_tag,t.up_mem_word,t.up_mem_write};for(unsigned i=0;i<8;i++)pkt[0][i+6]=t.up_mem_data[i];pkt[1]={t.up_head_fixed_layer,t.up_head_fixed_tag,t.up_head_fixed_role,t.up_head_fixed_head,t.up_head_fixed_row};pkt[2]={t.up_O_fixed_layer,t.up_O_fixed_tag,t.up_O_fixed_row};
  if(t.reset){held.fill(false);doneheld=false;check(!valid[0]&&!valid[1]&&!valid[2]&&!t.up_enc_done_valid&&!t.up_encoder_commit&&!t.up_rsp_ready&&!t.up_head_response_ready&&!t.up_O_response_ready,"reset isolation");}
  else for(unsigned i=0;i<3;i++){if(held[i]&&t.up_enc_phase!=9)check(valid[i]&&pkt[i]==old[i],"held command changed");held[i]=valid[i]&&!ready[i];old[i]=pkt[i];holds+=held[i];}
  std::array<uint32_t,7>ds{t.up_enc_done_tag,t.up_enc_done_fault,t.up_enc_done_flags,t.up_encoder_debug_completed_layers,t.up_enc_layer,t.up_encoder_owner_lock,t.up_encoder_backing_lease_held};if(doneheld&&!t.reset)check(t.up_enc_done_valid&&ds==olddone,"held terminal changed");doneheld=t.up_enc_done_valid&&!t.up_enc_done_ready&&!t.reset;olddone=ds;holds+=doneheld;
  check(!t.encoder_bank_fault&&!t.encoder_router_fault,"onboard bank/router fault");
  if(m.active&&m.region<3&&t.up_rsp_valid){
   check(clocks>=m.due,"onboard mutable reply before qualified N+6 edge");
   if(!m.response_seen){check(clocks==m.due,"onboard first mutable reply exactly N+6 PREedge");m.response_seen=true;mutable_response_packets++;}
   check(t.up_rsp_layer==m.layer&&t.up_rsp_origin==m.origin&&t.up_rsp_region==m.region&&t.up_rsp_tag==m.tag&&t.up_rsp_word==m.word&&bool(t.up_rsp_write)==m.write,"actual mutable response identity");
   auto expected_payload=actual(m);
   for(unsigned lane=0;lane<8;lane++){check(t.up_rsp_data[lane]==(m.write?m.data[lane]:expected_payload[lane]),"actual RTL mutable reply versus independent accepted-write mirror");mutable_response_checks++;}
   std::array<uint32_t,14> held_packet{t.up_rsp_layer,t.up_rsp_origin,t.up_rsp_region,t.up_rsp_tag,t.up_rsp_word,t.up_rsp_write};
   for(unsigned lane=0;lane<8;lane++)held_packet[6+lane]=t.up_rsp_data[lane];
   if(mutable_reply_held)check(held_packet==mutable_reply_packet,"actual onboard held reply payload/identity stable");
   mutable_reply_held=!t.up_rsp_ready;mutable_reply_packet=held_packet;
  }else check(!mutable_reply_held||t.reset,"held actual onboard reply withdrawn");
  bool rsp=t.up_rsp_valid&&t.up_rsp_ready,hs=t.up_head_response_valid&&t.up_head_response_ready,os=t.up_O_response_valid&&t.up_O_response_ready;
  bool stray_consumed=rsp&&stray_offered;
  if(stray_consumed){check(fault==6&&m.active&&m.layer==1&&m.region==0&&m.word==0&&m.write&&clocks<m.due,"old ACK must not replace queued genuine request");stray=false;orphan_replies++;std::cout<<"ORPHAN_REJECT old_layer="<<saved.layer<<" old_tag="<<saved.tag<<" genuine_layer="<<m.layer<<" genuine_tag="<<m.tag<<" genuine_pending=1"<<std::endl;}
  else if(rsp){check(m.active,"orphan memory reply");bool match=t.up_rsp_layer==m.layer&&t.up_rsp_origin==m.origin&&t.up_rsp_region==m.region&&t.up_rsp_tag==m.tag&&t.up_rsp_word==m.word&&t.up_rsp_write==m.write;
   if(match&&m.write)acks[m.layer][m.logical]++;
   if(match&&m.layer==0&&m.region==0&&m.word==0&&m.write&&m.logical==19&&!saved_valid){saved=m;saved_valid=true;}
   if(m.region<3)mutable_replies++;m.active=false;replies++;
  }
  if(hs){check(h.active,"orphan head response");h.active=false;head_replies++;}if(os){check(o.active,"orphan O response");o.active=false;O_replies++;}
  if(t.up_mem_valid&&t.up_mem_ready){
   check(!m.active&&t.up_encoder_owner_lock&&t.up_mem_layer<7&&t.up_mem_layer==t.up_enc_layer&&t.up_mem_tag==mseq++,"mutable owner/sequence/layer");
   m=Pending{};m.active=true;m.layer=t.up_mem_layer;m.origin=t.up_mem_origin;m.region=t.up_mem_region;m.word=t.up_mem_word;m.tag=t.up_mem_tag;m.write=t.up_mem_write;m.logical=logical();m.due=clocks+6+(slow?clocks%4:0);requests++;if(m.region<3)mutable_requests++;
   unsigned sizes[13]={(RV_WORDS),(RV_WORDS),(RV_CODEWORDS),0,240,80,40,40,12800,640,12800,160,40};check(m.region<13&&m.word<sizes[m.region],"physical region/extent");
   check(!m.write||m.region<3,"immutable source write");for(unsigned i=0;i<8;i++)m.data[i]=t.up_mem_data[i];
   if(m.layer<6){
    if(m.origin==1){check(m.layer>0&&!m.write&&m.region==1&&m.word==reload_requests[m.layer]&&layer_releases>=m.layer,"actual predecessor reload order/release");reload_requests[m.layer]++;
     for(unsigned b=0;b<8;b++){check(expected_bank[1][m.word][b]==expected(m.layer-1,14,m.word,b)&&expected_bank[1][m.word][b]==expected(m.layer,19,m.word,b),"actual predecessor is only successor source");read_checks++;}
    }else{
     check(m.origin==0,"wrong layer origin");child_requests[m.layer]++;
     if(m.region==1){unsigned next=m.logical==0?0:m.logical==8?1:m.logical==11?2:3;check(next>=workspace[m.layer]&&next<=workspace[m.layer]+1,"workspace lifetime regression");
      if(next==0&&m.write)check(acks[m.layer][19]==(RV_WORDS)&&(m.layer==0||reload_requests[m.layer]==(RV_WORDS)),"work overwrite before complete reload/fresh ACKs");
      if(next==1)check(acks[m.layer][0]==(RV_WORDS)&&acks[m.layer][2]==(RV_CODEWORDS),"context before complete normalization");
      if(next==2)check(acks[m.layer][22]==(RV_WORDS)&&acks[m.layer][9]==(RV_CODEWORDS),"FF norm before residual/context seal");
      if(next==3)check(acks[m.layer][11]==(RV_WORDS)&&acks[m.layer][13]==(RV_CODEWORDS),"final before FF global seal");workspace[m.layer]=next;
     }
     if(m.region==2){check((m.logical==2&&!t.up_encoder_debug_input_codes_retired&&!t.up_encoder_debug_context_codes_retired)||(m.logical==9&&t.up_encoder_debug_input_codes_retired&&!t.up_encoder_debug_context_codes_retired)||(m.logical==13&&t.up_encoder_debug_context_codes_retired),"shared code ownership");
      if(m.logical==9&&m.write)check(retired_input[m.layer]&&reads[m.layer][2]==(RV_FRAMES*160)&&acks[m.layer][8]==(RV_WORDS)&&!h.active,"code overwrite before actual heads/drain");
      if(m.logical==13)check(retired_context[m.layer]&&reads[m.layer][9]==(RV_CODEWORDS)&&acks[m.layer][22]==(RV_WORDS)&&!o.active,"FF codes before consumer release");
     }
     if(m.write){writes[m.layer][m.logical]++;for(unsigned i=0;i<8;i++){check(m.data[i]==expected(m.layer,m.logical,m.word,i),"numeric logical="+std::to_string(m.logical)+" word="+std::to_string(m.word)+" lane="+std::to_string(i));checks++;}}
     else{reads[m.layer][m.logical]++;if(m.region<3)for(unsigned i=0;i<8;i++){check(expected_bank[m.region][m.word][i]==expected(m.layer,m.logical,m.word,i),"actual mutable read after lifetime switch");read_checks++;}}
    }
   }else{
    check(layer_releases==6&&t.up_encoder_debug_completed_layers==6,"final before actual six result releases");
    check((m.origin==2&&!m.write&&m.region==1)||(m.origin==3&&!m.write&&m.region==12)||(m.origin==4&&m.write&&m.region==0),"final exact owner mapping");
    if(m.write){writes[6][14]++;for(unsigned i=0;i<8;i++){check(m.data[i]==input.encoded.at(m.word*8+i),"native final encoded output");checks++;}}
    else{reads[6][m.logical]++;if(m.origin==2)for(unsigned i=0;i<8;i++){check(expected_bank[1][m.word][i]==expected(5,14,m.word,i),"final actual pre-added sum");read_checks++;}}
   }
   if(fault==6&&m.layer==1&&m.origin==0&&m.region==0&&m.word==0&&m.write&&!injected){
    check(saved_valid&&saved.layer==0&&saved.origin==m.origin&&saved.region==m.region&&saved.word==m.word&&saved.write==m.write&&saved.tag!=m.tag,"saved real old-layer fresh ACK identity");
    bool changed=false;for(unsigned i=0;i<8;i++)changed|=saved.data[i]!=m.data[i];check(changed,"new source payload genuinely differs from old ACK");
    stray=true;stray_due=clocks+1;injected=true;orphan_offers++;orphan_queued++;
    std::cout<<"ORPHAN_OFFER old_layer="<<saved.layer<<" old_tag="<<saved.tag<<" genuine_layer="<<m.layer<<" genuine_tag="<<m.tag<<" genuine_due="<<m.due<<" orphan_due="<<stray_due<<std::endl;
   }
  }
  if(t.up_head_fixed_valid&&t.up_head_fixed_ready){
   check(!h.active&&t.up_encoder_owner_lock&&t.up_head_fixed_layer<6&&t.up_head_fixed_layer==t.up_enc_layer&&t.up_head_fixed_tag==hseq++&&t.up_head_fixed_role<3&&t.up_head_fixed_head<8&&t.up_head_fixed_row<320,"head physical identity");
   h=Pending{};h.active=true;h.layer=t.up_head_fixed_layer;h.tag=t.up_head_fixed_tag;h.role=t.up_head_fixed_role;h.head=t.up_head_fixed_head;h.word=t.up_head_fixed_row;h.due=clocks+3+(slow?clocks%4:0);
   for(unsigned i=0;i<10;i++)h.data[i]=input.gold[h.layer].weights.at(h.role*25600+h.word*80+h.head*10+i);head_requests++;hr[h.layer]++;
  }
  if(t.up_O_fixed_valid&&t.up_O_fixed_ready){
   check(!o.active&&t.up_encoder_owner_lock&&t.up_O_fixed_layer<6&&t.up_O_fixed_layer==t.up_enc_layer&&t.up_O_fixed_tag==oseq++&&t.up_O_fixed_row<320,"O physical identity");
   o=Pending{};o.active=true;o.layer=t.up_O_fixed_layer;o.tag=t.up_O_fixed_tag;o.word=t.up_O_fixed_row;o.due=clocks+3+(slow?clocks%4:0);
   for(unsigned i=0;i<80;i++)o.data[i]=input.gold[o.layer].weights.at(3*25600+o.word*80+i);O_requests++;orr[o.layer]++;
  }
  if(!t.reset){
   if(t.up_enc_start_valid&&t.up_enc_start_ready)starts++;
   if(t.up_source_valid&&t.up_source_ready){for(unsigned i=0;i<8;i++)check(t.up_source_data[i]==expected(0,19,t.up_source_word,i),"actual bridge SRAM source bytes");check(t.up_source_tag==tag&&t.up_source_word==sent,"actual bridge source packet identity");check(t.up_enc_layer==0&&t.up_enc_phase==2,"external source wrongly admitted");sent++;source_words++;if(sent==(RV_WORDS)||fault==1||fault==2)feeding=false;}
   if(t.up_enc_layer<6&&t.up_enc_phase==2){unsigned l=t.up_enc_layer;
    if(t.up_encoder_debug_input_codes_retired&&!retired_input[l]){check(!t.up_encoder_debug_normal_codes_lease_held&&t.up_encoder_debug_completed_heads==8&&t.up_encoder_debug_context_writes==(RV_WORDS)&&reads[l][2]==(RV_FRAMES*160)&&acks[l][8]==(RV_WORDS)&&!h.active,"input codes premature retirement");retired_input[l]=true;initial_retirements++;}
    if(t.up_encoder_debug_context_codes_retired&&!retired_context[l]){check(retired_input[l]&&!t.up_encoder_debug_context_lease_held&&reads[l][9]==(RV_CODEWORDS)&&acks[l][22]==(RV_WORDS)&&!o.active,"context premature retirement");retired_context[l]=true;context_retirements++;}
   }
   if(t.up_encoder_debug_layer_accept){check_layer();layer_accepts++;std::cout<<"LAYER_ACCEPT layer="<<unsigned(t.up_enc_layer)<<" clocks="<<clocks<<" mutable="<<child_requests[t.up_enc_layer]<<" head="<<hr[t.up_enc_layer]<<" O="<<orr[t.up_enc_layer]<<std::endl;}
   if(t.up_encoder_debug_layer_release){check(t.up_encoder_backing_lease_held&&!t.up_enc_result_valid&&layer_accepts==layer_releases+1,"child release is not whole publication");layer_releases++;}
   if(t.up_enc_done_valid&&t.up_enc_done_ready)DONEs++;
   if(t.up_encoder_commit){check(t.up_enc_done_valid&&t.up_enc_done_ready&&t.up_enc_done_fault==0&&t.up_encoder_debug_completed_layers==6&&!m.active&&!h.active&&!o.active&&!stray,"premature whole commit");commits++;}
  }
  t.clk=1;t.eval();t.clk=0;t.eval();clocks++;
  if(stray_consumed)check(t.up_encoder_owner_lock&&!t.up_enc_done_valid&&!t.up_enc_result_valid&&m.active&&m.layer==1,"orphan rejected without losing genuine queue");
 }

};

}
