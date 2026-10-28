from pathlib import Path
import json,hashlib,shutil,sys
import klayout.db as k
W=Path(__file__).resolve().parent;A=W.parents[1];O=W/(sys.argv[1] if len(sys.argv)>1 else 'v1');O.mkdir(exist_ok=True)
assert shutil.disk_usage('/').free>=22*2**30
source=A/'integrated/readout-tile0.gds';decoder=A/'periphery/handoff-v2/w5_row_decoder.gds';pins=json.loads((decoder.parent/'w5_row_decoder-pins.json').read_text())
L=k.Layout();L.read(str(source));L.read(str(decoder));T=L.create_cell('RV_K64_DECODED_TILE_00');old=L.cell('RV_K64_READOUT_TILE_00');T.copy_shapes(old)
lay={'m1':34,'v1':35,'m2':36,'v2':38,'m3':42,'v3':40,'m4':46,'v4':41,'m5':81}
def rect(c,l,x1,y1,x2,y2):c.shapes(L.layer(lay[l],0)).insert(k.DBox(min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)))
def sq(c,l,x,y,w):rect(c,l,x-w/2,y-w/2,x+w/2,y+w/2)
def label(c,l,n,x,y):c.shapes(L.layer(lay[l],10)).insert(k.DText(n,k.DTrans(x,y)))
removed=0
for s in list(T.shapes(L.layer(42,0)).each()):
 if s.is_box() and s.box.left==0 and s.box.width()>4000000 and s.box.bottom>110000:
  s.delete();removed+=1
assert removed==64,removed
D=L.cell('w5_row_decoder');assert D is not None
tr=k.Trans(k.Trans.M90,320000,100000);assert tr*k.Point(120000,0)==k.Point(200000,100000)
input_names=['enable']+[f'row[{i}]' for i in range(6)]
banks=[];routes=[]
for g in range(10):
 b=L.create_cell(f'RV_DECODED_BANK_00_{g}');b.insert(k.CellInstArray(L.cell(f'RV_JOINED_BANK_00_{g}').cell_index(),k.Trans()));b.insert(k.CellInstArray(D.cell_index(),tr))
 for row in range(64):
  ys=100+23.8+1.12*row;yt=110+2+1.44*row+1.8*(row//8)+.9;x=120+.8*row;xp=200.28;xa=102.9
  # Source M3 pin to M2 leg; isolated M3 intermediary at M4 via.
  sq(b,'m2',xp,ys,.56);sq(b,'v2',xp,ys,.26)
  rect(b,'m2',x-.19,ys-.19,xp+.19,ys+.19)
  sq(b,'m3',x,ys,.38);sq(b,'v2',x,ys,.26);sq(b,'v3',x,ys,.26);sq(b,'m4',x,ys,.38)
  rect(b,'m4',x-.19,min(ys,yt)-.19,x+.19,max(ys,yt)+.19)
  sq(b,'m4',x,yt,.6);sq(b,'v4',x,yt,.26)
  rect(b,'m5',xa-.4,yt-.3,x+.4,yt+.3)
  # M5 to actual local WL endpoint, through M4.
  sq(b,'m5',xa,yt,.8);sq(b,'m4',xa,yt,.6);sq(b,'m3',xa,yt,.6);sq(b,'v4',xa,yt,.26);sq(b,'v3',xa,yt,.26)
  routes.append({'group':g,'row':row,'source_y_um':ys,'target_y_um':yt,'track_x_um':x})
 # Extend the decoder's real M4 power stripes upward, without touching opposite rails.
 for net,y in [('VDD',225.),('VSS',228.)]:
  pr=next(p['rect_um'] for p in pins[net] if p['layer']=='Metal4');x=320-(pr[0]+pr[2])/2
  rect(b,'m4',x-.4,100+pr[3]-.4,x+.4,y+.4);sq(b,'m5',x,y,.8);sq(b,'v4',x,y,.26)
 for i,net in enumerate(input_names):
  pr=pins[net][0]['rect_um'];yp=100+(pr[1]+pr[3])/2;xp=320-(pr[0]+pr[2])/2;x=330+i*1.;yb=232+i*1.4
  rect(b,'m3',xp-.28,yp-.19,x+.19,yp+.19);sq(b,'m4',x,yp,.38);sq(b,'v3',x,yp,.26)
  rect(b,'m4',x-.22,yp-.19,x+.22,yb+.3);sq(b,'m4',x,yb,.6);sq(b,'m5',x,yb,.8);sq(b,'v4',x,yb,.26)
 T.insert(k.CellInstArray(b.cell_index(),k.Trans(g*468000,0)));banks.append(b)
# Physical common power and address/evaluate buses, with explicit new top labels.
end=9*468+337
for net,x,y in [('VDD',3.,225.),('VSS',1.,228.)]:
 rect(T,'m4',x-.22,218.,x+.22,y+.4);sq(T,'m4',x,y,.6);sq(T,'v4',x,y,.26)
 rect(T,'m5',x-.4,y-.4,end+.4,y+.4);label(T,'m5',net,x,y)
for i,net in enumerate(input_names):
 y=232+i*1.4;rect(T,'m5',0.,y-.4,end+.4,y+.4);label(T,'m5','EVAL' if net=='enable' else f'ROW{i-1}',.6,y)
opt=k.SaveLayoutOptions();opt.select_cell(T.cell_index());L.write(str(O/'decoded-tile.gds'),opt)
opt=k.SaveLayoutOptions();opt.select_cell(banks[0].cell_index());L.write(str(O/'decoded-bank0.gds'),opt)
bb=T.dbbox();report={'status':'generated_unverified','source_tile_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'decoder_sha256':hashlib.sha256(decoder.read_bytes()).hexdigest(),'removed_global_wordline_rectangles':removed,'decoder_instances':10,'wordline_connections':640,'address_evaluate_connections':70,'power_connections':20,'dimensions_um':[bb.width(),bb.height()],'area_um2':bb.width()*bb.height(),'ports':'ROW0..5,EVAL,PC,VDD,VSS,OUT0..1279; phase generation/mux/output capture external','routing':'M2 source legs, M4 vertical WL tracks, M5 WL target legs limited to gap left of decoder; upper M5 global controls/power','routes':routes}
(O/'geometry.json').write_text(json.dumps(report,indent=2)+'\n');print({n:v for n,v in report.items() if n!='routes'},flush=True)
