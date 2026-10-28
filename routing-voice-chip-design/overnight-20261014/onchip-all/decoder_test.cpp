// Independent exhaustive native-image readout test for either decoder service.
#include "verilated.h"
#ifdef TEST_SELF
#include "Vrv_onchip_decoder_self_v1.h"
using Top = Vrv_onchip_decoder_self_v1;
#else
#include "Vrv_onchip_decoder_body_v1.h"
using Top = Vrv_onchip_decoder_body_v1;
#endif
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
static void check(bool b,const char* m){if(!b)throw std::runtime_error(m);}
static std::vector<uint8_t> load(const std::string&p){
 std::ifstream f(p,std::ios::binary|std::ios::ate);check(bool(f),"open binary");
 const auto size=f.tellg();check(size>0,"empty binary");std::vector<uint8_t>v(size);
 f.seekg(0);f.read(reinterpret_cast<char*>(v.data()),size);check(bool(f),"read binary");return v;
}
int main(int argc,char**argv){try{
 Verilated::commandArgs(argc,argv);check(argc==2,"fixture root argument");
 std::string root=argv[1];Top t;uint64_t packets=0,hold_cycles=0,warm_cycles=0;
 auto tick=[&](){t.clk=0;t.eval();t.clk=1;t.eval();t.clk=0;t.eval();};
 t.clk=0;t.por_reset=1;t.warm_reset=0;t.req_valid=0;t.rsp_ready=0;tick();
 t.por_reset=0;t.eval();check(!t.rsp_valid&&!t.fault&&t.idle,"POR");
 auto packet=[&](unsigned layer,unsigned role,unsigned tile,unsigned region,unsigned word,const std::vector<uint8_t>&bytes,size_t offset){
  check(offset+32<=bytes.size(),"reference bounds");
  std::array<uint32_t,8> expected{};std::memcpy(expected.data(),bytes.data()+offset,32);
  uint32_t tag=0x80000000u+packets*13u;
  check(!t.rsp_valid&&t.req_ready&&t.idle,"ready before request");
  t.req_valid=1;t.req_layer=layer;t.req_role=role;t.req_region=region;t.req_word=word;t.req_tag=tag;
#ifndef TEST_SELF
  t.req_tile=tile;
#endif
  t.eval();check(!t.rsp_valid,"no combinational reply");tick();t.req_valid=0;
  // Poison live request selectors after capture. Every held cycle must still match.
  t.req_layer=7;t.req_role=0;t.req_region=!region;t.req_word=1;t.req_tag=~tag;
#ifndef TEST_SELF
  t.req_tile=7;
#endif
  auto observe=[&](){
   t.eval();check(t.rsp_valid&&!t.req_ready&&!t.idle&&!t.fault,"held queue state");
   check(t.rsp_tag==tag&&t.rsp_layer==layer&&t.rsp_role==role&&t.rsp_region==region&&t.rsp_word==word,"held response identity");
#ifndef TEST_SELF
   check(t.rsp_tile==tile,"held tile identity");
#endif
   for(unsigned j=0;j<8;j++)check(t.rsp_data[j]==expected[j],"native binary payload mismatch");
  };
  observe();
  if(packets%4096==0){
   for(unsigned k=0;k<3;k++){tick();observe();hold_cycles++;}
   t.warm_reset=1;t.rsp_ready=1;
   for(unsigned k=0;k<3;k++){tick();observe();warm_cycles++;}
   t.warm_reset=0;
  }
  t.rsp_ready=1;tick();t.rsp_ready=0;check(!t.rsp_valid&&t.idle,"ACK retirement");packets++;
 };
#ifdef TEST_SELF
 auto coefficients=load(root+"/self/coefficients.bin"), metadata=load(root+"/self/metadata.bin");
 for(unsigned l=0;l<6;l++)for(unsigned r=0;r<4;r++){
  for(unsigned w=0;w<3200;w++)packet(l,r,0,0,w,coefficients,((l*4+r)*3200+w)*32);
  for(unsigned w=0;w<80;w++)packet(l,r,0,1,w,metadata,((l*4+r)*80+w)*32);
 }
 check(packets==78720,"complete self image coverage");
#else
 auto cross=load(root+"/cross/coefficients.bin"), cm=load(root+"/cross/metadata.bin");
 auto up=load(root+"/ff/up-weights.bin"), um=load(root+"/ff/up-metadata.bin");
 auto down=load(root+"/ff/down-weights.bin"), dm=load(root+"/ff/down-metadata.bin");
 for(unsigned l=0;l<6;l++){
  for(unsigned r=4;r<6;r++){
   for(unsigned w=0;w<3200;w++)packet(l,r,0,0,w,cross,((l*2+r-4)*3200+w)*32);
   for(unsigned w=0;w<80;w++)packet(l,r,0,1,w,cm,((l*2+r-4)*80+w)*32);
  }
  // Reference enumerates the native matrix coordinates, not a flattened ROM address.
  for(unsigned tile=0;tile<8;tile++){
   for(unsigned row=0;row<320;row++)for(unsigned segment=0;segment<10;segment++)
    packet(l,6,tile,0,row*10+segment,up,(l*320+row)*2560+tile*320+segment*32);
   for(unsigned w=0;w<160;w++)packet(l,6,tile,1,w,um,((l*2560+tile*320+w*2)*4)*4);
  }
  for(unsigned row=0;row<1280;row++)for(unsigned segment=0;segment<10;segment++)
   packet(l,7,0,0,row*10+segment,down,(l*1280+row)*320+segment*32);
  for(unsigned w=0;w<160;w++)packet(l,7,0,1,w,dm,((l*320+w*2)*4)*4);
 }
 check(packets==278400,"complete body image coverage");
#endif
 // Illegal layer is acknowledged deterministically with a sticky diagnostic.
 t.req_layer=7;t.req_valid=1;tick();check(t.rsp_valid&&t.fault,"invalid address detection");
 t.req_valid=0;t.por_reset=1;tick();check(!t.rsp_valid&&!t.fault,"POR recovery");
 std::cout<<"RESPONDER_PASS packets="<<packets<<" bytes="<<packets*32
          <<" held_cycles="<<hold_cycles<<" warm_cycles="<<warm_cycles<<" mismatches=0\n";
 return 0;
}catch(const std::exception&e){std::cerr<<"RESPONDER_FAIL "<<e.what()<<'\n';return 1;}}
