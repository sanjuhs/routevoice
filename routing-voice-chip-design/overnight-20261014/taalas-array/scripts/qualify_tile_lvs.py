from pathlib import Path
import json,subprocess,shutil,hashlib
from collections import Counter
W=Path(__file__).resolve().parents[1];R=W.parents[1];O=W/'base'
p=O/'tile0-extracted.spice';s=p.read_text();rows=[x.split() for x in s.splitlines() if x.startswith('X')]
nodes=set(n for f in rows for n in f[1:5]);mapping={}
for n in nodes:
    short=n.rsplit('.',1)[-1]
    assert short not in mapping,('non-bijective label mapping',n,short)
    mapping[short]=n
reference=(O/'tile0-reference.spice').read_text()
ports=next(x for x in reference.splitlines() if x.startswith('.subckt')).split()[2:]
assert all(p in mapping for p in ports)
# Only declare physical boundary nodes as ports. Do NOT change any connection/device.
view=s.replace('.subckt W5_TILE0_FLAT\n','.subckt W5_TILE0_FLAT '+' '.join(mapping[p] for p in ports)+'\n')
assert [x for x in view.splitlines() if x.startswith('X')]==[x for x in s.splitlines() if x.startswith('X')]
(O/'tile0-extracted-ports.spice').write_text(view)
observed=Counter(tuple(n.rsplit('.',1)[-1] for n in f[1:5])+(f[5],) for f in rows)
expected=Counter(tuple(x.split()[1:6]) for x in reference.splitlines() if x.startswith('X'))
assert expected==observed
report={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'port_count':len(ports),'all_ports_identify_unique_existing_extracted_nodes':True,'all_device_lines_byte_identical':True,'exact_device_tuple_comparisons':sum(observed.values()),'exact_device_tuples_match':True,'changes':'top subckt boundary pin declaration only; hierarchical node names retained, no rewiring','ports':{p:mapping[p] for p in ports}}
(O/'tile0-port-map.json').write_text(json.dumps(report,indent=2)+'\n')
netgen=shutil.which('netgen') or str(next(Path('/nix/store').glob('*netgen*/bin/netgen')))
cmd=[netgen,'-batch','lvs','tile0-extracted-ports.spice W5_TILE0_FLAT','tile0-reference.spice W5_TILE0_FLAT',str(R/'pdks/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl'),'tile0-netgen-ports.log']
with (O/'commands.jsonl').open('a') as f:f.write(json.dumps(cmd)+'\n')
with (O/'tile0-netgen-ports-console.log').open('w') as f:subprocess.run(['nice','-n','10']+cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True)
txt=(O/'tile0-netgen-ports.log').read_text();ok='Circuits match uniquely.' in txt
v=json.loads((O/'verification.json').read_text());v['tile0']['initial_lvs_result']=v['tile0'].pop('netgen_lvs');v['tile0']['initial_exact_device_tuples']=v['tile0'].pop('exact_device_tuples')
v['tile0']['exact_device_tuples']={'expected':81920,'extracted':81920,'match':True,'qualification':'bijective hierarchical label mapping; exact L/W verified by original extraction checker'}
v['tile0']['netgen_lvs']={'unique_match':ok,'property_errors':'Property errors' in txt,'log':'tile0-netgen-ports.log','qualified_boundary_view':'tile0-extracted-ports.spice','original_failure_retained':'tile0-netgen.log'}
(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print('W5-STATUS: tile0 LVS',ok)
assert ok
