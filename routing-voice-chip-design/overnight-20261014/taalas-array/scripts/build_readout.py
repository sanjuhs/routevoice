"""First real-image joined array/receiver tile; decoder/mux remain explicit ports.
Reuses original layout generators, widening receiver strip into one128-bit row.
"""
from pathlib import Path
import os,sys,json,shutil,hashlib
sys.dont_write_bytecode=True
import numpy as np
import klayout.db as pya
W=Path(__file__).resolve().parents[1];R=W.parents[1];O=W/'integrated';O.mkdir(exist_ok=True)
assert shutil.disk_usage(W).free>=22*2**30
indices=np.load(W/'indices.npy');layout=pya.Layout();layout.dbu=.001
T=layout.create_cell('RV_K64_READOUT_TILE_00')
basepath=R/'experiments/taalas-access/mask-index-comparator/generate_layout.py'
recvpath=basepath.parent/'receiver-strip/generate_layout.py'
# Use80um separation channel above receiver for128 distinct horizontal tracks.
DX=468.;AX=10.;AY=110.
layers={'m1':34,'via1':35,'m2':36,'via2':38,'m3':42,'via3':40,'m4':46,'via4':41,'m5':81}
def rect(c,layer,x1,y1,x2,y2):c.shapes(layout.layer(layers[layer],0)).insert(pya.DBox(x1,y1,x2,y2))
def sq(c,l,x,y,w):rect(c,l,x-w/2,y-w/2,x+w/2,y+w/2)
def label(c,l,n,x,y):c.shapes(layout.layer(layers[l],10)).insert(pya.DText(n,pya.DTrans(x,y)))
def transfer(cell):
    d=layout.create_cell(cell.name);d.copy_tree(cell);return d
banks=[]
for g in range(10):
    # Literal reuse of qualified base generator; only real image and signal naming change.
    s=basepath.read_text().replace('import pya','import klayout.db as pya');s=s[:s.index('layout.write(')]
    s=s.replace('code=(row+3*output)%16','code=int(indices[row,32*group+output])')
    s=s.replace('f"IDX{output}_{bit}"','f"IDX{32*group+output}_{bit}"').replace('f"OPEN_R{row}_C{output}_B{bit}"','f"OPEN_R{row}_C{32*group+output}_B{bit}"')
    os.environ['TAALAS_ARRAY_ROWS']='64';os.environ['TAALAS_ARRAY_COLS']='32'
    ns={'__file__':str(O/'reused-base.py'),'indices':indices,'group':g};exec(compile(s,str(basepath),'exec'),ns)
    ns['cell'].name=f'RV_ARRAY_00_{g}';a=transfer(ns['cell'])
    s=recvpath.read_text().replace('import pya','import klayout.db as pya');s=s[:s.index('layout.write(')]
    s=s.replace('range(8)','range(1)').replace('range(16)','range(128)').replace('55.7','447.7').replace('82.89','10.09')
    s=s.replace("f'IDX{i}'","f'IDX{32*group+i//4}_{i%4}'").replace("f'OUT{i}'","f'OUT{128*group+i}'")
    nsr={'__file__':str(O/'reused-receiver.py'),'group':g};exec(compile(s,str(recvpath),'exec'),nsr)
    nsr['cell'].name=f'RV_RECEIVER_128_{g}';v=transfer(nsr['cell'])
    bank=layout.create_cell(f'RV_JOINED_BANK_00_{g}')
    bank.insert(pya.CellInstArray(a.cell_index(),pya.Trans(round(AX*1000),round(AY*1000))))
    bank.insert(pya.CellInstArray(v.cell_index(),pya.Trans(round(AX*1000),0)))
    for bc in range(128):
        x=AX+ns['center'](bc);rx=AX+bc*3.5+2.24;y=12+bc*.66
        rect(bank,'m2',x-.19,y-.19,x+.19,AY+.69)
        sq(bank,'m3',x,y,.38);sq(bank,'via2',x,y,.26)
        rect(bank,'m3',min(x,rx)-.19,y-.19,max(x,rx)+.19,y+.19)
        rect(bank,'m4',rx-.19,1.81,rx+.19,y+.19)
        for yy in [2.,y]:
            sq(bank,'m3',rx,yy,.38);sq(bank,'via3',rx,yy,.26)
        sq(bank,'m2',rx,2.,.38);sq(bank,'via2',rx,2.,.26)
    # Real return path from array source/substrate rail to receiver VSS.
    x=AX+.5;y=AY+.6
    sq(bank,'m2',x,y,.38);sq(bank,'m3',x,y,.38);sq(bank,'via2',x,y,.26)
    rect(bank,'m3',AX-3.19,y-.19,x+.19,y+.19)
    sq(bank,'via3',AX-3,y,.26);rect(bank,'m4',AX-3.19,.19,AX-2.81,y+.19)
    T.insert(pya.CellInstArray(bank.cell_index(),pya.Trans(round(g*DX*1000),0)));banks.append(bank)
# Join common64 wordlines and the receiver power/control rails through actual metal.
END=9*DX+AX+447.7
for r in range(64):
    y=AY+2+r*1.44+(r//8)*1.8+.90
    rect(T,'m3',0.,y-.19,9*DX+AX+93.48,y+.19)
for net,y in [('VSS',.38),('PC',8.56),('VDD',9.9)]:
    rect(T,'m3',AX-3,y-.19,END,y+.19)
# Bring outputs and PC to actual macro boundaries for the LEF abstract.
for g in range(10):
    for bc in range(128):
        x=g*DX+AX+bc*3.5+2.9
        rect(T,'m2',x-.19,0.,x+.19,1.77)
rect(T,'m3',0.,8.37,AX,8.75)
# Explicit M4/M5 supply connection pins on left, off all signal tracks.
for net,x,y in [('VSS',1.,.38),('VDD',3.,9.9)]:
    rect(T,'m3',x-.19,y-.19,AX,y+.19);sq(T,'m4',x,y,.38);sq(T,'via3',x,y,.26)
    rect(T,'m4',x-.22,y-.19,x+.22,220.)
    sq(T,'m4',x,219.,.6);sq(T,'via4',x,219.,.26);sq(T,'m5',x,219.,.8)
    label(T,'m4',net,x,218.);label(T,'m5',net,x,219.)
opt=pya.SaveLayoutOptions();opt.select_cell(banks[0].cell_index());layout.write(str(O/'joined-bank0.gds'),opt)
layout.write(str(O/'readout-tile0.gds'))
b=T.dbbox();bb=banks[0].dbbox()
result={'status':'joined_array_and_analog_readout_only','tile_selections':20480,'tile_bitcells':81920,'receiver_channels':1280,'receiver_transistors':5120,'tile_bounds_um':[b.left,b.bottom,b.right,b.top],'tile_dimensions_um':[b.width(),b.height()],'tile_area_um2':b.width()*b.height(),'partial_um2_per_selection':b.width()*b.height()/20480,'subbank_dimensions_um':[bb.width(),bb.height()],'channel_routing':'actual M2 bitline legs, M3 fanout horizontal tracks, M4 receiver legs;128 tracks at0.66um; zero ideal joins','wordlines':'actual commonM3 wires across10subbanks; decoder/driver external','exclusions':['row decoder/driver integration','precharge/evaluate nonoverlap control/driver','20-way bank select','raw-index output latches (not implemented in this tile; W2b captures mapped representatives)','complete PDN integrity','distributedRC and integrated timing'],'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [basepath,recvpath]}}
(O/'geometry.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
