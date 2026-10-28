from pathlib import Path
import json,math,hashlib
import klayout.db as d
W=Path(__file__).resolve().parents[1];O=W/'integrated';l=d.Layout();l.read(str(O/'readout-tile0.gds'));t=l.cell('RV_K64_READOUT_TILE_00');bbox=t.dbbox();width=math.ceil(bbox.right);height=math.ceil(bbox.top)
pins={}
for i in range(1280):
 g,bc=divmod(i,128);x=g*468.+10.+bc*3.5+2.9
 pins[f'OUT{i}']={'direction':'OUTPUT','use':'SIGNAL','rects':[('Metal2',[x-.18,0,x+.18,.5])]}
for r in range(64):
 y=110+2+r*1.44+(r//8)*1.8+.90
 pins[f'WL{r}']={'direction':'INPUT','use':'SIGNAL','rects':[('Metal3',[0,y-.18,.5,y+.18])]}
pins['PC']={'direction':'INPUT','use':'SIGNAL','rects':[('Metal3',[0,8.38,.5,8.74])]}
for name,x in [('VSS',1.),('VDD',3.)]:
 pins[name]={'direction':'INOUT','use':'GROUND' if name=='VSS' else 'POWER','rects':[('Metal4',[x-.21,217.,x+.21,220.]),('Metal5',[x-.4,218.6,x+.4,219.4])]}
layers={'Metal1':34,'Metal2':36,'Metal3':42,'Metal4':46,'Metal5':81};regions={n:d.Region(t.begin_shapes_rec(l.layer(num,0))) for n,num in layers.items()}
for n,p in pins.items():
 for layer,box in p['rects']:
  want=d.Region(d.Box(*(round(x*1000) for x in box)))
  assert (want-regions[layer]).is_empty(),('LEF pin outside metal',n,layer,box)
lines=['# W5 partial readout tile: NOT an ARRAY-PORT replacement; decoder/phase/mux external.','VERSION 5.8 ;','BUSBITCHARS "[]" ;','DIVIDERCHAR "/" ;','MACRO RV_K64_READOUT_TILE_00','  CLASS BLOCK ;','  ORIGIN 0 0 ;',f'  SIZE {width} BY {height} ;','  SYMMETRY X Y ;']
for name,p in pins.items():
 lines += [f'  PIN {name}',f'    DIRECTION {p["direction"]} ;',f'    USE {p["use"]} ;','    PORT']
 for layer,box in p['rects']:lines += [f'      LAYER {layer} ;','      RECT '+' '.join(f'{x:.3f}' for x in box)+' ;']
 lines+=['    END',f'  END {name}']
lines+=['  OBS']
for layer in layers:lines += [f'    LAYER {layer} ;',f'    RECT 0 0 {width} {height} ;']
lines+=['  END','END RV_K64_READOUT_TILE_00','END LIBRARY']
(O/'readout-tile0.lef').write_text('\n'.join(lines)+'\n');(O/'lef-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
(O/'lef-audit.json').write_text(json.dumps({'macro':'RV_K64_READOUT_TILE_00','size_um':[width,height],'outline_area_um2':width*height,'pins':len(pins),'all_pin_rectangles_inside_actual_gds_metal':True,'power_layers':['Metal4','Metal5'],'gds_sha256':hashlib.sha256((O/'readout-tile0.gds').read_bytes()).hexdigest(),'scope':'Partial readout tile only, no row decoder/phase controller/bank mux, no timing Liberty; not approved for W2b integration'},indent=2)+'\n')
print('W5-STATUS: partial readout tile LEF pins geometrically checked',len(pins))
