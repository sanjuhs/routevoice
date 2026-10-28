"""128 stronger-precharge physical receiver channels, separate from index array.

This initial legal construction targets explicit peripheral area rather than
minimum density. Bitline/output hookups to array/bank mux remain external.
"""
import json
from pathlib import Path
import pya

HERE=Path(__file__).resolve().parent
layout=pya.Layout();layout.dbu=.001
cell=layout.create_cell('TAALAS_INDEX_RECEIVER_128')
layers={'nwell':21,'comp':22,'poly':30,'nplus':32,'pplus':31,'contact':33,
        'm1':34,'via1':35,'m2':36,'via2':38,'m3':42,'via3':40,'m4':46}


def rect(layer,x1,y1,x2,y2):
    cell.shapes(layout.layer(layers[layer],0)).insert(pya.DBox(x1,y1,x2,y2))


def square(layer,x,y,size):rect(layer,x-size/2,y-size/2,x+size/2,y+size/2)


def label(layer,name,x,y):
    cell.shapes(layout.layer(layers[layer],10)).insert(pya.DText(name,pya.DTrans(x,y)))


def stack(x,y,top):
    for layer in ['m1','m2','m3'][:top]:square(layer,x,y,.38)
    if top>=2:square('via1',x,y,.26)
    if top>=3:square('via2',x,y,.26)


def transistor(x,y,width,kind):
    rect('comp',x+.8,y,x+1.96,y+width)
    rect('poly',x+1.24,y-.22,x+1.52,y+width+.68)
    for cx in [x+.98,x+1.78]:
        square('contact',cx,y+width/2,.22)
        square('m1',cx,y+width/2,.38)
    gy=y+width+.5
    square('poly',x+1.38,gy,.36);square('contact',x+1.38,gy,.22)
    square('m1',x+1.38,gy,.38)
    return y+width/2,gy


for row in range(8):
    oy=row*11.84
    for rail,y,left in [('VSS',.38,-3),('PC',10.0,-2),('VDD',11.34,-1)]:
        rect('m3',left-.19,oy+y-.19,55.7,oy+y+.19)
        square('m4',left,oy+y,.38);square('via3',left,oy+y,.26)
        label('m3',rail,0,oy+y)
    for col in range(16):
        x=col*3.5;i=row*16+col
        rect('nwell',x+.36,oy+2.7,x+2.40,oy+11.44)
        rect('nplus',x+.64,oy+1.17,x+2.12,oy+1.99)
        rect('pplus',x+.64,oy+2.97,x+2.12,oy+9.73)
        # Grounded substrate tap and VDD nwell tap.
        for ty,implant in [(.2,'pplus'),(10.64,'nplus')]:
            rect('comp',x+.8,oy+ty,x+1.96,oy+ty+.36)
            rect(implant,x+.64,oy+ty-.16,x+2.12,oy+ty+.52)
            square('contact',x+.98,oy+ty+.18,.22)
            square('m1',x+.98,oy+ty+.18,.38)
        dn,gn=transistor(x,oy+1.4,.36,'n')
        dp,gp=transistor(x,oy+3.2,.72,'p')
        dk,gk=transistor(x,oy+5.06,.36,'p')
        dc,gc=transistor(x,oy+6.62,2.88,'p')
        # Ground source and body; supply PMOS sources and body.
        rect('m1',x+.79,oy+.19,x+1.17,dn+.19);stack(x+.98,oy+.38,3)
        rect('m2',x+.11,dp-.19,x+.49,oy+11.53)
        for yy in [dp,dk,dc,oy+10.82]:
            rect('m1',x+.11,yy-.19,x+1.17,yy+.19);stack(x+.3,yy,2)
        rect('m1',x+.11,oy+10.63,x+.49,oy+11.53)
        stack(x+.3,oy+11.34,3)
        # Read node joins PMOS keeper/precharge drains and inverter gates.
        rect('m2',x+2.05,oy+2.0,x+2.43,dc+.19)
        for yy,start in [(gn,1.38),(gp,1.38),(dk,1.78),(dc,1.78)]:
            rect('m1',x+start-.19,yy-.19,x+2.43,yy+.19);stack(x+2.24,yy,2)
        label('m2',f'IDX{i}',x+2.24,oy+2.0)
        # Inverter output feeds keeper gate and an external index latch.
        rect('m2',x+2.71,dn-.19,x+3.09,gk+.19)
        for yy,start in [(dn,1.78),(dp,1.78),(gk,1.38)]:
            rect('m1',x+start-.19,yy-.19,x+3.09,yy+.19);stack(x+2.9,yy,2)
        label('m2',f'OUT{i}',x+2.9,dn)
        stack(x+1.38,gc,3)
for rail,x in [('VSS',-3),('PC',-2),('VDD',-1)]:
    rect('m4',x-.19,.19,x+.19,94.41);label('m4',rail,x,.38)
layout.write(str(HERE/'receiver-strip.gds'))
b=cell.dbbox();area=b.width()*b.height()
(HERE/'layout-geometry.json').write_text(json.dumps({
    'channels':128,'devices':512,'device_sizes_um':{'precharge_pmos':[2.88,.28],'keeper_pmos':[.36,.28],'inverter_pmos':[.72,.28],'inverter_nmos':[.36,.28]},
    'bounds_um':[b.left,b.bottom,b.right,b.top],'bounding_area_um2':area,'area_um2_per_index_bit_receiver':area/128,
    'layout_scope':'128 channels with actual wells/taps, local readout wiring and common VDD/VSS/precharge buses; no bitline-to-array or output-to-bank-mux routes',
    'excluded':['array','wordline decoder/drivers','precharge driver','bank-selection mux','index flip-flops','global integration/power straps'],
    'density_claim':'Constructive footprint only, not minimum peripheral area or integrated macro'},indent=2)+'\n')
