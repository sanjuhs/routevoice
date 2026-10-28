from pathlib import Path
import re,json,hashlib
import numpy as np
W=Path(__file__).resolve().parent;data=np.load(W/'vectors/model.npz')
s=(W/'rtl/index_fabric.sv').read_text()
rows=re.findall(r"frozen_rows\[(\d+)\]=1280'h([0-9a-f]+);",s)
assert len(rows)==1280 and len({int(x[0]) for x in rows})==1280
for rs,h in rows:
 vals=np.array([(int(h,16)>>(4*j))&15 for j in range(320)],dtype=np.uint8)
 np.testing.assert_array_equal(vals,data['indices'][int(rs)])
s=(W/'rtl/engine.sv').read_text()
books=re.findall(r"9'd(\d+): representative_map_(\d+)=8'd(\d+);",s)
assert len(books)==102400 and len({(x,y) for x,y,z in books})==102400
for address,column,value in books:
 a=int(address);assert int(value)==int(data['books'][a//16,int(column),a%16])
zp=re.findall(r"9'd(\d+): zero_point=8'd(\d+);",s)
assert len(zp)==320
for col,v in zp:assert int(v)==int(data['zero'][int(col)])
meta=re.findall(r"9'd(\d+):begin weight_scale=32'h([0-9a-f]+);bias=32'h([0-9a-f]+);end",(W/'rtl/metadata.sv').read_text())
assert len(meta)==320
for col,scale,bias in meta:
 c=int(col);assert int(scale,16)==data['weight_scale'].view(np.uint32)[c] and int(bias,16)==data['bias'].view(np.uint32)[c]
out={'pass':True,'rtl_index_positions_compared':409600,'rtl_book_entries_compared':102400,'zero_points_compared':320,'weight_scales_compared':320,'biases_compared':320,'source':'Independent regex reader of emitted RTL constants compared with executable/manifest-derived NPZ','rtl_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'rtl').glob('*.sv')}}
(W/'evidence/rtl-constant-audit.json').write_text(json.dumps(out,indent=2));print('W2b-STATUS: RTL constant audit PASS: all 409600 indices, 102400 representatives and 960 metadata constants')
