#!/usr/bin/env python3
"""Read-only W6 GDS geometry to routing abstract. No GDS modification."""
import os
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
import json,hashlib,re
import klayout.db as k
W=Path(__file__).resolve().parent;R=W.parents[2];G=R/'overnight-20261014/taalas-pitch/r1280-v2/bank.gds'
L=k.Layout();L.read(str(G));T=L.cell('PITCH_BANK_R1280');dbu=L.dbu
layers={34:'Metal1',36:'Metal2',42:'Metal3',46:'Metal4',81:'Metal5'}
labels={}
for li in L.layer_indices():
 inf=L.get_info(li)
 if inf.datatype!=10:continue
 it=T.begin_shapes_rec(li)
 while not it.at_end():
  s=it.shape()
  if s.is_text():
   tx=s.text.transformed(it.trans());n=tx.string
   if re.fullmatch(r'(WL|OUT)\d+|PC|VDD|VSS',n):labels.setdefault(n,[]).append((inf.layer,tx.x,tx.y))
  it.next()
def rects_at(layer,x,y):
 it=T.begin_shapes_rec_touching(L.layer(layer,0),k.Box(x-1,y-1,x+1,y+1));out=[]
 while not it.at_end():
  sh=it.shape();b=sh.bbox().transformed(it.trans())
  if b.contains(k.Point(x,y)):out.append(b)
  it.next()
 return out
pins={};checks=[]

for i in range(1280):
 n=f'WL{i}'; lab=sorted(labels[n],key=lambda z:z[1])[0];_,x,y=lab
 # Left end of the top-level continuous physical M3 wordline.
 b=k.Box(0,y-190,6500,y+190)
 assert any((q & b)==b for q in rects_at(42,100,y))
 pins[n]=[(42,b)];checks.append({'pin':n,'label_count':len(labels[n]),'label_layer':42,'physical_rectangle_verified':True})
for i in range(1280):
 n=f'OUT{i}';assert len(labels[n])==1;layer,x,y=labels[n][0];bs=rects_at(layer,x,y)
 assert bs and layer==36
 b=max(bs,key=lambda b:b.area());pins[n]=[(layer,b)]
 checks.append({'pin':n,'label_count':1,'label_layer':layer,'physical_rectangle_verified':True})
for n in ['PC','VDD','VSS']:
 lab=max((z for z in labels[n] if z[0]==46),key=lambda z:z[2]);layer,x,y=lab
 bs=rects_at(layer,x,y);assert bs
 # Small labelled section of continuous M4 spine plus actual top-metal pad.
 b=k.Box(x-190,y-190,x+190,y+190) if n=='PC' else max(bs,key=lambda z:z.area());pins[n]=[(46,b)]
 if n!='PC':
  top=rects_at(81,x,y);assert len(top)==1;pins[n].append((81,top[0]))
 checks.append({'pin':n,'label_count':len(labels[n]),'label_layer':46,'physical_rectangle_verified':True,'top_metal_pad':n!='PC'})
width=1004.;height=2258.85
out=['VERSION 5.8 ;','BUSBITCHARS "[]" ;','DIVIDERCHAR "/" ;','MACRO PITCH_BANK_R1280',' CLASS BLOCK ;',' ORIGIN 0 0 ;',f' SIZE {width:.3f} BY {height:.3f} ;',' SYMMETRY X Y ;']
def line(b):return f' RECT {b.left*dbu:.3f} {b.bottom*dbu:.3f} {b.right*dbu:.3f} {b.top*dbu:.3f} ;'
for n,shapes in pins.items():
 direction='OUTPUT' if n.startswith('OUT') else ('INOUT' if n in ['VDD','VSS'] else 'INPUT')
 use='POWER' if n=='VDD' else ('GROUND' if n=='VSS' else 'SIGNAL')
 out.extend([f' PIN {n}',f'  DIRECTION {direction} ;',f'  USE {use} ;','  PORT'])
 for layer,b in shapes:out.extend([f'   LAYER {layers[layer]} ;','  '+line(b)])
 out.extend(['  END',f' END {n}'])
out.append(' OBS');obscount={}
for layer,name in layers.items():
 if layer==34:reg=k.Region(k.Box(0,0,1004000,2258850))
 else:
  reg=k.Region(T.begin_shapes_rec(L.layer(layer,0)))
  if layer==36:reg.insert(k.Box(0,126000,1004000,2258850))
  reg.merge()
  pr=k.Region()
  for vals in pins.values():
   for pl,b in vals:
    if pl==layer:pr.insert(b)
  reg-=pr
 out.append(f'  LAYER {name} ;');nr=0
 for poly in reg.each():
  # Exact Manhattan decomposition; bbox would incorrectly block output escape.
  for p in poly.decompose_trapezoids():
   assert p.is_box();out.append(' '+line(p.bbox()));nr+=1
 obscount[name]=nr
out.extend([' END','END PITCH_BANK_R1280','END LIBRARY'])
(W/'PITCH_BANK_R1280.lef').write_text('\n'.join(out)+'\n')
ports=[]
for n in pins:
 d='output' if n.startswith('OUT') else ('inout' if n in ['VDD','VSS'] else 'input')
 ports.append(f'    {d} wire {n}')
(W/'PITCH_BANK_R1280.v').write_text('// Physical W6 macro; no behavioral replacement in synthesis.\n(* blackbox *) module PITCH_BANK_R1280 (\n'+',\n'.join(ports)+'\n);\nendmodule\n')
receipt={'source_gds':str(G.relative_to(R)),'source_gds_sha256':hashlib.sha256(G.read_bytes()).hexdigest(),'source_cell':T.name,'source_bounds_um':[T.dbbox().left,T.dbbox().bottom,T.dbbox().right,T.dbbox().top],'lef_origin_um':[0,0],'lef_size_um':[width,height],'lef_envelope_area_um2':width*height,'source_material_bbox_area_um2':T.dbbox().width()*T.dbbox().height(),'pin_count':len(pins),'wordlines':1280,'outputs':1280,'control':['PC'],'power':['VDD','VSS'],'checks':checks,'obstruction_rectangles':obscount,'power_access':'Original M5 0.8x0.8um pad physically present at M4-labelled VDD/VSS with via4; neither GDS nor labels changed.','scope':'Geometry pin coverage only, not full-bank LVS, timing, IR/EM or routability signoff.'}
(W/'pin-checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
(W/'pins.json').write_text(json.dumps({n:[{'layer':layers[l],'rect_um':[b.left*dbu,b.bottom*dbu,b.right*dbu,b.top*dbu]} for l,b in ss] for n,ss in pins.items()},indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='checks'},indent=2))
