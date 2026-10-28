"""W1b encoder-only reproducible ROM, wrapper, observer and command generation."""
from pathlib import Path
import hashlib,json,re,shutil
W=Path(__file__).resolve().parent
R=W.parents[1]
S=R/'experiments/chip-integration-20261012-frontend-learned-norm-connected-source-v3'
RUN=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-enc'
FIX=Path.home()/'.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3'
OLD='rv_pcm_encoder_greedy_frontend_history_producer_metadata_KV_tables_onboard_v1'
NEW='rv_allonchip_top_w1b'
RUN.mkdir(parents=True,exist_ok=True)
(W/'rom').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)
manifest=[]
inputs={}
def read(p):
 p=Path(p);inputs[str(p)]=dict(bytes=p.stat().st_size,sha256=sha(p));return p.read_bytes()
def emit(name,data,width):
 p=W/'rom'/f'{name}.hex';n=width//8;assert len(data)%n==0
 p.write_text(''.join(data[i:i+n][::-1].hex()+'\n' for i in range(0,len(data),n)))
 assert b''.join(int(x,16).to_bytes(n,'little') for x in p.read_text().splitlines())==data
 manifest.append(dict(name=name,path=str(p),bytes=len(data),width_bits=width,words=len(data)//n,sha256=sha(p),roundtrip_pass=True))
 return len(data)//n
fields=(FIX/'encoder/inputs.txt').read_text().split();pos=0;head=b'';omat=b'';mem=b''
for layer in range(6):
 weight=read(fields[pos]);assert len(weight)==409600
 for role in range(3):
  for h in range(8):
   for row in range(320):
    off=(role*25600+row*80+h*10)*4;head+=weight[off:off+40]
 omat+=weight[3*25600*4:]
 images={}
 for j,r in enumerate([7,15,16,17,18,21,20,19,8,9,10,14]):images[r]=Path(fields[pos+1+j])
 for r in [7,21,20,15,16,17,18]:mem+=read(images[r])
 pos+=25 # 13 filenames, 8 domains, 4 hashes
mem+=read(fields[pos+1]) # final learned vector after encoded
assert (len(head)+len(omat),len(mem))==(2457600,5146880)
depths={n:emit(n,d,w) for n,d,w in [('encoder_head',head,320),('encoder_O',omat,2560),('encoder_memory',mem,256)]}
(W/'rom-manifest.json').write_text(json.dumps(dict(inputs=inputs,outputs=manifest,native_bytes=7604480),indent=2)+'\n')

def responder(name,width,identity,latency,address,legal):
 ports=['input wire clk, por_reset, warm_reset','input wire req_valid','output wire req_ready, idle','output logic fault','output wire rsp_valid','input wire rsp_ready']
 for field,bits in identity:ports += [f'input wire [{bits-1}:0] req_{field}',f'output logic [{bits-1}:0] rsp_{field}']
 ports += [f'output logic [{width-1}:0] rsp_data']
 text=f'''// Immutable behavioral ROM implementation; no runtime weight write port.
// Accepted edge N -> PRE N+{latency}; payload held through backpressure.
// POR cancels pending transaction. Warm reset fences acceptance and ACK.
module rv_onchip_{name}_v1 #(parameter ROM_FILE="{W/'rom'/f'{name}.hex'}")(
'''+',\n'.join('  '+p for p in ports)+f'''\n);
  logic [{width-1}:0] rom [0:{depths[name]-1}];
  initial $readmemh(ROM_FILE,rom);
  logic busy;
  logic [2:0] remaining;
  wire legal = {legal};
  wire [31:0] address = {address};
  assign req_ready = !busy;
  assign idle = !busy;
  assign rsp_valid = busy && remaining == 0;
  always_ff @(posedge clk) begin
    if (por_reset) begin
      busy<=0; remaining<=0; fault<=0; rsp_data<='0;
'''+''.join(f'      rsp_{f}<=0;\n' for f,b in identity)+f'''    end else begin
      if (busy && remaining != 0) remaining<=remaining-1'b1;
      if (!warm_reset) begin
        if (rsp_valid && rsp_ready) busy<=0;
        if (req_valid && req_ready) begin
          busy<=1; remaining<=3'd{latency-1};
          rsp_data<=legal ? rom[address] : '0;
          if (!legal) fault<=1;
'''+''.join(f'          rsp_{f}<=req_{f};\n' for f,b in identity)+'''        end
      end
    end
  end
endmodule
'''
 (W/f'rv_onchip_{name}_v1.sv').write_text(text)
headid=[('layer',3),('tag',32),('role',2),('head',3),('row',9)]
oid=[('layer',3),('tag',32),('row',9)]
memid=[('client',2),('backing_owner',2),('scalar',1),('write',1),('layer',3),('origin',3),('region',4),('tag',32),('word',32),('job',32),('session',32),('sequence',32)]
responder('encoder_head',320,headid,3,'((32\'(req_layer)*3+32\'(req_role))*8+32\'(req_head))*320+32\'(req_row)','req_layer<6 && req_role<3 && req_row<320')
responder('encoder_O',2560,oid,3,"32'(req_layer)*320+32'(req_row)",'req_layer<6 && req_row<320')
offsets={4:0,5:240,6:320,7:360,8:400,9:13200,10:13840,11:26640}
sizes={4:240,5:80,6:40,7:40,8:12800,9:640,10:12800,11:160}
addr='req_layer==6 ? 160800+req_word : '+"32'(req_layer)*26800+req_word+("+''.join(f'req_region=={r} ? 32\'d{o} : ' for r,o in offsets.items())+"32'd0)"
legal='req_client==2 && req_backing_owner==2 && !req_scalar && !req_write && ((req_layer==6 && req_region==12 && req_word<40) || (req_layer<6 && ('+' || '.join(f'(req_region=={r} && req_word<{n})' for r,n in sizes.items())+')))'
responder('encoder_memory',256,memid,6,addr,legal)
rtl=(S/(OLD+'.sv')).read_text();hdr=rtl[rtl.index('(\n')+2:rtl.index('\n);')];ports=[]
for line in hdr.splitlines():
 line=line.split('//')[0].strip().rstrip(',')
 if not line:continue
 m=re.fullmatch(r'(input|output) wire\s*(\[[^]]+\])?\s*(.*)',line);assert m,line
 d,w,ns=m.groups()
 for n in ns.split(','):ports.append((d,w or '',n.strip()))
moved={n for d,w,n in ports if d=='input' and (n.startswith('up_head_') or n.startswith('up_O_'))}
ext=[(d,w,n) for d,w,n in ports if n.startswith('external_')]
# Expose complete original shared bus for response auditing; retain existing host port names.
header=[f'{"output" if n in moved else d} wire {w} {n}' for d,w,n in ports]
header += [f'output wire {w} onchip_{n}' for d,w,n in ext]
header += ['output wire onchip_head_fault, onchip_O_fault, onchip_memory_fault, onchip_memory_idle, onchip_memory_rsp_valid']
wrapper=f'module {NEW}(\n'+',\n'.join('  '+x for x in header)+'\n);\n'
wrapper+=f'{OLD} original (\n'+',\n'.join(f' .{n}({"onchip_" if n.startswith("external_") else ""}{n})' for d,w,n in ports)+'\n);\n'
for name,prefix,ids in [('encoder_head','up_head_',headid),('encoder_O','up_O_',oid)]:
 conn=dict(clk='clk',por_reset='bank_por_reset',warm_reset='reset',req_valid=prefix+'fixed_valid',req_ready=prefix+'fixed_ready',idle=prefix+'fixed_idle',fault='onchip_'+('head' if name.endswith('head') else 'O')+'_fault',rsp_valid=prefix+'response_valid',rsp_ready=prefix+'response_ready',rsp_data=prefix+'response_data')
 for f,b in ids:conn.update({f'req_{f}':prefix+'fixed_'+f,f'rsp_{f}':prefix+'response_'+f})
 wrapper+=f'rv_onchip_{name}_v1 {name}(\n'+',\n'.join(f' .{a}({b})' for a,b in conn.items())+'\n);\n'
wrapper+='wire encoder_select = onchip_external_req_client==2 && onchip_external_req_backing_owner==2 && onchip_external_req_region>=4 && onchip_external_req_region<=12;\nwire memory_ready;\n'
for f,b in memid+[('data',256)]:wrapper+=f'wire [{b-1}:0] memory_{f};\n'
wrapper+='assign onchip_external_idle=external_idle && onchip_memory_idle;\nassign onchip_external_req_ready=encoder_select ? memory_ready : external_req_ready;\nassign external_req_valid=onchip_external_req_valid && !encoder_select;\nassign onchip_external_rsp_valid=onchip_memory_rsp_valid || external_rsp_valid;\nassign external_rsp_ready=onchip_external_rsp_ready && !onchip_memory_rsp_valid;\n'
for d,w,n in ext:
 if n in ['external_idle','external_req_ready','external_req_valid','external_rsp_valid','external_rsp_ready']:continue
 if d=='output':wrapper+=f'assign {n}=onchip_{n};\n'
 else:wrapper+=f'assign onchip_{n}=onchip_memory_rsp_valid ? memory_{n[len("external_rsp_"):]} : {n};\n'
conn=dict(clk='clk',por_reset='bank_por_reset',warm_reset='reset',req_valid='onchip_external_req_valid && encoder_select',req_ready='memory_ready',idle='onchip_memory_idle',fault='onchip_memory_fault',rsp_valid='onchip_memory_rsp_valid',rsp_ready='onchip_external_rsp_ready',rsp_data='memory_data')
for f,b in memid:conn.update({f'req_{f}':'onchip_external_req_'+f,f'rsp_{f}':'memory_'+f})
wrapper+='rv_onchip_encoder_memory_v1 encoder_memory(\n'+',\n'.join(f' .{a}({b})' for a,b in conn.items())+'\n);\nendmodule\n'
(W/(NEW+'.sv')).write_text(wrapper)
for p in S.glob('*.hpp'):shutil.copyfile(p,W/p.name)
host=(S/'four_stage.cpp').read_text().replace(OLD,NEW)
for n in moved:host=re.sub(r'(?:for\(unsigned i=0;i<\d+;i\+\+\))?t\.'+n+r'(?:\[i\])?=[01];','',host)
host=once(host,'   p.learned_conservation();f.frontend_conservation();','   e.onchip_conservation();p.learned_conservation();f.frontend_conservation();')
(W/'four_stage.cpp').write_text(host)
p=(S/'encoder_services.hpp').read_text()
start=p.index('  t.external_idle=');end=p.index('  // Actual source packets',start)
p=p[:start]+'''  // Frontend is inactive in encoder phase; only quiesce its host bus.
  t.external_idle=1;t.external_req_ready=1;t.external_rsp_valid=0;
'''+p[end:]
observe='''
 uint64_t immutable_replies=0,immutable_packets=0,immutable_checks=0,head_checks=0,O_checks=0;
 void observe_onchip(){
  check(!t.onchip_head_fault&&!t.onchip_O_fault&&!t.onchip_memory_fault,"onchip encoder ROM address fault");
  check(bool(t.up_head_fixed_ready)==!h.active&&bool(t.up_head_fixed_idle)==!h.active,"onchip head queue ready/idle");
  check(bool(t.up_O_fixed_ready)==!o.active&&bool(t.up_O_fixed_idle)==!o.active,"onchip O queue ready/idle");
  check(bool(t.up_head_response_valid)==(h.active&&clocks>=h.due),"onchip head exact N+3 schedule");
  check(bool(t.up_O_response_valid)==(o.active&&clocks>=o.due),"onchip O exact N+3 schedule");
  if(t.up_head_response_valid){
   check(t.up_head_response_layer==h.layer&&t.up_head_response_tag==h.tag&&t.up_head_response_role==h.role&&t.up_head_response_head==h.head&&t.up_head_response_row==h.word,"onchip head reply identity");
   for(unsigned i=0;i<10;i++){check(t.up_head_response_data[i]==h.data[i],"onchip head ROM payload");head_checks++;}
  }
  if(t.up_O_response_valid){
   check(t.up_O_response_layer==o.layer&&t.up_O_response_tag==o.tag&&t.up_O_response_row==o.word,"onchip O reply identity");
   for(unsigned i=0;i<80;i++){check(t.up_O_response_data[i]==o.data[i],"onchip O ROM payload");O_checks++;}
  }
  check(!t.external_req_valid,"encoder immutable request escaped onchip route");
  check(bool(t.onchip_memory_rsp_valid)==(m.active&&m.region>=4&&clocks>=m.due),"onchip immutable exact N+6 schedule");
  if(t.onchip_memory_rsp_valid){
   check(m.active&&!m.write&&m.region>=4&&m.region<=12,"onchip immutable ownership");
   check(t.onchip_external_rsp_client==2&&t.onchip_external_rsp_backing_owner==2&&!t.onchip_external_rsp_scalar&&!t.onchip_external_rsp_write&&t.onchip_external_rsp_layer==m.layer&&t.onchip_external_rsp_origin==m.origin&&t.onchip_external_rsp_region==m.region&&t.onchip_external_rsp_tag==m.tag&&t.onchip_external_rsp_word==m.word&&!t.onchip_external_rsp_job&&!t.onchip_external_rsp_session&&!t.onchip_external_rsp_sequence,"onchip immutable complete identity");
   auto data=actual(m);for(unsigned i=0;i<8;i++){check(t.onchip_external_rsp_data[i]==data[i]&&t.up_rsp_data[i]==data[i],"onchip immutable payload");immutable_checks++;}
   if(!m.response_seen){check(clocks==m.due,"first immutable reply N+6");m.response_seen=true;immutable_packets++;}
   if(t.up_rsp_valid&&t.up_rsp_ready)immutable_replies++;
  }
 }
 void onchip_conservation(){
  check(head_requests==368640&&head_replies==head_requests&&O_requests==15360&&O_replies==O_requests,"onchip F64 head/O coverage");
  check(requests-mutable_requests==1947520&&immutable_replies==1947520&&immutable_packets==immutable_replies&&immutable_checks>=immutable_replies*8,"onchip F64 immutable coverage");
  check(head_checks>=head_replies*10&&O_checks>=O_replies*80,"onchip row all-lane coverage");
  std::cout<<"ONCHIP service=encoder_QKV rtl_replies="<<head_replies<<" host_replies=0 mismatches=0"<<std::endl;
  std::cout<<"ONCHIP service=encoder_O rtl_replies="<<O_replies<<" host_replies=0 mismatches=0"<<std::endl;
  std::cout<<"ONCHIP service=encoder_immutable rtl_replies="<<immutable_replies<<" host_replies=0 mismatches=0"<<std::endl;
 }
'''
p=once(p,' void check_layer(){',observe+' void check_layer(){')
p=once(p,'  t.clk=0;drive();t.eval();','  t.clk=0;drive();t.eval();observe_onchip();')
(W/'encoder_services.hpp').write_text(p)
for p in [W/'four_stage.cpp',*W.glob('*.hpp')]:
 for n in moved:assert not re.search(r'\bt\.'+n+r'(?:\[[^]]+\])?\s*=(?!=)',p.read_text()),(p,n)
# Original host headers for other services must remain byte-identical.
for p in S.glob('*.hpp'):
 if p.name!='encoder_services.hpp':assert sha(p)==sha(W/p.name)
c=json.loads((R/'experiments/chip-integration-20261012-Q8-learned-fulltables-lint-generation-control-v2/commands.json').read_text())
for k,args in c.items():
 args[args.index('--top-module')+1]=NEW;args[args.index('--Mdir')+1]=str(RUN/('obj' if k=='generate-full' else 'lint'))
 args += [str(W/(NEW+'.sv'))]+[str(W/f'rv_onchip_{n}_v1.sv') for n in depths]
 if k=='generate-full':
  args[args.index(str(S/'four_stage.cpp'))]=str(W/'four_stage.cpp');i=args.index('-CFLAGS')+1;args[i]=args[i].replace(str(S),str(W))
(W/'no-pch.mk').write_text((R/'overnight-20261014/onchip/no-pch.mk').read_text().replace('rv_allonchip_top_v1',NEW))
c['compile']=['/usr/bin/make','-C',str(RUN/'obj'),'-f',str(W/'no-pch.mk'),'-j6','OPT_FAST=-O3','OPT_SLOW=-O3','CXX=/usr/bin/c++','LINK=/usr/bin/c++','VM_PARALLEL_BUILDS=1']
num=json.loads((R/'experiments/chip-integration-20261012-Q8-learned-fulltables-numerical-run-v2/commands.json').read_text())
oldrun=str(Path.home()/'.local/state/routevoice-internal-runs/20261012/Q8-learned-fulltables-numerical-run-v2/actual')
for k in ['fixture','positive','render']:
 args=num[k]
 if k!='render':args[0]=str(RUN/'obj'/('V'+NEW))
 c[k]=[a.replace(oldrun,str(RUN/'actual')) for a in args]
(W/'commands.json').write_text(json.dumps(c,indent=2)+'\n')
(W/'source-provenance.json').write_text(json.dumps({str(p):sha(p) for p in [S/(OLD+'.sv'),S/'four_stage.cpp',*S.glob('*.hpp')]},indent=2)+'\n')
print('W1b-STATUS: generated 7,604,480 native ROM bytes; all hex roundtrips pass; other-service headers unchanged')
