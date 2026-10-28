#include "verilated.h"
#if KIND==0
#include "Vrv_onchip_encoder_head_v1.h"
using Top=Vrv_onchip_encoder_head_v1;
constexpr unsigned latency=3,lanes=10;
#elif KIND==1
#include "Vrv_onchip_encoder_O_v1.h"
using Top=Vrv_onchip_encoder_O_v1;
constexpr unsigned latency=3,lanes=80;
#else
#include "Vrv_onchip_encoder_memory_v1.h"
using Top=Vrv_onchip_encoder_memory_v1;
constexpr unsigned latency=6,lanes=8;
#endif
#include <fstream>
#include <vector>
#include <string>
#include <iostream>
#include <stdexcept>
#include <array>
void check(bool x,const char*m){if(!x)throw std::runtime_error(m);}
using Words=std::vector<uint32_t>;
Words read(const std::string&p){std::ifstream f(p,std::ios::binary|std::ios::ate);check(bool(f),"input open");auto n=f.tellg();Words v(size_t(n)/4);f.seekg(0);f.read((char*)v.data(),n);check(bool(f),"input read");return v;}
int main(int argc,char**argv){try{
 Verilated::commandArgs(argc,argv);check(argc==2,"manifest argument");std::ifstream f(argv[1]);
 std::array<Words,6> weights;std::array<std::array<Words,23>,6> image;std::string path;
 for(unsigned l=0;l<6;l++){f>>path;weights[l]=read(path);for(unsigned r:{7,15,16,17,18,21,20,19,8,9,10,14}){f>>path;image[l][r]=read(path);}for(unsigned i=0;i<12;i++)f>>path;}
 f>>path>>path;auto learned=read(path);
 Top t;uint64_t packets=0,checks=0,holds=0,warm=0;
 auto tick=[&](){t.clk=0;t.eval();t.clk=1;t.eval();t.clk=0;t.eval();};
 t.por_reset=1;t.warm_reset=0;t.req_valid=0;t.rsp_ready=0;tick();t.por_reset=0;
 auto identity=[&](){check(t.rsp_tag==packets+1&&t.rsp_layer==t.req_layer,"tag/layer");
#if KIND==0
 check(t.rsp_role==t.req_role&&t.rsp_head==t.req_head&&t.rsp_row==t.req_row,"QKV identity");
#elif KIND==1
 check(t.rsp_row==t.req_row,"O identity");
#else
 check(t.rsp_client==t.req_client&&t.rsp_backing_owner==t.req_backing_owner&&t.rsp_scalar==t.req_scalar&&t.rsp_write==t.req_write&&t.rsp_origin==t.req_origin&&t.rsp_region==t.req_region&&t.rsp_word==t.req_word&&t.rsp_job==t.req_job&&t.rsp_session==t.req_session&&t.rsp_sequence==t.req_sequence,"full memory identity");
#endif
 };
 auto packet=[&](const Words&v,unsigned off){
  check(t.req_ready&&t.idle&&!t.rsp_valid,"idle queue");t.req_tag=packets+1;t.req_valid=1;t.rsp_ready=0;tick();t.req_valid=0;
  for(unsigned i=1;i<latency;i++){check(!t.rsp_valid&&!t.req_ready&&!t.idle,"pre-latency busy");tick();}
  auto payload=[&](){check(t.rsp_valid&&!t.fault,"due response");identity();for(unsigned j=0;j<lanes;j++){check(t.rsp_data[j]==v.at(off+j),"ROM data");checks++;}};
  payload();
  for(unsigned i=0;i<packets%4;i++){tick();payload();holds++;}
  if(packets%997==0){t.warm_reset=1;t.rsp_ready=1;tick();payload();warm++;t.warm_reset=0;}
  t.rsp_ready=1;tick();check(!t.rsp_valid&&t.idle,"retired");packets++;
 };
 for(unsigned l=0;l<6;l++){t.req_layer=l;
#if KIND==0
  for(unsigned r=0;r<3;r++)for(unsigned h=0;h<8;h++)for(unsigned row=0;row<320;row++){t.req_role=r;t.req_head=h;t.req_row=row;packet(weights[l],r*25600+row*80+h*10);}
#elif KIND==1
  for(unsigned row=0;row<320;row++){t.req_row=row;packet(weights[l],3*25600+row*80);}
#else
  const unsigned sizes[8]={240,80,40,40,12800,640,12800,160},logical[8]={7,7,21,20,15,16,17,18};
  t.req_client=2;t.req_backing_owner=2;t.req_scalar=0;t.req_write=0;t.req_origin=0;t.req_job=0;t.req_session=0;t.req_sequence=0;
  for(unsigned r=4;r<12;r++)for(unsigned w=0;w<sizes[r-4];w++){t.req_region=r;t.req_word=w;packet(image[l][logical[r-4]],(w+(r==5?240:0))*8);}
#endif
 }
#if KIND==2
 t.req_layer=6;t.req_origin=3;t.req_region=12;for(unsigned w=0;w<40;w++){t.req_word=w;packet(learned,w*8);}
#endif
 // Invalid address produces zero data and a sticky fault, cleared by POR.
 t.req_layer=7;t.req_valid=1;t.rsp_ready=0;tick();t.req_valid=0;for(unsigned i=1;i<latency;i++)tick();check(t.fault&&t.rsp_valid,"illegal address");for(unsigned j=0;j<lanes;j++)check(!t.rsp_data[j],"illegal address zero");
 t.por_reset=1;tick();check(!t.rsp_valid&&!t.fault&&t.idle,"POR cancellation");
 std::cout<<"RESPONDER_PASS kind="<<KIND<<" packets="<<packets<<" bytes="<<packets*lanes*4<<" word_checks="<<checks<<" held_cycles="<<holds<<" warm_cycles="<<warm<<" mismatches=0\n";return 0;
}catch(const std::exception&e){std::cerr<<"RESPONDER_FAIL "<<e.what()<<"\n";return 1;}}
