"""Actual striped tall banks using retained GF180 array/pre2 receiver rules."""
from pathlib import Path
import argparse,hashlib,json,math,os,shutil,sys
sys.dont_write_bytecode=True
import numpy as np
import klayout.db as k
W=Path(__file__).resolve().parent;A=W.parent;R=A.parents[1]
p=argparse.ArgumentParser();p.add_argument('--rows',type=int,choices=[320,1280],required=True);args=p.parse_args()
H=args.rows;B=1280//H;O=W/f'r{H}';O.mkdir(exist_ok=True)
assert shutil.disk_usage('/').free>=22*2**30
if H==1280:assert shutil.disk_usage('/').free>=24*2**30, 'Reserve at least2GiB above hard22GiB floor for optional1280 GDS'
idx=np.load(A/'indices.npy');L=k.Layout();L.dbu=.001
DX=468.;AX=10.;AY=112.
layers={'m1':34,'via1':35,'m2':36,'via2':38,'m3':42,'via3':40,'m4':46,'via4':41,'m5':81}
def rect(c,l,x1,y1,x2,y2):c.shapes(L.layer(layers[l],0)).insert(k.DBox(x1,y1,x2,y2))
def sq(c,l,x,y,w):rect(c,l,x-w/2,y-w/2,x+w/2,y+w/2)
def label(c,l,n,x,y):c.shapes(L.layer(layers[l],10)).insert(k.DText(n,k.DTrans(x,y)))
def inst(c,sub,x=0,y=0):c.insert(k.CellInstArray(sub.cell_index(),k.Trans(round(x*1000),round(y*1000))))
def transfer(c,name):c.name=name;d=L.create_cell(name);d.copy_tree(c);return d
basepath=R/'experiments/taalas-access/mask-index-tall/generate_layout.py'
recvpath=basepath.parent/'receiver-pre2/generate_layout.py'
bases=[];receivers=[]
os.environ['TAALAS_ARRAY_ROWS']=str(H);os.environ['TAALAS_ARRAY_COLS']='32'
for g in range(10):
 s=basepath.read_text().replace('import pya','import klayout.db as pya');s=s[:s.index('layout.write(')]
 s=s.replace('code=code_for(row,output)','code=0').replace('f"IDX{output}_{bit}"','f"IDX{32*group+output}_{bit}"')
 ns={'__file__':str(O/'reused-base.py'),'group':g};exec(compile(s,str(basepath),'exec'),ns)
 for shape in list(ns['cell'].shapes(ns['layout'].layer(34,10)).each()):
  if shape.is_text() and shape.text.string.startswith('OPEN_'):shape.delete()
 bases.append(transfer(ns['cell'],f'TALL_BASE_R{H}_G{g:02d}'))
 s=recvpath.read_text().replace('import pya','import klayout.db as pya');s=s[:s.index('layout.write(')]
 s=s.replace('range(8)','range(1)').replace('range(16)','range(128)').replace('55.7','447.7').replace('94.41','11.53')
 s=s.replace("f'IDX{i}'","f'IDX{32*group+i//4}_{i%4}'").replace("f'OUT{i}'","f'OUT{128*group+i}'")
 nr={'__file__':str(O/'reused-receiver.py'),'group':g};exec(compile(s,str(recvpath),'exec'),nr)
 receivers.append(transfer(nr['cell'],f'TALL_PRE2_RECEIVER_G{g:02d}'))
