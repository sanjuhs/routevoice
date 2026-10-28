from pathlib import Path
from collections import Counter,defaultdict
import sys,json,re,hashlib,numpy as np
W=Path(__file__).resolve().parent;O=W/(sys.argv[1] if len(sys.argv)>1 else 'r320-v1');A=W.parents[2]/'overnight-20261014/taalas-array';meta=json.loads((O/'extraction.json').read_text());H=meta['rows'];b=meta['bank'];g=meta['subbank'];image=np.load(O/'image.npy');assert image.shape==(H,32)
np.save(O/'image.npy',image)
def norm(n):
 n=n.rsplit('.',1)[-1]
 if (m:=re.fullmatch(r'IDX(\d+)_(\d)',n)):return f'IDX{int(m[1])-g*32}_{m[2]}'
 if (m:=re.fullmatch(r'OUT(\d+)',n)):return f'OUT{int(m[1])-g*128}'
 if (m:=re.fullmatch(r'OPEN_R(\d+)_C(\d+)_B(\d)',n)):return f'OPEN_R{m[1]}_C{int(m[2])-g*32}_B{m[3]}'
 assert re.fullmatch(r'(?:WL\d+|VDD|VSS|PC)',n),n
 return n
maps={}
for kind in ['array','joined']:
 out=[];back={};forward={}
 for l in (O/f'{kind}-cap.spice').read_text().splitlines():
  f=l.split()
  if l.startswith(('X','C')):
   end=5 if l.startswith('X') else 3;nodes=[]
   for n in f[1:end]:
    short=norm(n);assert short not in back or back[short]==n,('nonbijective',short);back[short]=n;forward[n]=short;nodes.append(short)
   out.append(' '.join([f[0]]+nodes+f[end:]))
 (O/f'{kind}-canonical.spice').write_text('\n'.join(out)+'\n');maps[kind]={'nodes':len(back),'bijective':len(forward)==len(back)}
def dev(l):
 f=l.split();v=dict(s.lower().split('=') for s in f[6:]);return (tuple(sorted([f[1],f[3]])),f[2],f[4],f[5],float(v['w'].removesuffix('u')),float(v['l'].removesuffix('u')))
expect=[]
for r in range(H):
 for c in range(32):
  for bit in range(4):
   d=f'IDX{c}_{bit}' if int(image[r,c])>>bit&1 else f'OPEN_R{r}_C{c}_B{bit}';expect.append((tuple(sorted([d,'VSS'])),f'WL{r}','VSS','nfet_03v3',.36,.28))
a=Counter(dev(l) for l in (O/'array-canonical.spice').read_text().splitlines() if l.startswith('X'));assert a==Counter(expect)
for i in range(128):
 c,bit=divmod(i,4);bl=f'IDX{c}_{bit}';out=f'OUT{i}'
 for d,gate,s,body,kind,width in [(out,bl,'VSS','VSS','nfet_03v3',.36),(out,bl,'VDD','VDD','pfet_03v3',.72),(bl,out,'VDD','VDD','pfet_03v3',.36),(bl,'PC','VDD','VDD','pfet_03v3',2.88)]:expect.append((tuple(sorted([d,s])),gate,body,kind,width,.28))
j=Counter(dev(l) for l in (O/'joined-canonical.spice').read_text().splitlines() if l.startswith('X'));assert j==Counter(expect),(list((j-Counter(expect)).items())[:2],list((Counter(expect)-j).items())[:2])
report={'array_devices':sum(a.values()),'joined_devices':sum(j.values()),'all_device_connections_and_dimensions_match_real_image_and_pre2_receiver':True,'canonicalization':maps,'row_mapping':'logicalrow=localrow','global_lane_range':[g*32,(g+1)*32],'image_sha256':hashlib.sha256(image.tobytes()).hexdigest()};(O/'topology.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
