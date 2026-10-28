from pathlib import Path
import re,json,numpy as np
W=Path(__file__).resolve().parent;A=W.parents[1];R=A.parents[1];O=W/'v1'
def parse(p):
 s=re.sub(r'\n\+\s*',' ',p.read_text());out={};name=None
 for l in s.splitlines():
  f=l.split()
  if not f:continue
  if f[0].lower()=='.subckt':name=f[1];out[name]=(f[2:],[])
  elif f[0].lower()=='.ends':name=None
  elif name and f[0][0].lower()=='x':out[name][1].append(f)
 return out
hd=parse(A/'periphery/handoff-v2/w5_row_decoder.spice');lib=parse(R/'pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/spice/gf180mcu_fd_sc_mcu7t5v0.spice')
ports=['VDD','VSS','PC','EVAL']+[f'ROW{i}' for i in range(6)]+[f'OUT{i}' for i in range(1280)]
lines=['* Independent real image and receiver design; decoder handoff connectivity expanded with official GF180 transistor library','.subckt W5_DECODED_TILE_FLAT '+' '.join(ports)]
idx=np.load(A/'indices.npy')
for r in range(64):
 for c in range(320):
  for b in range(4):
   drain=f'IDX{c}_{b}' if (int(idx[r,c])>>b)&1 else f'OPEN_R{r}_C{c}_B{b}'
   lines.append(f'Xa{r}_{c}_{b} {drain} WL_G{c//32}_R{r} VSS VSS nfet_03v3 w=0.36u l=0.28u')
for i in range(1280):
 c,b=divmod(i,4);bl=f'IDX{c}_{b}';out=f'OUT{i}'
 for name,d,g,s,body,kind,w in [('n',out,bl,'VSS','VSS','nfet_03v3',.36),('p',out,bl,'VDD','VDD','pfet_03v3',.72),('k',bl,out,'VDD','VDD','pfet_03v3',.36),('pc',bl,'PC','VDD','VDD','pfet_03v3',1.44)]:lines.append(f'X{name}{i} {d} {g} {s} {body} {kind} w={w}u l=0.28u')
count=0
for group in range(10):
 def decnode(n):
  if n in ['VDD','VSS']:return n
  if n=='enable':return 'EVAL'
  if n.startswith('row['):return 'ROW'+n[4:-1]
  if n.startswith('wordline['):return f'WL_G{group}_R'+n[9:-1]
  return f'D{group}_'+n
 for f in hd['w5_row_decoder'][1]:
  typ=f[-1];pn,body=lib[typ];hpn=hd[typ][0];mapping=dict(zip(hpn,[decnode(n) for n in f[1:-1]]));assert len(hpn)==len(f)-2
  if 'VNW' not in mapping:mapping['VNW']=mapping['VDD']
  if 'VPW' not in mapping:mapping['VPW']=mapping['VSS']
  def cn(n):return mapping.get(n,f'D{group}_{f[0]}_'+n)
  for t in body:
   assert t[5] in ['nfet_05v0','pfet_05v0'],t
   lines.append(' '.join([f'XD{group}_{f[0]}_{t[0]}']+[cn(n) for n in t[1:5]]+t[5:]));count+=1
lines.append('.ends W5_DECODED_TILE_FLAT');(O/'reference.spice').write_text('\n'.join(lines)+'\n');(O/'reference.json').write_text(json.dumps({'array_receiver_devices':87040,'decoder_devices':count,'total_devices':87040+count,'ports':len(ports)},indent=2));print(count)
