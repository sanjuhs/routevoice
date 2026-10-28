from pathlib import Path
import re,json,sys,argparse,hashlib,numpy as np
from simulate import caps,parsed
W=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('directory');p.add_argument('--global-bit',type=int);p.add_argument('--global-rank-source');p.add_argument('--candidate-kind',choices=['fullbank_rc','connected_drains'],default='fullbank_rc');a=p.parse_args();O=W/a.directory;image=np.load(O/'image.npy');geo=json.loads((O/'source-geometry.json').read_text());H=len(image);incident=np.zeros(128)
for pair,value in caps((O/'joined-canonical.spice').read_text().splitlines()).items():
 for net in pair:
  kind,n,row=parsed(net)
  if kind=='BL':incident[n]+=value
pop=((image[:,:,None]>>np.arange(4))&1).reshape(H,128).sum(0);height=2+H*1.44+(H//8-1)*1.8+.65+.8-.5;rarray=.104*height/.38;ranking=[]
for n in range(128):
 route=geo['join_routes_subbank0'][n];assert route['bc']==n;length=sum(route[f'metal{i}_length_um'] for i in [2,3,4]);r=.104*length/.38+60
 ranking.append({'local_bit_column':n,'extracted_incident_metal_cap_ff':float(incident[n]),'connected_drains':int(pop[n]),'join_geometry_length_um':length,'join_ohm_at25c':r,'array_ohm_at25c':rarray,'rank_score_ohm_ff':float(incident[n]*(r+rarray/2))})
ranking.sort(key=lambda d:d['rank_score_ohm_ff'],reverse=True);peak=ranking[0]['local_bit_column']
if a.global_bit is not None:
 ex=json.loads((O/'extraction.json').read_text());assert a.global_bit//128==ex['subbank'];assert a.global_rank_source;peak=a.global_bit%128
selected=list(range(peak//16*16,peak//16*16+16));res={'method':'Rank all128local columns by extracted total incident metalC*(actual W6 stacked joinR+half fullheight arrayR), with connected-drain count separately. Initial group selected from all1280 by drain-population+geometryR proxy. Two-stage heuristic candidate, not absolute transistor-timing worst-case proof.','selected':selected,'selected_peak_local_bit':peak,'forced_global_peak':a.global_bit,'global_rank_source':a.global_rank_source,'global_rank_source_sha256':hashlib.sha256(Path(a.global_rank_source).read_bytes()).hexdigest() if a.global_rank_source else None,'ranking':ranking,'scope':'Actual new stacked128-column subbank only; rest of1280 columns not cap-extracted.'};
if a.global_bit is not None:
 res['method']='Selected column is the highest all1280-column full-bank extractedC/R proxy candidate from the separately hashed global ranking; actual local128-column extraction/ranking retained as a contextual comparison. Not an exhaustive transistor-timing worst-case proof.'
 res['scope']='Global fullbank ranking selects target; new local128-column extraction supplies timing circuit. Actual fullbank control loads and simultaneous current remain excluded from primary timing.'
 if a.candidate_kind=='connected_drains':
  res['method']='Selected column has the maximum connected-drain population among all1280 real-index bit columns; independently extracted local128-column C/R ranking retained for context. This candidate is distinct from the metal-C/R proxy maximum and is not proven worst transient.'
  res['scope']='Additional maximum-drain candidate characterized with actual cropped layout MOS/C and geometryR; fullbank current/control implementation excluded.'
res['candidate_kind']=a.candidate_kind if a.global_bit is not None else 'local_rc'
(O/'cap-ranking.json').write_text(json.dumps(res,indent=2));print('W6-STATUS: extracted candidate ranking',json.dumps({'selected':selected,'top5':ranking[:5]},indent=2))
bits=((image[:,:,None]>>np.arange(4))&1).reshape(H,128);one=np.flatnonzero(bits[:,peak]);zero=np.flatnonzero(~bits[:,peak].astype(bool));rows=[]
for row in [int(one[0]),int(zero[0]),int(one[-1]),int(zero[-1]),int(bits[:,selected].sum(axis=1).argmax())]:
 if row not in rows:rows.append(row)
(O/'pattern-override.json').write_text(json.dumps({'rows':rows,'scope':'Repeated near/far1/0 of explicitly selected candidate plus maximum simultaneous selected-column discharge row. Not exhaustive transitions.'},indent=2))
