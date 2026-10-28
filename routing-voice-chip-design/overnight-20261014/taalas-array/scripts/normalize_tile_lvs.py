from pathlib import Path
import json,subprocess,hashlib
W=Path(__file__).resolve().parents[1];R=W.parents[1];O=W/'base'
m=json.loads((O/'tile0-port-map.json').read_text());s=(O/'tile0-extracted-ports.spice').read_text();lines=[];bijection={}
for line in s.splitlines():
    f=line.split()
    if line.startswith('X'):
        for i in range(1,5):
            long=f[i];short=long.rsplit('.',1)[-1]
            assert short not in bijection or bijection[short]==long
            bijection[short]=long;f[i]=short
        line=' '.join(f)
    elif line.startswith('.subckt'):line=' '.join(f[:2]+[n.rsplit('.',1)[-1] for n in f[2:]])
    lines.append(line)
(O/'tile0-extracted-canonical-names.spice').write_text('\n'.join(lines)+'\n')
cmd=[str(next(Path('/nix/store').glob('*netgen*/bin/netgen'))),'-batch','lvs','tile0-extracted-canonical-names.spice W5_TILE0_FLAT','tile0-reference.spice W5_TILE0_FLAT',str(R/'pdks/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl'),'tile0-netgen-canonical.log']
with (O/'commands.jsonl').open('a') as f:f.write(json.dumps(cmd)+'\n')
with (O/'tile0-netgen-canonical-console.log').open('w') as f:subprocess.run(['nice','-n','10']+cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True)
txt=(O/'tile0-netgen-canonical.log').read_text();ok='Circuits match uniquely.' in txt
v=json.loads((O/'verification.json').read_text());v['tile0']['port_promotion_only_lvs_result']=v['tile0']['netgen_lvs'];v['tile0']['netgen_lvs']={'unique_match':ok,'property_errors':'Property errors' in txt,'log':'tile0-netgen-canonical.log','qualified_boundary_view':'tile0-extracted-canonical-names.spice','normalization':'bijective hierarchical label-prefix removal only; no device/property/topology changes','nodes_in_bijection':len(bijection),'prior_failures':['tile0-netgen.log','tile0-netgen-ports.log']}
(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print('W5-STATUS: tile0 canonical-label LVS',ok);assert ok
