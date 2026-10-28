"""Stream official full-bank ext2spice C output and rank every bitline.

Ranking is an engineering load/RC proxy, not proof of global dynamic worst case.
No source capacitors are clipped or silently omitted by this reader.
"""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import argparse,gzip,hashlib,json,re,sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'verification'))
from verify import image
P=Path(__file__).resolve().parent/'fullbank-caps'
p=argparse.ArgumentParser();p.add_argument('--spice',required=True);p.add_argument('--geometry',required=True);p.add_argument('--output',required=True);p.add_argument('--extraction-input');a=p.parse_args()
src=Path(a.spice).resolve();geo=Path(a.geometry).resolve();out=P/a.output
assert out.parent.resolve()==P.resolve() and not out.exists()
g=json.loads(geo.read_text());H=g['rows'];assert H==1280
extraction_input_path=Path(a.extraction_input) if a.extraction_input else src.parent/'input.json'
extraction_input=json.loads(extraction_input_path.read_text())
assert extraction_input['gds_sha256']==g['gds_sha256']
assert extraction_input['rows']==H
idx,identity=image()
values=[dict(total=Decimal(0),positive=Decimal(0),negative=Decimal(0),count=0,zero=0,negative_count=0) for _ in range(1280)]
control_values={n:dict(total=Decimal(0),positive=Decimal(0),negative=Decimal(0),count=0,zero=0,negative_count=0) for n in ['PC']+[f'WL{i}' for i in range(H)]}
control_names={}
units={'':Decimal('1e15'),'f':Decimal(1),'p':Decimal(1000),'n':Decimal(1000000),'u':Decimal(1000000000),'m':Decimal('1e12')}
counts=Counter();netmap={};reverse={};digest=hashlib.sha256()
def bit(n):
 short=n.rsplit('.',1)[-1]
 m=re.fullmatch(r'IDX(\d+)_(\d)',short)
 if not m:return None
 c,b=map(int,m.groups());assert 0<=c<320 and 0<=b<4
 assert short not in reverse or reverse[short]==n,('Non-bijective BL name',short,n,reverse.get(short))
 netmap[n]=short;reverse[short]=n
 return 4*c+b
opener=gzip.open if src.suffix=='.gz' else open
with opener(src,'rb') as f:
 for raw in f:
  digest.update(raw)
  if not raw.startswith(b'C'):continue
  fields=raw.decode().split();assert len(fields)==4,fields
  _,n1,n2,token=fields
  m=re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)([fpnum]?)',token);assert m,token
  value=Decimal(m[1])*units[m[2]]
  counts['all_records']+=1
  counts['zero_records']+=value==0;counts['negative_records']+=value<0
  i1,i2=bit(n1),bit(n2)
  assert i1 is None or i1!=i2,('Self capacitor',fields)
  if i1 is not None or i2 is not None:counts['records_incident_to_bitlines']+=1
  for i in (i1,i2):
   if i is None:continue
   v=values[i];v['total']+=value;v['count']+=1;v['zero']+=value==0
   if value>0:v['positive']+=value
   if value<0:v['negative']+=value;v['negative_count']+=1
  for node in (n1,n2):
   short=node.rsplit('.',1)[-1]
   if short not in control_values:continue
   assert short not in control_names or control_names[short]==node,('Non-bijective control name',short)
   control_names[short]=node;v=control_values[short]
   v['total']+=value;v['count']+=1;v['zero']+=value==0
   if value>0:v['positive']+=value
   if value<0:v['negative']+=value;v['negative_count']+=1
assert len(reverse)==1280,len(reverse)
assert len(control_names)==H+1,len(control_names)
routes={r['bc']:r for r in g['join_routes_subbank0']};assert len(routes)==128
array_length=2+H*1.44+(H//8-1)*1.8+.65+.8-.5
array_r=.104*array_length/.38
rank=[]
for i,v in enumerate(values):
 c,b=divmod(i,4);route=routes[i%128]
 join_length=sum(route[f'metal{m}_length_um'] for m in (2,3,4))
 join_r=.104*join_length/.38+15*(route['via2_count']+route['via3_count'])
 programmed=((idx[:,c]>>b)&1)
 rank.append(dict(bit_column=i,group=i//128,local_bit_column=i%128,lane=c,bit=b,
  receiver_row=i%8,capacitance_ff=float(v['total']),capacitance_ff_decimal=str(v['total']),
  positive_capacitance_ff=float(v['positive']),negative_capacitance_ff=float(v['negative']),
  incident_capacitor_records=v['count'],zero_records=v['zero'],negative_records=v['negative_count'],
  connected_drains=int(programmed.sum()),join_resistance_ohm=join_r,array_resistance_ohm=array_r,
  rc_proxy_ps=float(v['total'])*(join_r+.5*array_r)*.001,
  full_extracted_node=reverse[f'IDX{c}_{b}']))
rank.sort(key=lambda r:(r['rc_proxy_ps'],r['capacitance_ff']),reverse=True)
controls={n:dict(capacitance_ff=float(v['total']),capacitance_ff_decimal=str(v['total']),positive_capacitance_ff=float(v['positive']),negative_capacitance_ff=float(v['negative']),incident_records=v['count'],zero_records=v['zero'],negative_records=v['negative_count'],full_extracted_node=control_names[n]) for n,v in control_values.items()}
report=dict(source_spice=str(src),source_uncompressed_sha256=digest.hexdigest(),geometry=str(geo),
 geometry_sha256=hashlib.sha256(geo.read_bytes()).hexdigest(),gds_sha256=g['gds_sha256'],
 rows=H,bitlines=1280,identity=identity,capacitor_records=dict(counts),
 method='Official Magic ext2spice cthresh0 full-bank export. Sum all signed incident SPICE C records per bitline; every raw zero/negative record is retained in counts. Checked bijective BL prefix normalization. Junction capacitance is not in this metal-C total.',
 resistance_proxy='Rjoin=.104ohm/sq*(Lmetal2+Lmetal3+Lmetal4)/.38um +15ohm*(via2_count+via3_count); Rarray=.104ohm/sq*array_length/.38um; score=Cincident*(Rjoin+.5Rarray). Geometry-derived proxy, not automatic distributed-R extraction.',
 qualification='Ranks all1280 full-bank metal-C/geometry-R load proxies. Does not prove worst transient delay over every row, coupling state, PVT, junction charge, or full-bank current.',
 highest_capacitance=max(rank,key=lambda r:r['capacitance_ff']),ranking=rank)
report['control_metal_capacitance']=controls
report['maximum_connected_drains']=max(r['connected_drains'] for r in rank)
report['maximum_connected_drain_columns']=[r for r in rank if r['connected_drains']==report['maximum_connected_drains']]
report['drain_count_qualification']='Independent real-index drain population, not a junction-charge measurement. Highest metal-C/geometry-R candidate can differ from highest connected-drain population; neither alone proves worst transient.'
report['maximum_wordline_metal_capacitance']=max(((n,v) for n,v in controls.items() if n.startswith('WL')),key=lambda pair:pair[1]['capacitance_ff'])
report['control_qualification']='Full-bank PC/allWL incident signed metal capacitance only. Intrinsic device gate/channel capacitance remains in the transistor models, not these explicit interconnect-C sums.'
out.write_text(json.dumps(report,indent=2)+'\n')
print('W6-STATUS: full-bank1280bitline C/RC proxy ranking',rank[0],flush=True)