end_y=ns['end_y'];TOP=math.ceil(AY+end_y+4);PITCH=TOP+20;END=9*DX+AX+447.7
top=L.create_cell(f'TALL_ASSEMBLY_R{H}');banknames=[];selected=None
for b in range(B):
 assert shutil.disk_usage('/').free>=22*2**30
 bank=L.create_cell(f'TALL_BANK_R{H}_B{b:02d}');banknames.append(bank.name)
 for g in range(10):
  arr=L.create_cell(f'TALL_ARRAY_B{b:02d}_G{g:02d}');inst(arr,bases[g])
  for row in range(H):
   y=2+row*1.44+(row//8)*1.8+.98
   for bc in range(128):
    x=ns['center'](bc);c,bit=divmod(bc,4)
    if int(idx[b+B*row,32*g+c])>>bit&1:sq(arr,'via1',x,y,.26)
    else:label(arr,'m1',f'OPEN_R{row}_C{32*g+c}_B{bit}',x,y)
  sub=L.create_cell(f'TALL_JOINED_R{H}_B{b:02d}_G{g:02d}');inst(sub,arr,AX,AY);inst(sub,receivers[g],AX,0)
  for bc in range(128):
   x=AX+ns['center'](bc);rx=AX+bc*3.5+2.24;y=14+bc*.66
   rect(sub,'m2',x-.19,y-.19,x+.19,AY+.69)
   sq(sub,'m3',x,y,.38);sq(sub,'via2',x,y,.26)
   rect(sub,'m3',min(x,rx)-.19,y-.19,max(x,rx)+.19,y+.19)
   rect(sub,'m4',rx-.19,1.81,rx+.19,y+.19)
   for yy in [2.,y]:sq(sub,'m3',rx,yy,.38);sq(sub,'via3',rx,yy,.26)
   sq(sub,'m2',rx,2.,.38);sq(sub,'via2',rx,2.,.26)
  # Array return reaches receiver VSS physically, preserving prior join style.
  x=AX+.5;y=AY+.6
  sq(sub,'m2',x,y,.38);sq(sub,'m3',x,y,.38);sq(sub,'via2',x,y,.26)
  rect(sub,'m3',AX-3.19,y-.19,x+.19,y+.19)
  sq(sub,'via3',AX-3,y,.26);rect(sub,'m4',AX-3.19,.19,AX-2.81,y+.19)
  # Upper endpoints of all eight physical array ground straps have actual VSS metal.
  gy=AY+end_y-.4
  rect(sub,'m5',AX-3.4,gy-.4,AX+94,gy+.4)
  rect(sub,'m4',AX-3.22,AY+.6,AX-2.78,gy+.4)
  sq(sub,'via4',AX-3,gy,.26)
  for q in range(8):sq(sub,'via4',AX+1+q*11.56+.5,gy,.26)
  inst(bank,sub,g*DX)
  if (b,g)==((3,3) if H==320 else (0,7)):selected=sub
 for row in range(H):
  y=AY+2+row*1.44+(row//8)*1.8+.90
  rect(bank,'m3',0,y-.19,9*DX+AX+93.48,y+.19)
 for net,y in [('VSS',.38),('PC',10.),('VDD',11.34)]:rect(bank,'m3',AX-3,y-.19,END,y+.19)
 for g in range(10):
  for bc in range(128):
   x=g*DX+AX+bc*3.5+2.9;rect(bank,'m2',x-.19,0,x+.19,1.77)
 rect(bank,'m3',0,9.81,AX,10.19)
 for net,x,y in [('VSS',1.,.38),('VDD',3.,11.34)]:
  rect(bank,'m3',x-.19,y-.19,AX,y+.19);sq(bank,'m4',x,y,.38);sq(bank,'via3',x,y,.26)
  rect(bank,'m4',x-.22,y-.19,x+.22,TOP)
  sq(bank,'m4',x,TOP-1,.6);sq(bank,'via4',x,TOP-1,.26);sq(bank,'m5',x,TOP-1,.8)
  label(bank,'m4',net,x,TOP-2);label(bank,'m5',net,x,TOP-1)
 inst(top,bank,0,b*PITCH)
def save(cell,name):
 opt=k.SaveLayoutOptions();opt.select_cell(cell.cell_index());L.write(str(O/name),opt)
save(top,'assembly.gds')
if H==320:save(L.cell(banknames[0]),'bank0.gds')
save(selected,'timing-subbank.gds')
if H==320:save(L.cell(banknames[3]),'bank3.gds')
bb=L.cell(banknames[0]).dbbox();tb=top.dbbox()
report={'rows_per_bank':H,'bank_count':B,'logical_shape':[1280,320],'row_mapping':'logical_row = bank + bank_count * local_row','readouts_per_bank':1280,'readout_count':B*1280,'receiver_profile':'pre2 physical receiver: Wpc2.88 L.28; keeper.36/pinv.72/ninv.36; stockdrivers not placed','bank_dimensions_um':[bb.width(),bb.height()],'bank_area_um2':bb.width()*bb.height(),'assembly_dimensions_um':[tb.width(),tb.height()],'assembly_area_um2':tb.width()*tb.height(),'assembly_um2_per_selection':tb.width()*tb.height()/409600,'sum_bank_area_um2':B*bb.width()*bb.height(),'bank_pitch_um':PITCH,'array_origin_um':[AX,AY],'group_pitch_um':DX,'fanout_start_y_um':14,'fanout_pitch_um':.66,'join_metal_width_um':.38,'array_ground_straps':{'count_per32lane_subbank':8,'width_um':2,'layer':'Metal4','both_end_connections':'lower physical source return and upper M5 return to sameVSS'},'tops':{'assembly':top.name,'bank0':banknames[0],'timing_subbank':selected.name},'timing_subbank_gds':'timing-subbank.gds','exclusions':['row decoder and physical WL drivers','physicalPCdriver/phasecontrol','global bank output mux and output latches','global interbank signal/PDN integration','fullbank simultaneouscurrent/distributedRC timing'],'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [basepath,recvpath]},'gds_sha256':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in ['assembly.gds','bank0.gds','timing-subbank.gds'] if (O/n).exists()}}
(O/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print('W5-STATUS:',H,'row real-layout generation',json.dumps(report),flush=True)
# Recover programmed drain Via1 positions from the emitted GDS, not mask inputs.
V=k.Layout();V.read(str(O/'assembly.gds'));via=V.layer(35,0);back=np.zeros_like(idx)
coords={(round(ns['center'](bc)*1000),round((2+r*1.44+(r//8)*1.8+.98)*1000)):(r,bc) for r in range(H) for bc in range(128)}
ones=0
for b in range(B):
 for g in range(10):
  seen=set()
  for shape in V.cell(f'TALL_ARRAY_B{b:02d}_G{g:02d}').shapes(via).each():
   xy=(shape.box.center().x,shape.box.center().y);assert xy in coords and xy not in seen;seen.add(xy)
   r,bc=coords[xy];c,bit=divmod(bc,4);back[b+B*r,32*g+c]|=1<<bit;ones+=1
assert np.array_equal(back,idx)
read={'compared_indices':409600,'compared_bits':1638400,'mismatches':0,'programmed_ones':ones,'recovered_indices_sha256':hashlib.sha256(back.tobytes()).hexdigest(),'method':'reopened actualGDS maskVia1 center readback; reconstructed logical row order from explicit striped map'}
(O/'readback.json').write_text(json.dumps(read,indent=2)+'\n');print('W5-STATUS:',H,'row layout bitreadback',json.dumps(read),flush=True)
