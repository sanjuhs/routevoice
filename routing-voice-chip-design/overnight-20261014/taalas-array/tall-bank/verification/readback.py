"""Reopen saved GDS and independently decode actual programmed Via1 sites.

Array-cell names identify hierarchy only; bit values come exclusively from GDS.
Coordinates are the reviewed reused tall-bank generator's access-drain sites.
"""
from pathlib import Path
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
import klayout.db as k
import numpy as np
from verify import P,image,sha
p=argparse.ArgumentParser();p.add_argument('--gds',required=True);p.add_argument('--rows',type=int,default=320);p.add_argument('--bank',type=int,nargs='+',default=[0,1,2,3]);p.add_argument('--output',required=True);a=p.parse_args()
output=P/a.output;assert output.parent.resolve()==P.resolve() and not output.exists(),'Use a fresh local output filename'
gds=Path(a.gds).resolve();l=k.Layout();l.read(str(gds));idx,identity=image();records=[]
assert a.rows in (320,1280)
banks=1280//a.rows
for bank in a.bank:
 assert 0<=bank<banks
 observed=np.zeros((a.rows,320),np.uint8);ones=0
 for group in range(10):
  cell=l.cell(f'TALL_ARRAY_B{bank:02d}_G{group:02d}');assert cell is not None,(bank,group)
  region=k.Region(cell.begin_shapes_rec(l.layer(35,0)));centers={(p.bbox().center().x,p.bbox().center().y) for p in region.each()}
  for row in range(a.rows):
   y=2+row*1.44+(row//8)*1.8+.98
   for local in range(128):
    group16,off=divmod(local,16);x=2+group16*(16*.66+1)+off*.66+.33
    if (round(x/l.dbu),round(y/l.dbu)) in centers:
     lane,bit=divmod(group*128+local,4);observed[row,lane]|=1<<bit;ones+=1
 expected=idx[bank::banks,:];xor=observed^expected;bad=int(np.count_nonzero(xor));bitbad=sum(int(v).bit_count() for v in xor.ravel())
 record=dict(bank=bank,compared_selections=int(observed.size),compared_bits=int(observed.size*4),selection_mismatches=bad,bit_mismatches=bitbad,programmed_ones=ones,observed_sha256=hashlib.sha256(observed.tobytes()).hexdigest(),expected_sha256=hashlib.sha256(expected.tobytes()).hexdigest());records.append(record)
report=dict(gds=str(gds),gds_sha256=sha(gds),identity=identity,rows_per_bank=a.rows,row_mapping=f'logical_row=bank+{banks}*local_row',method='Reopened GDS recursive Via1 polygon centers at reviewed transistor drain coordinates; not label or mask-cell-name values',banks=records,all_match=all(x['bit_mismatches']==0 for x in records))
output.write_text(json.dumps(report,indent=2)+'\n');print('W5-STATUS: independent tall-bank GDS bit-readback',report,flush=True);assert report['all_match']
