#include "verilated.h"
#include "Vrv_source_position_immutable_rom_v1.h"
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
static void check(bool b,const char*m){if(!b)throw std::runtime_error(m);}
int main(int argc,char**argv){try{
 Verilated::commandArgs(argc,argv);check(argc==2,"position binary argument");
 std::ifstream f(argv[1],std::ios::binary|std::ios::ate);check(bool(f),"open frozen binary");
 check(f.tellg()==1310720,"position binary size");std::vector<unsigned char> bytes(1310720);f.seekg(0);f.read((char*)bytes.data(),bytes.size());check(bool(f),"read binary");
 Vrv_source_position_immutable_rom_v1 t;
 auto tick=[&](){t.clk=0;t.eval();t.clk=1;t.eval();t.clk=0;t.eval();};
 t.por_reset=1;t.common_reset=0;t.request_valid=0;t.response_ready=0;tick();t.por_reset=0;
 uint64_t held=0,warm=0;
 for(unsigned w=0;w<163840;w++){
  uint64_t expected=0;for(unsigned i=0;i<8;i++)expected|=uint64_t(bytes[w*8+i])<<(i*8);
  t.request_valid=1;t.request_session=0x10203040u+w;t.request_generation=0;t.request_tag=0x87654321u-w;t.request_word=w;t.eval();
  check(t.idle&&t.request_ready&&!t.request_rejected&&!t.response_valid,"ready before request");
  tick();t.request_valid=0;t.request_session=0;t.request_generation=7;t.request_tag=0;t.request_word=262143;t.eval();
  check(!t.response_valid&&!t.idle&&!t.request_ready,"N+1 busy");tick();check(!t.response_valid,"N+2 busy");tick();
  auto observe=[&](){t.eval();check(t.response_valid&&!t.idle&&!t.request_ready,"N+3 held queue");check(t.response_word==w&&t.response_session==0x10203040u+w&&t.response_generation==0&&t.response_tag==0x87654321u-w,"captured identity");check(t.response_data==expected,"binary position mismatch");};
  observe();if(w%4096==0){for(unsigned i=0;i<3;i++){tick();observe();held++;}t.common_reset=1;t.response_ready=1;for(unsigned i=0;i<3;i++){tick();observe();warm++;}t.common_reset=0;}
  t.response_ready=1;tick();t.response_ready=0;check(t.idle&&!t.response_valid,"ACK retirement");
 }
 std::cout<<"POSITION_EXHAUSTIVE_PASS packets=163840 bytes=1310720 held_cycles="<<held<<" warm_cycles="<<warm<<" mismatches=0\n";return 0;
}catch(const std::exception&e){std::cerr<<"POSITION_EXHAUSTIVE_FAIL "<<e.what()<<"\n";return 1;}}
