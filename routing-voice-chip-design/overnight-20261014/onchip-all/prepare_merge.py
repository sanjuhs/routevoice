"""Merge reviewed worker sources read-only; regenerate all ROMs from frozen binaries."""
from pathlib import Path
import hashlib,json,re,shutil
W=Path(__file__).resolve().parent
R=W.parents[1]; A=W.parent/'onchip'; B=W.parent/'onchip-enc'; C=W.parent/'onchip-front'
S=R/'experiments/chip-integration-20261012-frontend-learned-norm-connected-source-v3'
RUN=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-all'
OLD='rv_pcm_encoder_greedy_frontend_history_producer_metadata_KV_tables_onboard_v1'; NEW='rv_allonchip_top_all_v1'
FIX=Path.home()/'.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3'
RUN.mkdir(parents=True,exist_ok=True); (W/'rom').mkdir(exist_ok=True)
inputs={}; outputs=[]; sources={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 p=Path(p); inputs[str(p)]={'bytes':p.stat().st_size,'sha256':sha(p)};return p.read_bytes()
def source(p):
 sources[str(p)]={'bytes':p.stat().st_size,'sha256':sha(p)};return p.read_text()
def emit(name,data,width,previous):
 n=width//8;assert len(data)%n==0
 p=W/'rom'/f'{name}.hex';p.write_text(''.join(data[i:i+n][::-1].hex()+'\n' for i in range(0,len(data),n)))
 assert b''.join(int(x,16).to_bytes(n,'little') for x in p.read_text().splitlines())==data
 assert sha(p)==sha(Path(previous)),name
 outputs.append(dict(name=name,path=str(p),native_bytes=len(data),width_bits=width,words=len(data)//n,sha256=sha(p),roundtrip_pass=True,worker_output=str(previous)))
for worker in [A,C]:
 for d in json.loads(source(worker/'rom-manifest.json')):
  emit(Path(d['output']).stem,read(d['input']),d['width_bits'],d['output'])
fields=read(FIX/'encoder/inputs.txt').decode().split();pos=0;head=bytearray();omat=bytearray();mem=bytearray()
for layer in range(6):
 weight=read(fields[pos]);assert len(weight)==409600
 for role in range(3):
  for h in range(8):
   for row in range(320):
    off=(role*25600+row*80+h*10)*4;head.extend(weight[off:off+40])
 omat.extend(weight[3*25600*4:])
 images={r:fields[pos+1+j] for j,r in enumerate([7,15,16,17,18,21,20,19,8,9,10,14])}
 for r in [7,21,20,15,16,17,18]:mem.extend(read(images[r]))
 pos+=25
mem.extend(read(fields[pos+1]))
for name,data,width in [('encoder_head',head,320),('encoder_O',omat,2560),('encoder_memory',mem,256)]:emit(name,data,width,B/'rom'/f'{name}.hex')
assert sum(x['native_bytes'] for x in outputs)==28641280
(W/'rom-manifest.json').write_text(json.dumps(dict(inputs=inputs,outputs=outputs,native_bytes=28641280),indent=2)+'\n')
def repaths(s):
 for worker in [A,B,C]:
  s=s.replace(str(Path.home()/'.local/state/routevoice-internal-runs/20261014'/worker.name/'rom'),str(W/'rom'))
  s=s.replace(str(worker/'rom'),str(W/'rom'))
 return s
modules=[]
for worker,pattern in [(A,'rv_onchip_*.sv'),(B,'rv_onchip_*.sv'),(C,'rv_onchip_*.sv'),(C,'rv_source_position_immutable_rom_v1.sv')]:
 for p in worker.glob(pattern):
  (W/p.name).write_text(repaths(source(p)));modules.append(p.name)
for p in A.glob('*.hpp'):(W/p.name).write_text(source(p))
for worker,name in [(B,'encoder_services.hpp'),(C,'frontend_services.hpp'),(C,'taalas_adapter_session_compact_token_services_f500_v1.hpp')]: (W/name).write_text(source(worker/name))
# Use frontend host copy for conservation, combine encoder call and remove all moved initializers.
host=source(C/'four_stage.cpp').replace('rv_allonchip_top_w1c',NEW)
host=host.replace('p.learned_conservation();f.frontend_conservation();','e.onchip_conservation();p.learned_conservation();f.frontend_conservation();')
(W/'four_stage.cpp').write_text(host)
# Parse each worker's expanded ANSI ports, union direction changes only.
def ports(s):
 header=s[s.index('(\n')+2:s.index('\n);')];ret={}
 for line in header.splitlines():
  line=line.split('//')[0].strip().rstrip(',')
  if not line:continue
  m=re.fullmatch(r'(input|output) wire\s*(\[[^]]+\])?\s*(.*)',line);assert m,line
  d,w,ns=m.groups()
  for n in ns.split(','):ret[n.strip()]=(d,w or '')
 return ret
original=ports(source(S/f'{OLD}.sv')); moved=set()
for worker,top in [(A,'rv_allonchip_top_v1'),(B,'rv_allonchip_top_w1b'),(C,'rv_allonchip_top_w1c')]:
 wp=ports(source(worker/f'{top}.sv'))
 moved.update(n for n,(d,w) in original.items() if d=='input' and wp[n][0]=='output')
moved.update(n for n,(d,w) in original.items() if d=='input' and n.startswith('external_'))
for p in [W/'four_stage.cpp',*W.glob('*.hpp')]:
 s=p.read_text()
 for n in moved:
  # All remaining moved assignments are scalar constants or initialization loops.
  s=re.sub(r'(?:for\(unsigned i=0;i<(?:8|10|80);i\+\+\))?t\.'+re.escape(n)+r'(?:\[i\])?=[01];','',s)
 s=s.replace('t.onchip_external_','t.external_').replace('t.w1c_external_','t.external_')
 if p.name=='encoder_services.hpp':
  s=s.replace('check(!t.external_req_valid,"encoder immutable request escaped onchip route");','check(!t.onchip_route_fault,"merged immutable route fault");')
  s=s.replace('  std::cout<<"ONCHIP service=encoder_QKV rtl_replies="<<head_replies<<" host_replies=0 mismatches=0"<<std::endl;\n  std::cout<<"ONCHIP service=encoder_O rtl_replies="<<O_replies<<" host_replies=0 mismatches=0"<<std::endl;', '  std::cout<<"ONCHIP service=encoder_QKV_O rtl_replies="<<(head_replies+O_replies)<<" host_replies=0 mismatches=0"<<std::endl;')
 if p.name=='frontend_services.hpp':s=s.replace('!t.onchip_frontend_fault&&!t.external_rsp_valid','!t.onchip_frontend_fault&&!t.onchip_route_fault')
 for n in moved:assert not re.search(r'\bt\.'+re.escape(n)+r'(?:\[[^]]*\])?\s*=(?!=)',s),(p,n)
 p.write_text(s)
# Original top connected directly to output-only debug buses.
extra=['onchip_body_fault','onchip_self_fault','onchip_head_fault','onchip_O_fault','onchip_memory_fault','onchip_memory_idle','onchip_memory_rsp_valid','onchip_frontend_fault','onchip_position_rejected','w1c_front_select','w1c_front_idle','w1c_front_rsp_valid','onchip_route_fault']
sv='// All six fixed-weight services internal. Original recognizer source unchanged.\nmodule '+NEW+'(\n'
sv+=',\n'.join(f'  {"output" if n in moved else d} wire {w} {n}' for n,(d,w) in original.items())+',\n'
sv+=',\n'.join('  output wire '+n for n in extra)+'\n);\n'
sv+=OLD+' original (\n'+',\n'.join(f' .{n}({n})' for n in original)+'\n);\n'
a=source(A/'rv_allonchip_top_v1.sv');sv+=a[a.index('  rv_onchip_decoder_body_v1'):a.rindex('endmodule')]
b=source(B/'rv_allonchip_top_w1b.sv');sv+=b[b.index('rv_onchip_encoder_head_v1'):b.index('wire encoder_select')]
c=source(C/'rv_allonchip_top_w1c.sv');sv+=repaths(c[c.index(' rv_source_position_immutable_rom_v1 #'):c.rindex('endmodule')])
identity={n.removeprefix('external_rsp_'):w for n,(d,w) in original.items() if n.startswith('external_rsp_') and n not in ['external_rsp_valid','external_rsp_ready']}
sv+='wire encoder_select = external_req_client==2 && external_req_backing_owner==2 && external_req_region>=4 && external_req_region<=12;\n'
sv+='assign w1c_front_select=external_req_client==0 && (external_req_region==0 || external_req_region==1 || external_req_region==4 || external_req_region==5 || external_req_region==8);\n'
sv+='assign onchip_route_fault=(external_req_valid && !(encoder_select || w1c_front_select)) || (onchip_memory_rsp_valid && w1c_front_rsp_valid);\n'
sv+='wire memory_ready, front_ready;\nassign external_idle=onchip_memory_idle && w1c_front_idle;\n'
sv+='assign external_req_ready=encoder_select ? (memory_ready && w1c_front_idle) : (w1c_front_select && front_ready && onchip_memory_idle);\n'
sv+='assign external_rsp_valid=onchip_memory_rsp_valid || w1c_front_rsp_valid;\n'
for n,w in identity.items():
 sv+=f'wire {w} memory_{n},front_{n};\nassign external_rsp_{n}=w1c_front_rsp_valid ? front_{n} : memory_{n};\n'
for mod,inst,pre,valid,ready,idle,fault,por,req,rspready in [
 ('rv_onchip_encoder_memory_v1','encoder_memory','memory','onchip_memory_rsp_valid','memory_ready','onchip_memory_idle','onchip_memory_fault','bank_por_reset','external_req_valid && encoder_select && w1c_front_idle','external_rsp_ready && !w1c_front_rsp_valid'),
 ('rv_onchip_frontend_v1','frontend_rom','front','w1c_front_rsp_valid','front_ready','w1c_front_idle','onchip_frontend_fault','frontend_por_reset','external_req_valid && w1c_front_select && onchip_memory_idle','external_rsp_ready')]:
 conn=dict(clk='clk',por_reset=por,warm_reset='reset',req_valid=req,req_ready=ready,idle=idle,fault=fault,rsp_valid=valid,rsp_ready=rspready)
 for n in identity:
  if n!='data':conn['req_'+n]='external_req_'+n
  conn['rsp_'+n]=pre+'_'+n
 sv+=mod+' '+inst+'(\n'+',\n'.join(f' .{a}({b})' for a,b in conn.items())+'\n);\n'
sv+='endmodule\n';(W/f'{NEW}.sv').write_text(sv)
(W/'port-audit.json').write_text(json.dumps(dict(moved_inputs_to_debug_outputs=sorted(moved),remaining_inputs=[n for n,(d,w) in original.items() if d=='input' and n not in moved],host_drives_moved_outputs=0),indent=2)+'\n')
# Independent worker tests retained under unique filenames.
for worker,name,new in [(A,'responder_test.cpp','decoder_test.cpp'),(B,'responder_test.cpp','encoder_test.cpp'),(C,'responder_test.cpp','frontend_test.cpp'),(C,'tb_source_position_immutable_rom_v1.sv','tb_source_position_immutable_rom_v1.sv')]: (W/new).write_text(repaths(source(worker/name)))
commands=json.loads(source(A/'commands-a.json'))
def relocate(cmd,worker):
 ret=[]
 for x in cmd:
  x=x.replace(str(Path.home()/'.local/state/routevoice-internal-runs/20261014'/worker.name),str(RUN)).replace(str(worker),str(W))
  x=x.replace('rv_allonchip_top_v1',NEW).replace('/obj-a','/obj').replace('/actual-a','/actual')
  if x.endswith('/responder_test.cpp'):x=str(W/({'onchip':'decoder_test.cpp','onchip-enc':'encoder_test.cpp','onchip-front':'frontend_test.cpp'}[worker.name]))
  ret.append(x)
 return ret
commands={k:relocate(v,A) for k,v in commands.items()}
for key in ['lint-full','generate-full']:
 commands[key]+=[str(W/n) for n in modules if 'decoder_' not in n]
for worker,prefix in [(B,'test-'),(C,'unit-')]:
 for k,v in json.loads(source(worker/'commands.json')).items():
  if k.startswith(prefix):commands[k]=relocate(v,worker)
(W/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
(W/'no-pch.mk').write_text(source(A/'no-pch.mk').replace('rv_allonchip_top_v1',NEW))
s=source(A/'run_stage.py').replace("20261014/onchip'","20261014/onchip-all'").replace('commands-a.json','commands.json').replace('actual-a','actual')
start=s.index('    processes = subprocess.check_output');end=s.index("    actual = RUN/",start)
s=s[:start]+s[end:];s=s.replace('# OS advisory lock: at most one W1 F64 runner, plus check other recognizable F64 runners.','# Own merged-run lock only; user explicitly authorizes concurrent worker positives.')
(W/'run_stage.py').write_text(s)
s=source(A/'compare_outputs.py').replace('20261014/onchip/actual-a','20261014/onchip-all/actual')
s=s.replace("('decoder_self',787200)","('decoder_self',787200), ('encoder_QKV_O',384000), ('encoder_immutable',1947520), ('frontend_immutable',55720960), ('producer_positions',2560)")
s=s.replace("assert {p.name", "assert 'common_clocks=312578649' in log\nassert {p.name")
(W/'compare_outputs.py').write_text(s)
(W/'source-provenance.json').write_text(json.dumps(sources,indent=2)+'\n')
print('W1-STATUS: merged seven responders / six services, 28,641,280 native ROM bytes; no host fixed-service input ports or writes')
commands['unit-position-exhaustive-build']=[commands['unit-body-build'][0],'--cc','--exe','--build','-j','2','-Wno-fatal','--top-module','rv_source_position_immutable_rom_v1','--Mdir',str(RUN/'unit-position-exhaustive'),'-GIMAGE_FILE="'+str(W/'rom/positions.hex')+'"',str(W/'rv_source_position_immutable_rom_v1.sv'),str(W/'position_test.cpp'),'-CFLAGS','-std=c++17 -O2']
position_input=next(x['input'] for x in json.loads((C/'rom-manifest.json').read_text()) if x.get('service')=='positions')
commands['unit-position-exhaustive']=[str(RUN/'unit-position-exhaustive/Vrv_source_position_immutable_rom_v1'),position_input]
(W/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
