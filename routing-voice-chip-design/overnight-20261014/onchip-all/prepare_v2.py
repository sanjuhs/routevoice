"""Close frozen-model input boundary, preserving every v1 design/host file."""
from pathlib import Path
import hashlib,json,re
W=Path(__file__).resolve().parent;R=W.parents[1];H=W/'host-v2'
RUN=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-all';FIX=Path.home()/'.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3'
H.mkdir(exist_ok=True);(RUN/'v2').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
v1pins=json.loads((W/'build-input-pins.json').read_text())
for p,h in v1pins.items():assert sha(Path(p))==h,p
contract=FIX/'producer/real-domain-contract.json';c=json.loads(contract.read_text());metadata=FIX/'producer/metadata.txt'
assert [int(x) for x in metadata.read_text().split()]==[c['position_scale_bits'],c['position_zero']]==[1012345286,123]
position_header='taalas_adapter_session_compact_token_services_f500_v1.hpp';p=(W/position_header).read_text()
assert 't.source_start_position_scale=pscale;t.source_start_position_zero=pzero;t.source_start_position_offset=0;' in p
prod=(W/'producer_services.hpp').read_text();m=re.search(r'const uint32_t image\[8\]=\{([^}]+)\};',prod);assert m
words=[int(x.strip(),16) for x in m.group(1).split(',')];image=sum(x<<(32*i) for i,x in enumerate(words));image_hex=f'{image:064x}'
barrier=R/'rtl/taalas_compact_history_token_barrier_q1.sv';consumer=R/'experiments/chip-integration-20261012-routevoice-remaining-widths-v1/taalas_compact_history_layer_self_o_q1.sv'
for f in [barrier,consumer]:assert "MODEL_IMAGE_ID=256'h"+image_hex in f.read_text()
assert 'setup_fault<=setup_image_id==MODEL_IMAGE_ID?0:16\'h0001;' in barrier.read_text()
constants={'source_start_position_scale':(32,1012345286),'source_start_position_zero':(8,123),'source_start_position_offset':(12,0),'compact_setup_image_id':(256,image)}
v1=W/'rv_allonchip_top_all_v1.sv';v2=W/'rv_allonchip_top_all_v2.sv';old=v1.read_text();s=once(old,'module rv_allonchip_top_all_v1(','module rv_allonchip_top_all_v2(');removed=[];params=[]
for n,(width,value) in constants.items():
 line=f'  input wire [{width-1}:0] {n},\n';s=once(s,line,'');removed.append(line)
 param='FROZEN_'+n.upper();params.append(f'localparam logic [{width-1}:0] {param} = {width}\'h{value:0{(width+3)//4}x};')
 s=once(s,f'.{n}({n})',f'.{n}({param})')
localparams='// Frozen model constants; no runtime parameter inputs.\n'+'\n'.join(params)+'\n'
s=s.replace('\n);\n','\n);\n'+localparams,1);v2.write_text(s)
# Mechanically prove that only module name, four input declarations and four
# constant connections differ from v1; every other byte of RTL is retained.
expected=old.replace('module rv_allonchip_top_all_v1(','module rv_allonchip_top_all_v2(')
for line in removed:expected=expected.replace(line,'')
for n in constants:expected=expected.replace(f'.{n}({n})',f'.{n}(FROZEN_{n.upper()})')
expected=expected.replace('\n);\n','\n);\n'+localparams,1);assert s==expected
for f in W.glob('*.hpp'):(H/f.name).write_bytes(f.read_bytes())
host=(W/'four_stage.cpp').read_text().replace('Vrv_allonchip_top_all_v1','Vrv_allonchip_top_all_v2')
for n in constants:
 host=once(host,('for(unsigned i=0;i<8;i++)' if n=='compact_setup_image_id' else '')+'t.'+n+('[i]' if n=='compact_setup_image_id' else '')+'=0;','')
(H/'four_stage.cpp').write_text(host)
p=once(p,'t.source_start_position_scale=pscale;t.source_start_position_zero=pzero;t.source_start_position_offset=0;','')
p=once(p,'t.source_start_tag=sid;', 'h.check(pscale==1012345286u&&pzero==123u,"v2 frozen position domain unchanged");\n  t.source_start_tag=sid;')
(H/position_header).write_text(p)
prod=once(prod,'for(unsigned i=0;i<8;i++)t.compact_setup_image_id[i]=image[i];','// Model image identity is tied inside v2. Keep its independent host binding check.\n  const uint32_t frozen_image[8]={'+','.join(f'0x{x:08x}u' for x in words)+'};\n  for(unsigned i=0;i<8;i++)check(image[i]==frozen_image[i],"v2 frozen model image unchanged");')
(H/'producer_services.hpp').write_text(prod)
for f in [H/'four_stage.cpp',*H.glob('*.hpp')]:
 for n in constants:assert not re.search(r'\bt\.'+n+r'\b',f.read_text()),(f,n)
