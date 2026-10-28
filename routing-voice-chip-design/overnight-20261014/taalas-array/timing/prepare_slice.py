from pathlib import Path
import hashlib,json,re
import numpy as np
W=Path(__file__).resolve().parent
R=W.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'models/candidates/codebook-4bit-optimal-rectangular-k64/packed/encoder.ort-095.indices.bin'
packed=p.read_bytes()
record=json.loads((R/'overnight-20261014/fabric-k64/evidence/selected-record.json').read_text())
ix=np.zeros((1280,320),np.uint8);covered=np.zeros_like(ix)
for block in record['blocks']:
 r0,r1=block['rows'];c0,c1=block['columns'];offset=block['index_offset'];size=block['index_bytes']
 x=np.frombuffer(packed[offset:offset+size],dtype=np.uint8)
 values=np.empty(x.size*2,np.uint8);values[0::2]=x&15;values[1::2]=x>>4
 assert c1-c0==1 and not covered[r0:r1,c0:c1].any()
 ix[r0:r1,c0]=values[:r1-r0];covered[r0:r1,c0:c1]=1
assert covered.all()
identity=json.loads((R/'overnight-20261014/fabric-k64/evidence/identity.json').read_text())
assert sha(p)==identity['packed_sha256']
assert hashlib.sha256(ix.tobytes()).hexdigest()==identity['indices_unpacked_sha256']
rtl=R/'overnight-20261014/fabric-k64/rtl/index_fabric.sv'
rows=re.findall(r"frozen_rows\[(\d+)\]=1280'h([0-9a-f]+)",rtl.read_text())
assert len(rows)==1280
for r,h in rows:
 n=int(h,16)
 assert all(int(ix[int(r),c])==((n>>(4*c))&15) for c in range(320))
# Highest connected-drain count among all 20 row tiles and 10 local 32-lane banks.
# This is a capacitance-risk proxy, not a proven worst timing corner.
candidates=[]
for tile in range(20):
 for bank in range(10):
  data=ix[tile*64:(tile+1)*64,bank*32:(bank+1)*32]
  pop=((data[:,:,None]>>np.arange(4))&1).sum(axis=0)
  pos=np.unravel_index(pop.argmax(),pop.shape)
  candidates.append((int(pop.max()),int(pop.sum()),tile,bank,int(pos[0]),int(pos[1])))
chosen=max(candidates);_,_,tile,bank,col,bit=chosen
data=ix[tile*64:(tile+1)*64,bank*32:(bank+1)*32]
(W/'indices.json').write_text(json.dumps(data.tolist()))
report={'source_packed':str(p.relative_to(R)),'packed_sha256':sha(p),'rtl_sha256':sha(rtl),'w2b_unpacked_hash_matches':True,'rtl_indices_compared':409600,'tile':tile,'bank':bank,'global_row_start':tile*64,'global_column_start':bank*32,'maximum_connected_drains':chosen[0],'total_connected_drains':chosen[1],'maximum_population_local_column':col,'maximum_population_bit':bit,'selection_basis':'Maximum connected-drain population over 20*10 real 64x32 banks; tie break total connected drains. Proxy for load, not electrically proven worst-case. All 64 rows physically present; bounded transient rows reported separately.'}
(W/'slice-identity.json').write_text(json.dumps(report,indent=2)+'\n')
src=R/'experiments/taalas-access/mask-index-comparator/generate_layout.py'
s=src.read_text().replace('ROWS=int(os.environ.get("TAALAS_ARRAY_ROWS","16"))','ROWS=64').replace('OUTPUTS=int(os.environ.get("TAALAS_ARRAY_COLS","4"))','OUTPUTS=32')
s=s.replace('if (ROWS,OUTPUTS)!=(16,4):\n    HERE=HERE/f"r{ROWS}-c{OUTPUTS}"\n    HERE.mkdir(exist_ok=True)','IMAGE=json.loads((HERE/"indices.json").read_text())')
s=s.replace('code=(row+3*output)%16','code=IMAGE[row][output]').replace('"synthetic_index":"(row+3*output) mod 16",','"actual_image":"indices.json",')
(W/'generate_slice.py').write_text(s)
print(json.dumps(report,indent=2))
