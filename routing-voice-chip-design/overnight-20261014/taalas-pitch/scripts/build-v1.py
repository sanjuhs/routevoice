"""W6 native-pitch array, eight staggered rows of retained pre2 receivers."""
from pathlib import Path
import argparse,os,sys,json,hashlib,shutil
sys.dont_write_bytecode=True
import numpy as np
import klayout.db as k
W=Path(__file__).resolve().parents[1]; R=W.parents[1]; A=W.parent/'taalas-array'
p=argparse.ArgumentParser();p.add_argument('--rows',type=int,choices=[64,320,1280],required=True);p.add_argument('--revision',default='v1');args=p.parse_args()
H=args.rows;O=W/f'r{H}-{args.revision}';O.mkdir(exist_ok=False)
assert shutil.disk_usage('/').free>=22.3*2**30
idx=np.load(A/'indices.npy')[:H];L=k.Layout();L.dbu=.001
AX=10.;AY=126.;DX=100.;RP=14.4
layers={'m1':34,'via1':35,'m2':36,'via2':38,'m3':42,'via3':40,'m4':46,'via4':41,'m5':81}
def rect(c,l,x1,y1,x2,y2):c.shapes(L.layer(layers[l],0)).insert(k.DBox(x1,y1,x2,y2))
def sq(c,l,x,y,w=.38):rect(c,l,x-w/2,y-w/2,x+w/2,y+w/2)
def label(c,l,n,x,y):c.shapes(L.layer(layers[l],10)).insert(k.DText(n,k.DTrans(x,y)))
def inst(c,s,x=0,y=0):c.insert(k.CellInstArray(s.cell_index(),k.Trans(round(x*1000),round(y*1000))))
def copy(c,name):c.name=name;d=L.create_cell(name);d.copy_tree(c);return d
basepath=R/'experiments/taalas-access/mask-index-tall/generate_layout.py';recvpath=basepath.parent/'receiver-pre2/generate_layout.py'
os.environ['TAALAS_ARRAY_ROWS']=str(H);os.environ['TAALAS_ARRAY_COLS']='32'
s=basepath.read_text().replace('import pya','import klayout.db as pya');s=s[:s.index('layout.write(')].replace('code=code_for(row,output)','code=0')
ns={'__file__':str(O/'reused-base.py')};exec(compile(s,str(basepath),'exec'),ns)
for li in list(ns['layout'].layer_indices()):
 if ns['layout'].get_info(li).datatype==10:ns['cell'].shapes(li).clear()
