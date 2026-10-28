from pathlib import Path
import json,re,hashlib
W=Path(__file__).resolve().parent;P=W.parent/'verification/bank3-v1/control-capacitance.json';x=json.loads(P.read_text());rank=[]
for name,entry in x['bitlines'].items():
 m=re.fullmatch(r'IDX(\d+)_(\d)',name);lane,bit=int(m[1]),int(m[2]);bc=lane%32*4+bit;q,local=divmod(bc,16);ax=10+2+q*11.56+local*.66+.33;rx=10+bc*3.5+2.24;y=14+.66*bc;length=112+.5-y+abs(rx-ax)+y-2;r=.104*length/.38+60;ra=.104*533.95/.38
 rank.append({'net':name,'subbank':lane//32,'local_bit_column':bc,'incident_capacitance_ff':entry['incident_capacitance_ff'],'connected_drains':entry['access_connected_drains'],'join_ohm_at25c':r,'rank_score_ohm_ff':entry['incident_capacitance_ff']*(r+ra/2)})
rank.sort(key=lambda d:d['rank_score_ohm_ff'],reverse=True);(W/'fullbank3-ranking.json').write_text(json.dumps({'source':str(P),'source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'scope':'All1280columns ofphysical320row stripedbank3 only; other3banks notcapextracted','method':'IncidentmetalC times(joinR+halfarrayR), geometryR same perlocalcolumn; intrinsicjunction/driver/mismatch notpartofrank','ranking':rank},indent=2));print(json.dumps(rank[:8],indent=2))
