"""Verify v2 boundary and retained v1 pins; pin direct build inputs and ROMs."""
from pathlib import Path
import hashlib,json,re,sys
W=Path(__file__).resolve().parent;RUN=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-all/v2';H=W/'host-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((W/'input-audit-v2.json').read_text())
for p,h in d['unchanged_v1_pins'].items():assert sha(Path(p))==h,p
for p,h in d['sources'].items():assert sha(Path(p))==h,p
s=(W/'rv_allonchip_top_all_v2.sv').read_text();header=s[:s.index('\n);')];ports=re.findall(r'input wire\s*(?:\[[^]]+\])?\s*(\w+)',header)
assert set(ports)=={x['input'] for x in d['input_classification'] if x['classification']!='model constant'} and len(ports)==31
for n,c in d['constants'].items():
 assert n not in ports
 value=int(c['value_decimal']);width=c['width_bits'];param='FROZEN_'+n.upper()
 assert f"localparam logic [{width-1}:0] {param} = {width}'h{value:0{(width+3)//4}x};" in s
 assert f'.{n}({param})' in s
 for p in [H/'four_stage.cpp',*H.glob('*.hpp')]:assert not re.search(r'\bt\.'+n+r'\b',p.read_text()),(p,n)
v1=(W/'rv_allonchip_top_all_v1.sv').read_text();expected=v1.replace('module rv_allonchip_top_all_v1(','module rv_allonchip_top_all_v2(')
for n,c in d['constants'].items():
 expected=expected.replace(f"  input wire [{c['width_bits']-1}:0] {n},\n",'').replace(f'.{n}({n})',f'.{n}(FROZEN_{n.upper()})')
expected=expected.replace('\n);\n','\n);\n'+s[s.index('// Frozen model constants;'):s.index('rv_pcm_encoder_greedy_frontend_history_producer_metadata_KV_tables_onboard_v1 original')],1)
assert s==expected,'Unapproved RTL changes beyond constant closure'
manifest=json.loads((W/'rom-manifest.json').read_text())
for x in manifest['outputs']:assert sha(Path(x['path']))==x['sha256']
headerfile=RUN/'obj/Vrv_allonchip_top_all_v2.h'
if headerfile.exists():
 g=headerfile.read_text();geninputs=re.findall(r'VL_IN\w*\(&([^,]+),',g)
 assert set(geninputs)==set(ports)
 for n in d['constants']:assert n not in geninputs
paths=set()
for arg in json.loads((W/'commands-v2.json').read_text())['generate-full']:
 p=Path(arg)
 if p.is_absolute() and p.is_file() and p.suffix in ['.sv','.v','.cpp']:paths.add(p)
paths.update(H.glob('*.hpp'))
paths.update(W/n for n in ['prepare_v2.py','audit_v2.py','run_stage_v2.py','compare_outputs_v2.py','commands-v2.json','no-pch-v2.mk','input-audit-v2.json'])
pins={str(p):sha(p) for p in sorted(paths)}
if '--verify-pins' in sys.argv:assert pins==json.loads((W/'build-input-pins-v2.json').read_text()),'v2 input changed'
else:(W/'build-input-pins-v2.json').write_text(json.dumps(pins,indent=2)+'\n')
print(f'V2_BOUNDARY_AUDIT_PASS removed_model_inputs=4 runtime_inputs=31 model_constant_inputs=0 v1_pins_unchanged={len(d["unchanged_v1_pins"])} v2_build_pins={len(pins)}')