# All other header contents must be byte-identical; original assertions retained.
for f in W.glob('*.hpp'):
 if f.name not in [position_header,'producer_services.hpp']:assert f.read_bytes()==(H/f.name).read_bytes()
commands=json.loads((W/'commands.json').read_text());commands={k:commands[k] for k in ['lint-full','generate-full','compile','fixture','positive','compare','render']}
for key,args in commands.items():
 for i,arg in enumerate(args):
  arg=arg.replace('rv_allonchip_top_all_v1','rv_allonchip_top_all_v2').replace(str(RUN/'obj'),str(RUN/'v2/obj')).replace(str(RUN/'actual'),str(RUN/'v2/actual'))
  arg=arg.replace(str(W/'four_stage.cpp'),str(H/'four_stage.cpp')).replace('-I'+str(W),'-I'+str(H)).replace(str(W/'no-pch.mk'),str(W/'no-pch-v2.mk')).replace(str(W/'compare_outputs.py'),str(W/'compare_outputs_v2.py'))
  args[i]=arg
(W/'commands-v2.json').write_text(json.dumps(commands,indent=2)+'\n')
(W/'no-pch-v2.mk').write_text((W/'no-pch.mk').read_text().replace('rv_allonchip_top_all_v1','rv_allonchip_top_all_v2'))
runner=(W/'run_stage.py').read_text().replace("20261014/onchip-all'","20261014/onchip-all/v2'").replace('commands.json','commands-v2.json').replace("WORK/'logs'","WORK/'logs-v2'").replace("WORK/'f64.lock'","WORK/'f64-v2.lock'")
# Guard has 1 GiB margin over the user's new 22 GiB minimum.
runner=runner.replace('22*1024**3','23*1024**3').replace('fewer than 22 GiB','fewer than 23 GiB').replace('below 22 GiB','below 23 GiB').replace('20 GiB floor','22 GiB floor')
(W/'run_stage_v2.py').write_text(runner)
compare=(W/'compare_outputs.py').read_text().replace('20261014/onchip-all/actual','20261014/onchip-all/v2/actual').replace("WORK/'logs'","WORK/'logs-v2'").replace('comparison-result.json','comparison-result-v2.json')
(W/'compare_outputs_v2.py').write_text(compare)
original_inputs=json.loads((W/'port-audit.json').read_text())['remaining_inputs']
resets=set('frontend_por_reset table_por_reset producer_por_reset history_por_reset reset learned_por_reset bank_por_reset'.split())
metadata_names=set('up_start_tag up_pcm_tag up_pcm_index compact_setup_session source_start_tag begin_job_tag begin_session begin_source_tag begin_token_tag_base begin_frames'.split())
rows=[]
for n in original_inputs:
 category='model constant' if n in constants else 'reset' if n in resets else 'audio data' if n=='up_pcm_value' else 'job metadata' if n in metadata_names else 'control-handshake'
 rows.append(dict(input=n,classification=category,v2_action='internal localparam; removed from ports' if n in constants else 'retained'))
assert len(rows)==35 and sum(x['classification']=='model constant' for x in rows)==4
source_inputs={str(f):sha(f) for f in [v1,W/'four_stage.cpp',W/'producer_services.hpp',W/position_header,contract,metadata,barrier,consumer]}
record=dict(passed=True,constants={n:dict(width_bits=w,value_hex=f'{v:x}',value_decimal=str(v)) for n,(w,v) in constants.items()},image_id_evidence='Constant MODEL_IMAGE_ID equality check in token barrier; setup_session is the separately latched per-job ID.',input_classification=rows,remaining_inputs=31,remaining_model_constant_inputs=0,rtl_change_assertion='Exact v1 text after only module rename, four input removals, four localparams and corresponding binding substitutions.',sources=source_inputs,unchanged_v1_pins=v1pins)
(W/'input-audit-v2.json').write_text(json.dumps(record,indent=2)+'\n')
for f,h in v1pins.items():assert sha(Path(f))==h,f
print('W1-STATUS: v2 prepared; four model inputs internalized, 31 runtime inputs classified; v1 pins unchanged')
