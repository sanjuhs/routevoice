"""Mask-via index ROM comparator for the P2 stored-address branch.

Four static one-transistor bits encode each representative index. The array
does not carry products; external index receivers/latches and a product mux
are required and excluded from this base-array layout.
"""
import json
import os
from pathlib import Path
import pya

HERE=Path(__file__).resolve().parent
ROWS=64
OUTPUTS=32
if ROWS<=0 or ROWS%8 or OUTPUTS<=0 or OUTPUTS%4:
    raise ValueError("Rows must be a multiple of 8; outputs a multiple of 4")
IMAGE=json.loads((HERE/"indices.json").read_text())
BITS=4*OUTPUTS
GROUPS=BITS//16
layout=pya.Layout();layout.dbu=.001
cell=layout.create_cell(f"TAALAS_MASK_INDEX_R{ROWS}_C{OUTPUTS}")
layers={"comp":22,"poly":30,"nplus":32,"pplus":31,"contact":33,
        "m1":34,"via1":35,"m2":36,"via2":38,"m3":42}


def rect(layer,x1,y1,x2,y2):
    cell.shapes(layout.layer(layers[layer],0)).insert(pya.DBox(x1,y1,x2,y2))


def square(layer,x,y,size):rect(layer,x-size/2,y-size/2,x+size/2,y+size/2)


def label(layer,name,x,y):
    cell.shapes(layout.layer(layers[layer],10)).insert(pya.DText(name,pya.DTrans(x,y)))


def center(bitcol):
    group,local=divmod(bitcol,16)
    return 1+group*(16*.66+1.0)+1.0+local*.66+.33


pitchy=1.44
y_positions=[2.0+r*pitchy+(r//8)*1.8 for r in range(ROWS)]
tap_positions=[1.0]+[2.0+(g+1)*8*pitchy+g*1.8+.65 for g in range(ROWS//8)]
end_x=1+GROUPS*(16*.66+1.0)
end_y=max(tap_positions)+.8
rect("m2",.31,.5,.69,end_y)
label("m2","VSS",.5,.6)
for bc in range(BITS):
    x=center(bc);output,bit=divmod(bc,4)
    rect("m2",x-.19,.5,x+.19,end_y)
    label("m2",f"IDX{output}_{bit}",x,.6)
    for row,oy in enumerate(y_positions):
        rect("comp",x-.18,oy,x+.18,oy+1.16)
        square("contact",x,oy+.18,.22)
        square("contact",x,oy+.98,.22)
        square("m1",x,oy+.98,.38)
        code=IMAGE[row][output]
        if (code>>bit)&1:
            square("via1",x,oy+.98,.26)
        else:
            # Label isolates a programmed-open drain for exact graph checks.
            label("m1",f"OPEN_R{row}_C{output}_B{bit}",x,oy+.98)
for row,oy in enumerate(y_positions):
    rect("nplus",.8,oy-.16,end_x+.2,oy+1.32)
    rect("poly",1.0,oy+.44,end_x+.07,oy+.72)
    rect("m1",.31,oy-.01,end_x,oy+.37)
    square("via1",.5,oy+.18,.26)
    rect("m3",1.0,oy+.71,end_x,oy+1.09)
    label("m3",f"WL{row}",1.1,oy+.90)
    for group in range(GROUPS):
        x=1+group*(16*.66+1.0)+.5
        rect("poly",x-.18,oy+.44,x+.18,oy+1.08)
        square("contact",x,oy+.90,.22)
        for metal in ["m1","m2","m3"]:square(metal,x,oy+.90,.38)
        square("via1",x,oy+.90,.26);square("via2",x,oy+.90,.26)
for ty in tap_positions:
    rect("comp",1.0,ty-.25,end_x,ty+.25)
    rect("pplus",.8,ty-.45,end_x+.2,ty+.45)
    rect("m1",.31,ty-.19,end_x,ty+.19)
    square("via1",.5,ty,.26)
    for bc in range(0,BITS,4):square("contact",center(bc),ty,.22)
layout.write(str(HERE/"index-array.gds"))
b=cell.dbbox()
(HERE/"layout-geometry.json").write_text(json.dumps({
    "variant":"separate mask-programmed index-bit comparator; P2 stored-address branch",
    "rows":ROWS,"outputs":OUTPUTS,"indices":ROWS*OUTPUTS,"bit_cells":ROWS*BITS,
    "mask_encoding":"Via1 present means one, absent means zero; 4 bit cells per index",
    "actual_image":"indices.json",
    "bit_column_pitch_um":.66,"row_pitch_um":pitchy,
    "poly_strap_corridor_um_per_16_bits":1.0,
    "active_repeat_area_um2_per_index":4*(.66+1/16)*pitchy,
    "bounds_um":[b.left,b.bottom,b.right,b.top],
    "bounding_area_um2":b.width()*b.height(),
    "bounding_area_um2_per_index":b.width()*b.height()/(ROWS*OUTPUTS),
    "excluded":["wordline decoding/drivers","4 index receivers/latches per output","16-to-1 shared-product mux per output","product distribution/generators","accumulator/state","IO/clock/power infrastructure"],
    "caution":"Not direct one-transistor product routing. No runtime SRAM weights; consumes index readout and mux energy/area. Raw bit-layout footprint cannot be used as whole macro area."},indent=2)+"\n")
