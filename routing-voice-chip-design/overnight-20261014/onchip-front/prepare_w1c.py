"""W1c only: preserve native FP32 bits; original top and other services unchanged."""
from pathlib import Path
import hashlib,json,re,shutil
WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[1]
SRC=ROOT/'experiments/chip-integration-20261012-frontend-learned-norm-connected-source-v3'
RUN=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-front'
FIX=Path.home()/'.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3'
POS=ROOT/'experiments/runtime-source-position-immutable-rom-source-20261013-v1'
OLD='rv_pcm_encoder_greedy_frontend_history_producer_metadata_KV_tables_onboard_v1'
NEW='rv_allonchip_top_w1c'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)
def main():
 RUN.mkdir(parents=True,exist_ok=True)
 rom=RUN/'rom';rom.mkdir(exist_ok=True)
 images={0:('conv1_weights',4096000),1:('conv1_bias',2560),4:('conv2_weights',4096000),5:('conv2_bias',1280),8:('linear_weights',102400)}
 manifest=[]
 for r,(name,size) in images.items():
  src=FIX/'frontend/shared'/(name+'.bin');data=src.read_bytes();assert len(data)==size
  target=rom/(name+'.hex');target.write_text(''.join(data[i:i+4][::-1].hex()+'\n' for i in range(0,size,4)))
  assert b''.join(int(x,16).to_bytes(4,'little') for x in target.read_text().splitlines())==data
  manifest.append(dict(region=r,input=str(src),input_bytes=size,input_sha256=digest(src),output=str(target),output_sha256=digest(target),width_bits=32,words=size//4,roundtrip_pass=True))
 src=Path((FIX/'producer/paths.txt').read_text().splitlines()[0]);data=src.read_bytes();assert len(data)==1310720
 target=rom/'positions.hex';target.write_text(''.join(data[i:i+8][::-1].hex()+'\n' for i in range(0,len(data),8)))
 assert b''.join(int(x,16).to_bytes(8,'little') for x in target.read_text().splitlines())==data
 assert target.read_bytes()==(POS/'source_position_163840x64.memh').read_bytes()
 manifest.append(dict(service='positions',input=str(src),input_bytes=len(data),input_sha256=digest(src),output=str(target),output_sha256=digest(target),width_bits=64,words=len(data)//8,roundtrip_pass=True,retained_image_identical=True))
 (WORK/'rom-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 shutil.copyfile(POS/'rv_source_position_immutable_rom_v1.sv',WORK/'rv_source_position_immutable_rom_v1.sv')
 fields={'client':'[1:0]','backing_owner':'[1:0]','scalar':'','write':'','layer':'[2:0]','origin':'[2:0]','region':'[3:0]','tag':'[31:0]','word':'[31:0]','job':'[31:0]','session':'[31:0]','sequence':'[31:0]'}
 params=',\n'.join(f' parameter {name.upper()}_FILE = "{rom/(name+".hex")}"' for name,size in images.values())
 decl='\n'.join(f' logic [31:0] {name}[0:{size//4-1}];\n initial $readmemh({name.upper()}_FILE,{name});' for name,size in images.values())
 ports=',\n'.join(f' input wire {w} req_{n}, output logic {w} rsp_{n}' for n,w in fields.items())
 cases='\n'.join(f' {r}: if(req_word < {size//4}) begin selected={name}[req_word]; legal_address=1; end' for r,(name,size) in images.items())
 capture='\n'.join(f'       rsp_{n} <= req_{n};' for n in fields)
 clear='\n'.join(f'       rsp_{n} <= 0;' for n in fields)
 (WORK/'rv_onchip_frontend_v1.sv').write_text(f'''// Native FP32 immutable words. Accepted N -> PRE N+1, held until ACK.
// No runtime write port; no claim of physical ROM area/timing qualification.
module rv_onchip_frontend_v1 #(
{params}
)(input wire clk, por_reset, warm_reset,
 input wire req_valid, output wire req_ready,
{ports},
 output wire idle, output logic fault,
 output logic rsp_valid, input wire rsp_ready, output logic [255:0] rsp_data);
{decl}
 logic [31:0] selected;
 logic legal_address;
 always_comb begin
 selected=0; legal_address=0;
 case(req_region)
{cases}
 default: ;
 endcase
 end
 wire legal = legal_address && req_client==0 && req_backing_owner==0 && req_scalar && !req_write;
 assign idle=!rsp_valid;
 assign req_ready=!por_reset && !warm_reset && !rsp_valid && (!req_valid || legal);
 always_ff @(posedge clk) begin
   if(por_reset) begin
     rsp_valid<=0; rsp_data<=0; fault<=0;
{clear}
   end else if(!warm_reset) begin
     if(req_valid && !legal) fault<=1;
     if(rsp_valid && rsp_ready) rsp_valid<=0;
     if(req_valid && req_ready) begin
       rsp_valid<=1; rsp_data<={{224'd0,selected}};
{capture}
     end
   end
 end
endmodule
''')
 oldrtl=(SRC/(OLD+'.sv')).read_text();header=oldrtl[oldrtl.index('(\n')+2:oldrtl.index('\n);')]
 ports=[]
 for line in header.splitlines():
  line=line.split('//')[0].strip().rstrip(',')
  if not line:continue
  m=re.fullmatch(r'(input|output) wire\s*(\[[^]]+\])?\s*(.*)',line);assert m,line
  d,w,names=m.groups()
  for n in names.split(','):ports.append((d,w or '',n.strip()))
 moved={n for d,w,n in ports if d=='input' and n.startswith('source_position_')}
 ext={n:w for d,w,n in ports if d=='input' and n.startswith('external_')}
 header=',\n'.join(f' {"output" if n in moved else d} wire {w} {n}' for d,w,n in ports)
 debug=',\n'.join(f' output wire {w} w1c_{n}' for n,w in ext.items())
 wrapper=f'// W1c: retained top unchanged; only frontend immutable and positions internalized.\nmodule {NEW}(\n{header},\n{debug},\n output wire onchip_frontend_fault,onchip_position_rejected,\n output wire w1c_front_select,w1c_front_idle,w1c_front_rsp_valid\n);\n'
 wrapper+=f' {OLD} original(\n'+',\n'.join(f' .{n}({"w1c_" if n in ext else ""}{n})' for d,w,n in ports)+'\n );\n'
 wrapper+=' assign w1c_front_select=external_req_client==0 && (external_req_region==0 || external_req_region==1 || external_req_region==4 || external_req_region==5 || external_req_region==8);\n'
 wrapper+=' wire front_ready;\n'
 for n,w in fields.items():wrapper+=f' wire {w} front_rsp_{n};\n'
 wrapper+=' wire [255:0] front_rsp_data;\n'
 wrapper+=' assign w1c_external_idle=external_idle && w1c_front_idle;\n assign w1c_external_req_ready=w1c_front_select ? front_ready : (w1c_front_idle && external_req_ready);\n'
 for n,w in ext.items():
  if n in ('external_idle','external_req_ready'):continue
  suffix=n[len('external_rsp_'):]
  expr='w1c_front_rsp_valid || external_rsp_valid' if suffix=='valid' else f'w1c_front_rsp_valid ? front_rsp_{suffix} : external_rsp_{suffix}'
  wrapper+=f' assign w1c_{n}={expr};\n'
 con={'clk':'clk','por_reset':'frontend_por_reset','warm_reset':'reset','req_valid':'external_req_valid && w1c_front_select','req_ready':'front_ready','idle':'w1c_front_idle','fault':'onchip_frontend_fault','rsp_valid':'w1c_front_rsp_valid','rsp_ready':'external_rsp_ready','rsp_data':'front_rsp_data'}
 for n in fields:con['req_'+n]='external_req_'+n;con['rsp_'+n]='front_rsp_'+n
 wrapper+=' rv_onchip_frontend_v1 frontend_rom(\n'+',\n'.join(f' .{a}({b})' for a,b in con.items())+'\n );\n'
 con={'clk':'clk','por_reset':'producer_por_reset','common_reset':'reset','idle':'source_position_idle','request_rejected':'onchip_position_rejected'}
 for n in ('valid','ready','session','generation','tag','word'):con['request_'+n]='source_position_'+n
 for n in ('valid','ready','session','generation','tag','word','data'):con['response_'+n]='source_position_response_'+n
 wrapper+=f' rv_source_position_immutable_rom_v1 #(.IMAGE_FILE("{target}")) positions(\n'+',\n'.join(f' .{a}({b})' for a,b in con.items())+'\n );\nendmodule\n'
 (WORK/(NEW+'.sv')).write_text(wrapper)
 for src in SRC.glob('*.hpp'):shutil.copyfile(src,WORK/src.name)
 host=(SRC/'four_stage.cpp').read_text().replace(OLD,NEW)
 for n in moved:host=re.sub(r't\.'+n+r'=[01];','',host)
 marker='   p.learned_conservation();f.frontend_conservation();'
 host=once(host,marker,marker+'''
   enc::require(f.external_frontend_requests==55720960&&f.external_frontend_replies==55720960&&p.producer.position_requests==2560&&p.producer.position_replies==2560,"W1c F64 exact observed coverage");
   std::cout<<"ONCHIP service=frontend_immutable rtl_replies="<<f.external_frontend_replies<<" host_replies=0 mismatches=0"<<std::endl;
   std::cout<<"ONCHIP service=producer_positions rtl_replies="<<p.producer.position_replies<<" host_replies=0 mismatches=0"<<std::endl;
''')
 (WORK/'four_stage.cpp').write_text(host)
 p=(WORK/'frontend_services.hpp').read_text()
 start=p.index('  t.step_enable=!mode');end=p.index('  t.clk=0;',start)
 p=p[:start]+'''  t.step_enable=!mode||(bits&3);
  // Host external provider quiesced: immutable frontend requests are answered in RTL.
  t.external_req_ready=1;t.external_idle=1;t.external_rsp_valid=0;
'''+p[end:]
 marker='  std::array<uint32_t,6>dn'
 idx=p.index(marker)
 observe='''  check(mode==0&&fault==0&&!hold_request,"W1c frontend deterministic nominal mode");
  check(!t.onchip_frontend_fault&&!t.external_rsp_valid,"W1c frontend ROM fault or host reply");
  check(bool(t.w1c_front_idle)==(!reply.active||backend_reply),"W1c frontend queue idle");
  check(bool(t.w1c_front_rsp_valid)==(reply.active&&!backend_reply),"W1c frontend exact PRE N+1 schedule");
  if(t.w1c_front_rsp_valid){
   check(t.w1c_external_rsp_tag==reply.tag&&t.w1c_external_rsp_region==reply.region&&t.w1c_external_rsp_word==reply.word&&t.w1c_external_rsp_write==reply.write&&t.w1c_external_rsp_client==reply.client,"W1c frontend reply identity");
   check(t.w1c_external_rsp_backing_owner==0&&t.w1c_external_rsp_scalar&&t.w1c_external_rsp_layer==0&&t.w1c_external_rsp_origin==0&&t.w1c_external_rsp_job==0&&t.w1c_external_rsp_session==0&&t.w1c_external_rsp_sequence==0,"W1c frontend complete metadata");
   check(t.w1c_external_rsp_data[0]==reply.data,"W1c frontend FP32 bits mismatch");
   for(unsigned i=1;i<8;i++)check(t.w1c_external_rsp_data[i]==0,"W1c frontend scalar padding");
  }
'''
 p=p[:idx]+observe+p[idx:]
 (WORK/'frontend_services.hpp').write_text(p)
 p=(WORK/'taalas_adapter_session_compact_token_services_f500_v1.hpp').read_text().replace('position remains external.', 'position is now RTL-owned and checked below.')
 for n in moved:p=re.sub(r't\.'+n+r'=[^;]*;','',p)
 marker='  take_position=!t.reset'
 idx=p.index(marker)
 p=p[:idx]+'''  h.check(h.mode==0&&!t.onchip_position_rejected,"W1c position deterministic legal mode");
  h.check(bool(t.source_position_idle)==!position.active,"W1c position idle");
  h.check(bool(t.source_position_ready)==(!t.reset&&!t.producer_por_reset&&!position.active),"W1c position queue ready/reset fencing");
  h.check(bool(t.source_position_response_valid)==(position.active&&!position.delay),"W1c position exact PRE N+3 schedule");
  if(t.source_position_response_valid){
   h.check(t.source_position_response_session==position.sid&&t.source_position_response_generation==position.gen&&t.source_position_response_tag==position.tag&&t.source_position_response_word==position.word,"W1c position held reply identity");
   h.check(t.source_position_response_data==position.data,"W1c position original binary mismatch");
  }
'''+p[idx:]
 (WORK/'taalas_adapter_session_compact_token_services_f500_v1.hpp').write_text(p)
 for path in [WORK/'four_stage.cpp',*WORK.glob('*.hpp')]:
  for n in moved:assert not re.search(r'\bt\.'+n+r'\s*=(?!=)',path.read_text()),(path,n)
 assert 'reply.data' not in p[p.index(' void drive(){'):p.index(' void capture(){')]
 c=json.loads((ROOT/'experiments/chip-integration-20261012-Q8-learned-fulltables-lint-generation-control-v2/commands.json').read_text())
 for key,args in c.items():
  args[args.index('--top-module')+1]=NEW;args[args.index('--Mdir')+1]=str(RUN/('obj' if key=='generate-full' else 'lint'))
  args.extend(str(WORK/f) for f in [NEW+'.sv','rv_onchip_frontend_v1.sv','rv_source_position_immutable_rom_v1.sv'])
  if key=='generate-full':
   args[args.index(str(SRC/'four_stage.cpp'))]=str(WORK/'four_stage.cpp');i=args.index('-CFLAGS')+1;args[i]=args[i].replace(str(SRC),str(WORK))
 (WORK/'no-pch.mk').write_text((ROOT/'experiments/chip-integration-20261012-Q8-learned-fulltables-compile-v3/no-pch.mk').read_text().replace(OLD,NEW))
 c['compile']=['/usr/bin/make','-C',str(RUN/'obj'),'-f',str(WORK/'no-pch.mk'),'-j6','OPT_FAST=-O3','OPT_SLOW=-O3','CXX=/usr/bin/c++','LINK=/usr/bin/c++','VM_PARALLEL_BUILDS=1']
 numeric=json.loads((ROOT/'experiments/chip-integration-20261012-Q8-learned-fulltables-numerical-run-v2/commands.json').read_text())
 oldrun=str(Path.home()/'.local/state/routevoice-internal-runs/20261012/Q8-learned-fulltables-numerical-run-v2/actual')
 for key in ('fixture','positive','render'):
  args=numeric[key]
  if key!='render':args[0]=str(RUN/'obj'/('V'+NEW))
  c[key]=[a.replace(oldrun,str(RUN/'actual')) for a in args]
 if (WORK/'commands.json').exists():
  for k,v in json.loads((WORK/'commands.json').read_text()).items():
   if k not in c:c[k]=v
 (WORK/'commands.json').write_text(json.dumps(c,indent=2)+'\n')
 (WORK/'source-provenance.json').write_text(json.dumps({str(p):digest(p) for p in [SRC/(OLD+'.sv'),SRC/'four_stage.cpp',*SRC.glob('*.hpp'),POS/'rv_source_position_immutable_rom_v1.sv']},indent=2)+'\n')
 print('W1c-STATUS: generated frontend FP32 and reused position ROM; 9608960 native bytes; six exact hex roundtrips pass')
if __name__=='__main__':main()
