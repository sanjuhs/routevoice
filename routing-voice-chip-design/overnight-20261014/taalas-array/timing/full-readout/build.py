"""Reuse parent v3 geometry, with distinct real via programming in all20tiles."""
from pathlib import Path
import hashlib,json,shutil,os,time
import numpy as np
import klayout.db as k
W=Path(__file__).resolve().parent;A=W.parents[1];R=A.parents[1]
assert shutil.disk_usage('/').free>=22*2**30
source=A/'integrated/readout-tile0.gds';indices=np.load(A/'indices.npy')
L=k.Layout();L.read(str(source));assert L.dbu==.001
src=L.cell('RV_K64_READOUT_TILE_00');top=L.create_cell('RV_K64_PARTIAL_READOUT_1280x320')
v=L.layer(35,0);ml=L.layer(34,10)
centers={}
for row in range(64):
 y=round((2+row*1.44+(row//8)*1.8+.98)*1000)
 for bc in range(128):
  group,local=divmod(bc,16);x=round((2+group*11.56+local*.66+.33)*1000)
  centers[x,y]=(row,bc)
assert len(centers)==8192
bases=[];common_counts=[]
for g in range(10):
 old=L.cell(f'RV_ARRAY_00_{g}');b=L.create_cell(f'RV_VIAFREE_BASE_G{g:02d}');b.copy_shapes(old)
 removed=[]
 for s in list(b.shapes(v).each()):
  if s.is_box() and (s.box.center().x,s.box.center().y) in centers:
   removed.append((s.box.center().x,s.box.center().y));s.delete()
 label_count=0
 for s in list(b.shapes(ml).each()):
  if s.is_text() and s.text.string.startswith('OPEN_R'):s.delete();label_count+=1
 expected=sum(int(indices[r,g*32+c])>>bit&1 for r in range(64) for c in range(32) for bit in range(4))
 assert len(removed)==expected and label_count==8192-expected,(g,len(removed),expected,label_count)
 bases.append(b);common_counts.append({'group':g,'removed_mask_vias':len(removed),'removed_open_labels':label_count})
arrays=[];tiles=[]
for book in range(20):
 assert shutil.disk_usage('/').free>=22*2**30
 tile=L.create_cell(f'RV_K64_READOUT_BOOK_{book:02d}');tile.copy_shapes(src)
 for g in range(10):
  arr=L.create_cell(f'RV_REAL_MASK_B{book:02d}_G{g:02d}');arr.insert(k.CellInstArray(bases[g].cell_index(),k.Trans()))
  for (x,y),(r,bc) in centers.items():
   col,bit=divmod(bc,4)
   if int(indices[book*64+r,g*32+col])>>bit&1:arr.shapes(v).insert(k.Box(x-130,y-130,x+130,y+130))
   else:arr.shapes(ml).insert(k.Text(f'OPEN_R{r}_C{g*32+col}_B{bit}',k.Trans(x,y)))
  bank=L.create_cell(f'RV_JOINED_B{book:02d}_G{g:02d}');old=L.cell(f'RV_JOINED_BANK_00_{g}');bank.copy_shapes(old)
  for inst in old.each_inst():
   ci=inst.cell_index
   if L.cell(ci).name==f'RV_ARRAY_00_{g}':ci=arr.cell_index()
   bank.insert(k.CellInstArray(ci,inst.trans))
  tile.insert(k.CellInstArray(bank.cell_index(),k.Trans(g*468000,0)))
  arrays.append(arr.name)
 top.insert(k.CellInstArray(tile.cell_index(),k.Trans(0,book*240000)));tiles.append(tile.name)
opt=k.SaveLayoutOptions();opt.select_cell(top.cell_index());L.write(str(W/'partial-full-readout.gds'),opt)
b=top.dbbox();tb=tiles and L.cell(tiles[0]).dbbox()
report={'scope':'20 distinct real-programmed physically joined array+analog-receiver tiles; NOT complete macro','input_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'input_indices_sha256':hashlib.sha256((A/'indices.npy').read_bytes()).hexdigest(),'logical_shape':[1280,320],'selections':409600,'bitcells':1638400,'receiver_channels':25600,'receiver_transistors':102400,'hierarchy':'10 common via-free bases,10 shared receiver cells,200 distinct actual mask cells,200 joined banks,20 tile geometries','placement':'1 column x20 tile rows;240um ypitch;20um clear ygap','bounds_um':[b.left,b.bottom,b.right,b.top],'dimensions_um':[b.width(),b.height()],'bounding_area_um2':b.width()*b.height(),'bounding_area_um2_per_selection':b.width()*b.height()/409600,'sum_tile_area_um2':tb.width()*tb.height()*20,'tile_dimensions_um':[tb.width(),tb.height()],'tile_area_um2':tb.width()*tb.height(),'common_base_checks':common_counts,'mask_cells':arrays,'tile_cells':tiles,'exclusions':['No global 20-way bank select/output mux','No row decoder/wordline driver','No precharge/evaluate phase controller/drivers','No global signal or power interconnection between tiles','No top-level ARRAY-PORT pins or LEF','No full-assembly timing/energy or independent LVS'],'gds_bytes':(W/'partial-full-readout.gds').stat().st_size,'gds_sha256':hashlib.sha256((W/'partial-full-readout.gds').read_bytes()).hexdigest()}
(W/'geometry.json').write_text(json.dumps(report,indent=2)+'\n');print({key:value for key,value in report.items() if key not in ['mask_cells','tile_cells','common_base_checks']},flush=True)
# Reopen saved GDS and recover all choices from actual via coordinates.
V=k.Layout();V.read(str(W/'partial-full-readout.gds'));via=V.layer(35,0);back=np.zeros((1280,320),np.uint8);observed=0
for book in range(20):
 for g in range(10):
  arr=V.cell(f'RV_REAL_MASK_B{book:02d}_G{g:02d}');seen=set()
  for s in arr.shapes(via).each():
   assert s.is_box();xy=(s.box.center().x,s.box.center().y);assert xy in centers and xy not in seen;seen.add(xy)
   r,bc=centers[xy];col,bit=divmod(bc,4);back[book*64+r,g*32+col]|=1<<bit;observed+=1
assert np.array_equal(back,indices)
read={'all_indices_compared':409600,'all_bits_compared':1638400,'mismatches':0,'programmed_via1_ones':observed,'recovered_unpacked_sha256':hashlib.sha256(back.tobytes()).hexdigest(),'method':'Reopened emitted GDS; each programmed mask Via1 center decoded to row/lane/bit; absence decodes0. Common-base stripping independently checked against source ones/zeros.'}
(W/'readback.json').write_text(json.dumps(read,indent=2)+'\n');print(read,flush=True)
