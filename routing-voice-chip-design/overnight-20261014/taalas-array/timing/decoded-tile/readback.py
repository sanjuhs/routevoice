from pathlib import Path
import klayout.db as k,numpy as np,json,hashlib
W=Path(__file__).resolve().parent;A=W.parents[1];O=W/'v1';L=k.Layout();L.read(str(O/'decoded-tile.gds'));via=L.layer(35,0);centers={}
for r in range(64):
 y=round((2+1.44*r+1.8*(r//8)+.98)*1000)
 for bc in range(128):
  group,local=divmod(bc,16);x=round((2+group*11.56+local*.66+.33)*1000);centers[x,y]=(r,bc)
back=np.zeros((64,320),np.uint8);ones=0
for g in range(10):
 c=L.cell(f'RV_ARRAY_00_{g}');seen=set()
 for s in c.shapes(via).each():
  if not s.is_box():continue
  xy=(s.box.center().x,s.box.center().y)
  if xy not in centers:continue
  assert xy not in seen;seen.add(xy);r,bc=centers[xy];col,b=divmod(bc,4);back[r,32*g+col]|=1<<b;ones+=1
expect=np.load(A/'indices.npy')[:64];bad=int(np.count_nonzero(back!=expect));assert bad==0
report={'compared_indices':20480,'compared_bits':81920,'index_mismatches':bad,'programmed_via1_ones':ones,'recovered_unpacked_sha256':hashlib.sha256(back.tobytes()).hexdigest(),'method':'Reopened saved decoded-tile.gds, recovered programmed Via1 mask centers of each of10actual arraycells; absence=0. Compared indices.npy first64rows, previously independently matched to W2b and packed model.'};(O/'readback.json').write_text(json.dumps(report,indent=2));print(report)
