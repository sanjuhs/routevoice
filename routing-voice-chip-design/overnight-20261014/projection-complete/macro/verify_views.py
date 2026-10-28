from pathlib import Path
import json,re,hashlib
import klayout.db as k
W=Path(__file__).resolve().parent;R=W.parents[2];G=R/'overnight-20261014/taalas-pitch/r1280-v2/bank.gds'
l=k.Layout();l.read(str(G));t=l.cell('PITCH_BANK_R1280');names=set();labels={};layers={'Metal1':34,'Metal2':36,'Metal3':42,'Metal4':46,'Metal5':81}
for li in l.layer_indices():
 if l.get_info(li).datatype!=10:continue
 it=t.begin_shapes_rec(li)
 while not it.at_end():
  s=it.shape()
  if s.is_text():
   tx=s.text.transformed(it.trans());names.add(tx.string);labels.setdefault(tx.string,[]).append((l.get_info(li).layer,tx.x,tx.y))
  it.next()
lef=(W/'PITCH_BANK_R1280.lef').read_text();pinblocks=re.findall(r'^ PIN (\w+)\n(.*?)^ END \1$',lef,re.M|re.S)
assert len(pinblocks)==2563
matched=[]
for name,body in pinblocks:
 assert name in names
 for layer,rect in re.findall(r'LAYER (\w+) ;\s*RECT ([^;]+);',body):
  x1,y1,x2,y2=map(float,rect.split());b=k.Box(*[round(v*1000) for v in [x1,y1,x2,y2]])
  it=t.begin_shapes_rec_touching(l.layer(layers[layer],0),b);reg=k.Region()
  while not it.at_end():
   sh=it.shape()
   if sh.is_box() or sh.is_polygon():reg.insert(sh.polygon.transformed(it.trans()))
   it.next()
  assert (k.Region(b)-reg).is_empty(),(name,layer,rect)
 matched.append(name)
 # Any exported WL left access is on the same direct rectangle as a source label.
 if name.startswith('WL'):
  _,x,y=min(labels[name],key=lambda z:z[1]);direct=t.shapes(l.layer(42,0));assert any(sh.bbox().contains(k.Point(x,y)) and sh.bbox().contains(k.Point(100,y)) for sh in direct.each())
for name in ['VDD','VSS']:
 _,x,y=max([z for z in labels[name] if z[0]==46],key=lambda z:z[2]);it=t.begin_shapes_rec_touching(l.layer(41,0),k.Box(x-1,y-1,x+1,y+1));assert not it.at_end()
files=['PITCH_BANK_R1280.lef','PITCH_BANK_R1280.lib','PITCH_BANK_R1280.v']
r={'pass':True,'lef_pin_count':len(matched),'pin_names_exist_in_gds_labels':True,'all_lef_pin_rectangles_inside_actual_gds_metal':True,'WL_left_access_same_top_level_rectangle_as_label':True,'VDD_VSS_M4_to_M5_via4_exists':True,'source_gds_sha256':hashlib.sha256(G.read_bytes()).hexdigest(),'sha256':{f:hashlib.sha256((W/f).read_bytes()).hexdigest() for f in files},'physical_signoff':False}
(W/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
