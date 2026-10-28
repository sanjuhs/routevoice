"""Reuse the qualified stored-index generator; real masks, independent readback.

This output is explicitly the cell-array core, NOT the completed read macro.
"""
from pathlib import Path
import os,sys,json,re,hashlib,shutil
sys.dont_write_bytecode=True
import numpy as np
import klayout.db as pya
W=Path(__file__).resolve().parents[1]; R=W.parents[1]
O=W/'base';O.mkdir(exist_ok=True)
assert shutil.disk_usage(W).free >= 22*2**30
sha=lambda b:hashlib.sha256(b).hexdigest()
candidate=R/'models/candidates/codebook-4bit-optimal-rectangular-k64'
manifest=json.loads((candidate/'candidate.json').read_text())
record=next(x for x in manifest['changed_tensor_records'] if x['file']=='encoder.ort' and x['tensor']=='val_89_quantized')
packed=(candidate/'packed'/record['packed_file']).read_bytes()
assert sha(packed)==record['packed_sha256']
indices=np.zeros((1280,320),np.uint8);coverage=np.zeros_like(indices);weights=np.zeros_like(indices)
used=np.zeros(len(packed),np.uint8)
for b in record['blocks']:
    r0,r1=b['rows'];c0,c1=b['columns'];off=b['index_offset'];size=b['index_bytes'];n=b['value_count']
    assert c1-c0==1 and r1-r0==64 and n==64 and size==32
    a=np.frombuffer(packed[off:off+size],np.uint8);v=np.empty(n,np.uint8);v[::2]=a&15;v[1::2]=a>>4
    assert not coverage[r0:r1,c0:c1].any() and not used[off:off+size].any()
    indices[r0:r1,c0]=v;coverage[r0:r1,c0]=1;used[off:off+size]=1
    weights[r0:r1,c0]=np.array(b['codebook_uint8'],np.uint8)[v]
assert coverage.all() and used.all() and sha(weights.tobytes())==record['reconstructed_sha256']
w2=json.loads((R/'overnight-20261014/fabric-k64/results.json').read_text())['identity']
assert sha(indices.tobytes())==w2['indices_unpacked_sha256']
rtl_path=R/'overnight-20261014/fabric-k64/rtl/index_fabric.sv'
rows=re.findall(r"frozen_rows\[(\d+)\]=1280'h([0-9a-f]+);",rtl_path.read_text())
assert len(rows)==1280
for row,h in rows:
    v=int(h,16)
    assert all(int(indices[int(row),c])==((v>>(4*c))&15) for c in range(320))
np.save(W/'indices.npy',indices)
identity={'packed_sha256':sha(packed),'manifest_sha256':sha((candidate/'candidate.json').read_bytes()),'indices_sha256':sha(indices.tobytes()),'reconstructed_weight_sha256':sha(weights.tobytes()),'w2b_rtl_sha256':sha(rtl_path.read_bytes()),'positions_compared_to_w2b':int(indices.size),'bits_compared_to_w2b':int(indices.size*4),'pass':True,'mapping':'frozen_index_bits[4*lane+bit]; row-major logical tensor; packed file is block-major, low nibble first'}
(W/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')

# Retain original rules, dimensions, contacts, implants, taps and strap corridors.
source=R/'experiments/taalas-access/mask-index-comparator/generate_layout.py'
s=source.read_text().replace('import pya','import klayout.db as pya')
s=s[:s.index('layout.write(')]
start=s.index('        code=(row+3*output)%16');end=s.index('for row,oy in enumerate(y_positions):',start)
s=s[:start]+s[end:]
os.environ['TAALAS_ARRAY_ROWS']='64';os.environ['TAALAS_ARRAY_COLS']='320'
ns={'__file__':str(O/'reused-generator.py')};exec(compile(s,str(source),'exec'),ns)
layout=ns['layout'];base=ns['cell'];base.name='RV_INDEX_BASE_64_320'
center=ns['center'];ys=ns['y_positions'];top=layout.create_cell('RV_K64_CELL_ARRAY_CORE')
tiles=[]
for group in range(20):
    mask=layout.create_cell(f'RV_K64_MASK_{group:02d}')
    for row,y in enumerate(ys):
        for bc in range(1280):
            col,bit=divmod(bc,4);x=center(bc)
            if (int(indices[group*64+row,col])>>bit)&1:
                mask.shapes(layout.layer(35,0)).insert(pya.DBox(x-.13,y+.85,x+.13,y+1.11))
            else:
                mask.shapes(layout.layer(34,10)).insert(pya.DText(f'OPEN_R{row}_C{col}_B{bit}',pya.DTrans(x,y+.98)))
    tile=layout.create_cell(f'RV_K64_CELL_TILE_{group:02d}')
    for child in [base,mask]:tile.insert(pya.CellInstArray(child.cell_index(),pya.Trans()))
    top.insert(pya.CellInstArray(tile.cell_index(),pya.Trans((group%4)*946000,(group//4)*128000)))
    tiles.append(tile)
opt=pya.SaveLayoutOptions();opt.select_cell(tiles[0].cell_index());layout.write(str(O/'tile0.gds'),opt)
layout.write(str(O/'array-core.gds'))

# Re-open emitted GDS; inspect real Via1 polygons at each programmed site.
rd=pya.Layout();rd.read(str(O/'array-core.gds'));decoded=np.zeros_like(indices)
for group in range(20):
    tile=rd.cell(f'RV_K64_CELL_TILE_{group:02d}')
    via=pya.Region(tile.begin_shapes_rec(rd.layer(35,0)))
    centers={(p.bbox().center().x,p.bbox().center().y) for p in via.each()}
    for row,y in enumerate(ys):
        for bc in range(1280):
            x=center(bc)
            if (round(x*1000),round((y+.98)*1000)) in centers:
                col,bit=divmod(bc,4);decoded[group*64+row,col] |= 1<<bit
assert np.array_equal(decoded,indices)
b=tiles[0].dbbox();f=top.dbbox()
result={'status':'cell_array_only','original_generator_sha256':sha(source.read_bytes()),'tile_count':20,'rows_per_tile':64,'lanes':320,'bits_per_lane':4,'tile_bit_cells':81920,'total_selections':409600,'total_bit_cells':1638400,'tile_bounds_um':[b.left,b.bottom,b.right,b.top],'tile_dimensions_um':[b.width(),b.height()],'tile_area_um2':b.width()*b.height(),'cell_only_um2_per_selection':b.width()*b.height()/20480,'sum_tile_area_um2':20*b.width()*b.height(),'composition_dimensions_um':[f.width(),f.height()],'composition_area_um2':f.width()*f.height(),'layout_to_bits':{'compared_bits':1638400,'mismatches':0,'decoded_indices_sha256':sha(decoded.tobytes()),'method':'reopened GDS recursive Via1 polygon center membership at actual drain sites; independent of mask cell names'},'exclusions':['decoder','wordline and precharge drivers','precharge/sense/keeper','output latches','bank-selection mux','intertile wiring','PDN'],'sha256':{p.name:sha(p.read_bytes()) for p in [O/'tile0.gds',O/'array-core.gds']}}
(O/'geometry.json').write_text(json.dumps(result,indent=2)+'\n')
print('W5-STATUS: real mask generation and GDS bit readback PASS',json.dumps(result))
