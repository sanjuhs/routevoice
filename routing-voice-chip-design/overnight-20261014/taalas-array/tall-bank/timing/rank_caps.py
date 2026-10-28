from pathlib import Path
import re,json,sys,numpy as np
from simulate import caps,parsed
W=Path(__file__).resolve().parent;O=W/(sys.argv[1] if len(sys.argv)>1 else 'r320-v1');geo=json.loads((O/'source-geometry.json').read_text());image=np.load(O/'image.npy');H=len(image);incident=np.zeros(128)
for pair,value in caps((O/'joined-canonical.spice').read_text().splitlines()).items():
 for net in pair:
  kind,n,row=parsed(net)
  if kind=='BL':incident[n]+=value
pop=((image[:,:,None]>>np.arange(4))&1).reshape(H,128).sum(0);height=2+H*1.44+(H//8-1)*1.8+.65+.8-.5;rarray=.104*height/.38;ranking=[]
for n in range(128):
 q,local=divmod(n,16);x=10+2+q*11.56+local*.66+.33;rx=10+3.5*n+2.24;y=14+n*.66;length=(112+.5-y)+abs(rx-x)+(y-2);r=.104*length/.38+60
 ranking.append({'local_bit_column':n,'extracted_incident_metal_cap_ff':float(incident[n]),'connected_drains':int(pop[n]),'join_geometry_length_um':length,'join_ohm_at25c':r,'array_ohm_at25c':rarray,'rank_score_ohm_ff':float(incident[n]*(r+rarray/2))})
ranking.sort(key=lambda d:d['rank_score_ohm_ff'],reverse=True);peak=ranking[0]['local_bit_column'];selected=list(range(peak//16*16,peak//16*16+16));res={'method':'Rank all128local columns by extracted total incident metalC*(actual joinR+half fullheight arrayR), with connected-drain count reported separately. Heuristic candidate, not absolute transistor-timing worst-case proof.','selected':selected,'ranking':ranking,'scope':'Ranks all128 columns of this actual selected joined subbank only; fullbank3 C ranking separately provided for320. Other banks are not cap-extracted.'};(O/'cap-ranking.json').write_text(json.dumps(res,indent=2));print(json.dumps({'selected':selected,'top5':ranking[:5]},indent=2))
