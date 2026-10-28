from pathlib import Path
import sys,json,re,hashlib,collections
import numpy as np
B=Path(__file__).resolve().parent;W=B/sys.argv[1];ix=np.load(B.parent/'indices.npy')[:64,:32]
net=(W/'joined.spice').read_text();devices=[];nodes=set()
for l in net.splitlines():
 if l.startswith('X'):
  t=l.split();nodes.update(t[1:5]);devices.append(t)
base=lambda s:s.rsplit('.',1)[-1]
required=['VDD','VSS','PC']+[f'WL{i}' for i in range(64)]+[f'IDX{c}_{b}' for c in range(32) for b in range(4)]+[f'OUT{i}' for i in range(128)]
ports=[]
for n in required:
 found=[x for x in nodes if base(x)==n];assert len(found)==1,(n,found);ports.append(found[0])
def key(d,g,s,b,model,w,l):return (tuple(sorted((d,s))),g,b,model,w,l)
expected=[]
for row in range(64):
 for col in range(32):
  for bit in range(4):
   d=f'IDX{col}_{bit}' if ix[row,col]>>bit&1 else f'OPEN_R{row}_C{col}_B{bit}'
   expected.append(key(d,f'WL{row}','VSS','VSS','nfet_03v3','0.36u','0.28u'))
for i in range(128):
 idx=f'IDX{i//4}_{i%4}';out=f'OUT{i}'
 expected.extend([key(idx,'PC','VDD','VDD','pfet_03v3','1.44u','0.28u'),key(idx,out,'VDD','VDD','pfet_03v3','0.36u','0.28u'),key(out,idx,'VSS','VSS','nfet_03v3','0.36u','0.28u'),key(out,idx,'VDD','VDD','pfet_03v3','0.72u','0.28u')])
actual=[]
for t in devices:
 kv=dict(p.split('=') for p in t[6:]);actual.append(key(*[base(x) for x in t[1:5]],t[5],kv['w'],kv['l']))
a,e=collections.Counter(actual),collections.Counter(expected)
if a!=e:
 (W/'device-mismatch.json').write_text(json.dumps({'missing':list((e-a).items())[:30],'extra':list((a-e).items())[:30]},indent=2));raise AssertionError('Device graph differs; see device-mismatch.json')
for name in ['joined.spice','joined-cap.spice']:
 src=(W/name).read_text();assert '.subckt RV_JOINED_FLAT\n' in src
 (W/name.replace('.spice','-ports.spice')).write_text(src.replace('.subckt RV_JOINED_FLAT\n','.subckt RV_JOINED_FLAT '+' '.join(ports)+'\n'))
r={'checked_devices':len(actual),'array_bit_devices':8192,'receiver_devices':512,'all_device_topology_and_dimensions_match':True,'promoted_unique_ports':len(ports),'port_view_scope':'Only declares exact unique existing extracted node names as subcircuit ports; no merged/renamed nodes or altered device/capacitance connections','independent_lvs':False,'original_spice_sha256':hashlib.sha256((W/'joined.spice').read_bytes()).hexdigest(),'ports':dict(zip(required,ports))}
(W/'topology.json').write_text(json.dumps(r,indent=2)+'\n');print({k:v for k,v in r.items() if k!='ports'})