base=copy(ns['cell'],f'PITCH_BASE_R{H}');end_y=ns['end_y'];center=ns['center']
T=L.create_cell(f'PITCH_BANK_R{H}');routes=[]
for g in range(10):
 arr=L.create_cell(f'PITCH_ARRAY_R{H}_G{g:02d}');inst(arr,base)
 label(arr,'m2','VSS',.5,.6)
 for bc in range(128):label(arr,'m2',f'IDX{32*g+bc//4}_{bc%4}',center(bc),.6)
 for row in range(H):
  y=2+row*1.44+(row//8)*1.8+.98
  label(arr,'m3',f'WL{row}',1.1,y-.08)
  for bc in range(128):
   x=center(bc);c,bit=divmod(bc,4)
   if int(idx[row,32*g+c])>>bit&1:sq(arr,'via1',x,y,.26)
   else:label(arr,'m1',f'OPEN_R{row}_C{32*g+c}_B{bit}',x,y)
 s=recvpath.read_text().replace('import pya','import klayout.db as pya');s=s[:s.index('layout.write(')]
 s=s.replace('oy=row*11.84','oy=row*14.4').replace('55.7','91.4').replace('94.41','112.33')
 s=s.replace('x=col*3.5;i=row*16+col','x=(col//2)*11.56+(col%2)*5.28;i=col*8+row')
 s=s.replace("f'IDX{i}'","f'IDX{32*group+i//4}_{i%4}'").replace("f'OUT{i}'","f'OUT{128*group+i}'")
 nr={'__file__':str(O/'reused-receiver.py'),'group':g};exec(compile(s,str(recvpath),'exec'),nr)
 recv=copy(nr['cell'],f'PITCH_RECEIVER_G{g:02d}')
 sub=L.create_cell(f'PITCH_JOINED_R{H}_G{g:02d}');inst(sub,arr,AX,AY);inst(sub,recv,AX,0)
 for bc in range(128):
  row=bc%8;col=bc//8;oy=row*RP;x=AX+center(bc);rx=AX+(col//2)*11.56+(col%2)*5.28+2.24;y=oy+12.5;top_y=AY-1
  rect(sub,'m2',x-.19,top_y-.19,x+.19,AY+.69)
  for lay in ['m3','m4']:sq(sub,lay,x,top_y)
  for lay in ['via2','via3']:sq(sub,lay,x,top_y,.26)
  rect(sub,'m4',x-.19,y-.19,x+.19,top_y+.19)
  sq(sub,'m3',x,y);sq(sub,'via3',x,y,.26)
  rect(sub,'m3',min(x,rx)-.19,y-.19,max(x,rx)+.19,y+.19)
  sq(sub,'m2',rx,y);sq(sub,'via2',rx,y,.26)
  rect(sub,'m2',rx-.19,oy+2.,rx+.19,y+.19)
  if g==0:routes.append({'bc':bc,'receiver_row':row,'receiver_origin_um':[rx-2.24,oy], 'array_x_um':x,'receiver_pin_um':[rx,oy+2.], 'join_y_um':y,'array_join_y_um':top_y,'metal2_length_um':AY+.5-top_y+y-(oy+2.),'metal3_length_um':abs(x-rx),'metal4_length_um':top_y-y,'via2_count':2,'via3_count':2,'width_um':.38})
 # Both ends of actual array ground straps tied physically to receiver VSS.
 for gy in [AY+.6,AY+end_y-.4]:
  rect(sub,'m5',AX-3.4,gy-.4,AX+94,gy+.4)
  sq(sub,'m4',AX-3,gy,.6);sq(sub,'via4',AX-3,gy,.26)
  for q in range(8):sq(sub,'via4',AX+1+q*11.56+.5,gy,.26)
 rect(sub,'m4',AX-3.22,.19,AX-2.78,AY+end_y)
 inst(T,sub,g*DX)
# Physically common wordlines and receiver phase/supply rails.
for row in range(H):
 y=AY+2+row*1.44+(row//8)*1.8+.9
 rect(T,'m3',0,y-.19,9*DX+AX+93.48,y+.19)
for row in range(8):
 for net,yy in [('VSS',.38),('PC',10.),('VDD',11.34)]:
  y=row*RP+yy;rect(T,'m3',AX-3,y-.19,9*DX+AX+91.4,y+.19)
# Actual power and PC pins at left edge, no output escape claim.
for net,x,y in [('VSS',1.,.38),('VDD',3.,11.34),('PC',5.,10.)]:
 rect(T,'m3',x-.19,y-.19,AX,y+.19);sq(T,'m4',x,y);sq(T,'via3',x,y,.26)
 rect(T,'m4',x-.22,y-.19,x+.22,AY+end_y)
 label(T,'m4',net,x,AY+end_y-1)
 if net!='PC':
  sq(T,'m4',x,AY+end_y-1,.6);sq(T,'via4',x,AY+end_y-1,.26);sq(T,'m5',x,AY+end_y-1,.8)
opt=k.SaveLayoutOptions();opt.select_cell(T.cell_index());L.write(str(O/'bank.gds'),opt)
b=T.dbbox(); report={'rows':H,'columns':320,'selections':H*320,'bits':H*1280,'option':'A, eight staggered receiver rows','top':T.name,'array_origin_um':[AX,AY],'group_pitch_um':DX,'receiver_row_pitch_um':RP,'receiver_rows':8,'receiver_cols_per_row_per_group':16,'receiver_profile':'pre2 2.88/.28 PMOS; keeper .36/.28; inverter .72/.28 P,.36/.28 N','bounds_um':[b.left,b.bottom,b.right,b.top],'dimensions_um':[b.width(),b.height()],'area_um2':b.width()*b.height(),'um2_per_selection':b.width()*b.height()/(H*320),'native_bit_pitch_um':.66,'native_group_of16_pitch_um':11.56,'join_routes_subbank0':routes,'array_end_y_um':end_y,'exclusions':['physical WL/PC drivers and decoder','phase controller','output latch and escape routing','global PDN IR/EM','shared products, lookup, accumulators'],'source_sha256':{str(t.relative_to(R)):hashlib.sha256(t.read_bytes()).hexdigest() for t in [basepath,recvpath,A/'indices.npy']},'gds_sha256':hashlib.sha256((O/'bank.gds').read_bytes()).hexdigest()}
(O/'geometry.json').write_text(json.dumps(report,indent=2)+'\n');print('W6-STATUS: generated',H,'rows',report['dimensions_um'],report['um2_per_selection'],'um2/selection',flush=True)
# Reopen programmed via geometry and independently reconstruct logical image.
V=k.Layout();V.read(str(O/'bank.gds'));back=np.zeros_like(idx);via=V.layer(35,0)
coords={(round(center(bc)*1000),round((2+r*1.44+(r//8)*1.8+.98)*1000)):(r,bc) for r in range(H) for bc in range(128)}
for g in range(10):
 seen=set()
 for shape in V.cell(f'PITCH_ARRAY_R{H}_G{g:02d}').shapes(via).each():
  xy=(shape.box.center().x,shape.box.center().y);assert xy in coords and xy not in seen;seen.add(xy);r,bc=coords[xy];c,bit=divmod(bc,4);back[r,32*g+c]|=1<<bit
mismatch=int(np.count_nonzero(back!=idx));assert mismatch==0
(O/'readback.json').write_text(json.dumps({'compared_indices':H*320,'compared_bits':H*1280,'mismatches':mismatch,'recovered_sha256':hashlib.sha256(back.tobytes()).hexdigest(),'method':'reopened GDS programmed Via1 centers at exact device drain positions, not mask input replay'},indent=2)+'\n')
print('W6-STATUS: reopened GDS bit readback zero mismatches',H*1280,flush=True)
