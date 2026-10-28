"""Exact signed incident-C pair comparison: fullbank versus retained crop."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import argparse,gzip,hashlib,json,re
W=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--crop',required=True);p.add_argument('--ranking',default='fullbank-caps/rank.json');a=p.parse_args();O=W/a.crop;ranking=W/a.ranking;R=json.loads(ranking.read_text());target=R['ranking'][0];globalbit=target['bit_column'];g=globalbit//128
assert json.loads((O/'extraction.json').read_text())['subbank']==g
candidate=f'IDX{globalbit//4}_{globalbit%4}';units={'':Decimal('1e15'),'f':Decimal(1),'p':Decimal(1000),'n':Decimal(1000000),'u':Decimal(1000000000),'m':Decimal('1e12')}
def value(s):
 m=re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)([fpnum]?)',s);assert m,s
 return Decimal(m[1])*units[m[2]]
def norm(n,local):
 n=n.rsplit('.',1)[-1]
 if local:
  if (m:=re.fullmatch(r'IDX(\d+)_(\d)',n)):return f'IDX{int(m[1])+g*32}_{m[2]}'
  if (m:=re.fullmatch(r'OUT(\d+)',n)):return f'OUT{int(m[1])+g*128}'
  if (m:=re.fullmatch(r'OPEN_R(\d+)_C(\d+)_B(\d)',n)):return f'OPEN_R{m[1]}_C{int(m[2])+g*32}_B{m[3]}'
 return n
full=defaultdict(Decimal);crop=defaultdict(Decimal);source=Path(R['source_spice'])
for path,local,collection in [(source,False,full),(O/'joined-canonical.spice',True,crop)]:
 opener=gzip.open if path.suffix=='.gz' else open
 with opener(path,'rt') as f:
  for line in f:
   if not line.startswith('C'):continue
   _,x,y,v=line.split();x,y=norm(x,local),norm(y,local)
   if candidate not in [x,y]:continue
   assert x!=y;other=y if x==candidate else x;collection[other]+=value(v)
fulltotal=sum(full.values());croptotal=sum(crop.values());assert abs(float(fulltotal)-target['capacitance_ff'])<1e-8
records=[]
def category(n):
 if (m:=re.fullmatch(r'IDX(\d+)_(\d)',n)):return 'local_bitline' if int(m[1])//32==g else 'remote_bitline'
 if (m:=re.fullmatch(r'OUT(\d+)',n)):return 'local_output' if int(m[1])//128==g else 'remote_output'
 if (m:=re.fullmatch(r'OPEN_R(\d+)_C(\d+)_B(\d)',n)):return 'local_open_drain' if int(m[2])//32==g else 'remote_open_drain'
 if n.startswith('WL') or n in ['PC','VSS','VDD']:return 'common_control_or_supply'
 return 'other'
for other in sorted(set(full)|set(crop)):
 f,c=full[other],crop[other];records.append({'other_node':other,'category':category(other),'full_ff':str(f),'crop_ff':str(c),'delta_full_minus_crop_ff':str(f-c)})
by=defaultdict(lambda:{'full_ff':Decimal(0),'crop_ff':Decimal(0),'delta_ff':Decimal(0),'pairs':0})
for r in records:
 q=by[r['category']];q['full_ff']+=Decimal(r['full_ff']);q['crop_ff']+=Decimal(r['crop_ff']);q['delta_ff']+=Decimal(r['delta_full_minus_crop_ff']);q['pairs']+=1
report={'timing_candidate_global_bit':globalbit,'group':g,'full_incident_cap_ff':float(fulltotal),'crop_incident_cap_ff':float(croptotal),'delta_full_minus_crop_ff':float(fulltotal-croptotal),'relative_delta_percent':float((fulltotal-croptotal)/fulltotal*100),'pair_categories':{n:{k:str(v) if isinstance(v,Decimal) else v for k,v in q.items()} for n,q in by.items()},'changed_pair_count':sum(Decimal(r['delta_full_minus_crop_ff'])!=0 for r in records),'pairs':records,'fullrank_sha256':hashlib.sha256(ranking.read_bytes()).hexdigest(),'fullcap_uncompressed_sha256':R['source_uncompressed_sha256'],'crop_canonical_spice_sha256':hashlib.sha256((O/'joined-canonical.spice').read_bytes()).hexdigest(),'qualification':'Exact signed pair sums from official fullbank export and actual selected joined-subbank crop. No cap delta added to simulation. Neither sign of incident-C delta nor equality proves conservative transient behavior, actual global control timing, fullbank current or distributed parasitic equivalence.'}
(O/'fullbank-vs-crop-capacitance.json').write_text(json.dumps(report,indent=2)+'\n');print('W6-STATUS: fullbank versus cropped candidate capacitance', {k:v for k,v in report.items() if k!='pairs'},flush=True)
