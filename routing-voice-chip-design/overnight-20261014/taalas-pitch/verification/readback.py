"""Independent original-packed-tensor versus reopened programmed GDS audit."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
import klayout.db as k
import numpy as np
from verify import P,image,sha

p=argparse.ArgumentParser()
p.add_argument('--gds',required=True)
p.add_argument('--rows',type=int,required=True)
p.add_argument('--output',required=True)
a=p.parse_args()
out=P/a.output
assert out.parent.resolve()==P.resolve() and not out.exists()
assert a.rows in (64,320,1280)
gds=Path(a.gds).resolve()
l=k.Layout();l.read(str(gds))
top=l.cell(f'PITCH_BANK_R{a.rows}');assert top is not None
original,identity=image();observed=np.zeros((a.rows,320),np.uint8)
via=l.layer(35,0);placements=[];programmed_ones=0
children=list(top.each_inst());assert len(children)==10
for group in range(10):
 name=f'PITCH_ARRAY_R{a.rows}_G{group:02d}'
 joined_name=f'PITCH_JOINED_R{a.rows}_G{group:02d}'
 ji=[i for i in children if i.cell.name==joined_name];assert len(ji)==1
 ai=[i for i in ji[0].cell.each_inst() if i.cell.name==name];assert len(ai)==1
 assert ji[0].na<=1 and ji[0].nb<=1 and ai[0].na<=1 and ai[0].nb<=1
 placements.append(dict(group=group,joined_transform=str(ji[0].trans),array_transform=str(ai[0].trans)))
 cell=l.cell(name);assert cell is not None
 centers=[]
 for shape in cell.shapes(via).each():
  assert shape.is_box()
  centers.append((shape.box.center().x,shape.box.center().y))
 assert len(centers)==len(set(centers))
 found=set(centers);used=set()
 for row in range(a.rows):
  y=2+row*1.44+(row//8)*1.8+.98
  for local in range(128):
   group16,off=divmod(local,16)
   x=2+group16*(16*.66+1)+off*.66+.33
   key=(round(x/l.dbu),round(y/l.dbu))
   if key in found:
    lane,bit=divmod(group*128+local,4)
    observed[row,lane]|=1<<bit;programmed_ones+=1;used.add(key)
 assert used==found,('Unexpected programmed via locations',group,sorted(found-used)[:10])
expected=original[:a.rows,:]
xor=observed^expected
report=dict(gds=str(gds),gds_sha256=sha(gds),identity=identity,rows=a.rows,
 compared_selections=int(observed.size),compared_bits=int(observed.size*4),
 selection_mismatches=int(np.count_nonzero(xor)),
 bit_mismatches=sum(int(v).bit_count() for v in xor.ravel()),
 programmed_ones=programmed_ones,
 observed_sha256=hashlib.sha256(observed.tobytes()).hexdigest(),
 expected_sha256=hashlib.sha256(expected.tobytes()).hexdigest(),
 placements=placements,
 method='Reopened GDS Via1 centers at reviewed drain sites, plus each array instantiated exactly once. Expected bits independently decoded from original packed K64 tensor; no use of generator index image as oracle.')
out.write_text(json.dumps(report,indent=2)+'\n')
print('W6-STATUS: independent GDS readback',report['compared_bits'],'bits',report['bit_mismatches'],'mismatches',flush=True)
assert report['bit_mismatches']==0
