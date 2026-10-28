from pathlib import Path
import numpy as np,json,hashlib
W=Path(__file__).resolve().parent;A=W.parents[1];idx=np.load(A/'indices.npy');assert idx.shape==(1280,320)
records=[]
for height in [320,1280]:
 for bank in range(1280//height):
  bits=((idx[bank::1280//height,:,None]>>np.arange(4))&1).reshape(height,1280)
  for subbank in range(10):
   for strap in range(8):
    start=subbank*128+strap*16;b=bits[:,start:start+16];pop=b.sum(0);peak=int(pop.argmax());far=np.flatnonzero(b[:,peak]);zeros=np.flatnonzero(~b[:,peak].astype(bool))
    # Highest population then full16column group loading; farthest connected1 stresses read path.
    records.append({'rows':height,'bank':bank,'global_row_formula':f'{bank}+{1280//height}*localrow','subbank':subbank,'global_lane_range':[subbank*32,(subbank+1)*32],'strap_group':strap,'local_bit_columns':list(range(strap*16,(strap+1)*16)),'max_connected_drains':int(pop.max()),'group_connected_drains':int(pop.sum()),'population_by_selected_column':[int(v) for v in pop],'peak_local_bit_column':strap*16+peak,'farthest_peak_one_row':int(far[-1]),'farthest_peak_zero_row':int(zeros[-1]),'all16_active_count_max':int(b.sum(1).max())})
ranked={}
for height in [320,1280]:
 r=sorted((d for d in records if d['rows']==height),key=lambda d:(d['max_connected_drains'],d['group_connected_drains']),reverse=True);ranked[str(height)]=r
pick=ranked['320'][0];height=320;off=pick['bank'];cols=pick['local_bit_columns'];g=pick['subbank'];b=((idx[off::4,g*32:(g+1)*32,None]>>np.arange(4))&1).reshape(320,128)[:,cols]
# Six-row repeated sequence covers near/far, most simultaneous discharges, and adjacent-transition stress.
peakrow=int(b.sum(1).argmax());transition=int(np.count_nonzero(b[1:]!=b[:-1],axis=1).argmax())
rows=[]
for r in [0,pick['farthest_peak_one_row'],pick['farthest_peak_zero_row'],peakrow,transition,transition+1,318,319]:
 if r not in rows:rows.append(r)
report={'indices_sha256':hashlib.sha256((A/'indices.npy').read_bytes()).hexdigest(),'unpacked_indices_sha256':hashlib.sha256(idx.astype(np.uint8).tobytes()).hexdigest(),'mapping':'striped banks, global_row=bank+(1280//height)*localrow','criterion':'Highest connected drain population per column, then highest total population in its actual shared-ground16column group; provisional until extracted-cap ranking. Not exhaustive worst-case guarantee.','selected320':pick,'sampled_rows320':rows,'ranked':ranked}
(W/'selection.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='ranked'},indent=2))
