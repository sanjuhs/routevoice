#include "verilated.h"
#include "Vrv_onchip_frontend_v1.h"
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
static void check(bool b,const char*m){if(!b)throw std::runtime_error(m);}
int main(int argc,char**argv){try{
 Verilated::commandArgs(argc,argv);check(argc==2,"fixture path");Vrv_onchip_frontend_v1 t;
 auto tick=[&](){t.clk=0;t.eval();t.clk=1;t.eval();t.clk=0;t.eval();};
 t.por_reset=1;t.warm_reset=0;t.req_valid=0;t.rsp_ready=0;tick();t.por_reset=0;
 const unsigned regions[]={0,1,4,5,8};const char*files[]={"conv1_weights","conv1_bias","conv2_weights","conv2_bias","linear_weights"};
 uint64_t packets=0,held=0,warm=0;
 for(unsigned k=0;k<5;k++){
  std::ifstream f(std::string(argv[1])+"/frontend/shared/"+files[k]+".bin",std::ios::binary|std::ios::ate);check(bool(f),"open independent binary");
  size_t n=f.tellg();std::vector<uint32_t> words(n/4);f.seekg(0);f.read((char*)words.data(),n);check(bool(f),"read binary");
  for(unsigned w=0;w<words.size();w++){
   t.req_valid=1;t.req_client=0;t.req_backing_owner=0;t.req_scalar=1;t.req_write=0;t.req_layer=3;t.req_origin=2;t.req_region=regions[k];t.req_word=w;t.req_tag=0x80000000u+w;t.req_job=123;t.req_session=456;t.req_sequence=789;t.eval();check(t.req_ready&&t.idle&&!t.rsp_valid,"idle ready");
   tick();t.req_valid=0;t.req_word=0xffffffffu;t.req_tag=0; t.eval();
   auto observe=[&](){t.eval();check(t.rsp_valid&&!t.req_ready&&!t.idle&&!t.fault,"held queue");check(t.rsp_client==0&&t.rsp_backing_owner==0&&t.rsp_scalar&&!t.rsp_write&&t.rsp_layer==3&&t.rsp_origin==2&&t.rsp_region==regions[k]&&t.rsp_word==w&&t.rsp_tag==0x80000000u+w&&t.rsp_job==123&&t.rsp_session==456&&t.rsp_sequence==789,"all captured metadata");check(t.rsp_data[0]==words[w],"native FP32 mismatch");for(unsigned i=1;i<8;i++)check(t.rsp_data[i]==0,"zero padding");};
   observe();if(packets%4096==0){for(unsigned i=0;i<3;i++){tick();observe();held++;}t.warm_reset=1;t.rsp_ready=1;for(unsigned i=0;i<3;i++){tick();observe();warm++;}t.warm_reset=0;}
   t.rsp_ready=1;tick();t.rsp_ready=0;check(!t.rsp_valid&&t.idle,"ACK");packets++;
  }
 }
 check(packets==2074560,"whole native words");
 for(unsigned k=0;k<5;k++){
  t.req_valid=1;t.req_region=regions[k];t.req_word=0xffffffffu;t.eval();check(!t.req_ready,"reject bad address");tick();check(t.fault&&!t.rsp_valid,"invalid offer diagnostic");
  t.por_reset=1;tick();t.por_reset=0;t.req_valid=0;t.eval();check(!t.fault&&t.idle,"POR clear");
 }
 t.req_valid=1;t.req_region=0;t.req_word=0;t.req_write=1;t.eval();check(!t.req_ready,"immutable write refused");tick();check(t.fault&&!t.rsp_valid,"no write ACK");
 std::cout<<"FRONTEND_ROM_PASS packets="<<packets<<" bytes="<<packets*4<<" held_cycles="<<held<<" warm_cycles="<<warm<<" invalid_addresses=5 rejected_writes=1 mismatches=0\n";
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
