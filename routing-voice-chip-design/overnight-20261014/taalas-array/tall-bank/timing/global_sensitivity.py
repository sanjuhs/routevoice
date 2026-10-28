"""Unplaced distributed stock drivers plus measured fullbank WL/PC load sensitivity."""
from pathlib import Path
import argparse,json,re,hashlib,shutil
import simulate as s
W=Path(__file__).resolve().parent;BASE=s.build;CAP=W.parent/'verification/bank3-v1/control-capacitance.json'
def build(O,corner,vdd,temp,period,segments):
 lines,names,meta,image=BASE(O,corner,vdd,temp,period,segments);globalcap=json.loads(CAP.read_text());ex=json.loads((O/'extraction.json').read_text());G=ex['subbank'];sheet=meta['metal_sheet_ohm_square'];active=meta['active_rows'];extras=[];new=[];capby={};joined=s.caps((O/'joined-canonical.spice').read_text().splitlines())
 for net in ['PC']+[f'WL{row}' for row in active]:capby[net]=sum(v for pair,v in joined.items() if net in pair)
 def pcnode(g):return 'pc' if g==G else f'pcglobal{g}'
 def wlrail(row,g):return f'wlrail{row}g{g}'
 def wlcell(row,g):return f'wl{row}' if g==G else f'wl{row}g{g}'
 for l in lines:
  f=l.split()
  if l.startswith('Xpcdrv '):
   for g in range(10):new.append(' '.join([f[0]+f'g{g}']+[pcnode(g) if n=='pc' else n for n in f[1:]]))
  elif (m:=re.match(r'Xwdrv(\d+) ',l)):
   row=int(m[1])
   for g in range(10):new.append(' '.join([f[0]+f'g{g}']+[wlrail(row,g) if n==f'wd{row}' else n for n in f[1:]]))
  elif (m:=re.match(r'Rwl(\d+) ',l)):
   row=int(m[1]);new.append(f'Rwl{row} {wlrail(row,G)} wl{row} {f[-1]}')
  else:new.append(l)
 for g in range(10):
  if g:
   extras.append(f'Rpcglobal{g} {pcnode(g-1)} {pcnode(g)} {sheet*468/.38:g}')
  addpc=globalcap['controls']['PC']['incident_capacitance_ff']-capby['PC'];assert addpc>=0
  extras.append(f'Cpcglobal{g} {pcnode(g)} 0 {addpc/10:g}f')
  if g!=G:
   for j in range(128):extras.append(s.mos(f'pcdummy{g}_{j}','rdd',pcnode(g),'rdd','rdd','pfet',2.88))
  for row in active:
   if g:extras.append(f'Rwlglobal{row}_{g} {wlrail(row,g-1)} {wlrail(row,g)} {sheet*468/.38:g}')
   addwl=globalcap['controls'][f'WL{row}']['incident_capacitance_ff']-capby[f'WL{row}'];assert addwl>=0
   extras.append(f'Cwlglobal{row}_{g} {wlrail(row,g)} 0 {addwl/10:g}f')
   if g!=G:
    extras.append(f'Rwlbranch{row}_{g} {wlrail(row,g)} {wlcell(row,g)} {sheet*93.68/.38:g}')
    for j in range(128):extras.append(s.mos(f'wldummy{row}_{g}_{j}','0',wlcell(row,g),'0','0','nfet',.36))
 names += [pcnode(g) for g in range(10) if g!=G]+[wlcell(row,g) for row in active for g in range(10) if g!=G]
 start=new.index('.control');new[start:start]=extras
 for i,l in enumerate(new):
  if l.startswith('wrdata trace.dat '):new[i]='wrdata trace.dat '+' '.join(n if n in ['pr','pw','pp','pa'] else f'v({n})' for n in names)
 meta['phase_precharge_nodes']=[pcnode(g) for g in range(10)];meta['phase_wordline_nodes']=[wlcell(row,g) for row in active for g in range(10)]
 meta['global_loading_sensitivity']={'control_caps_source':str(CAP),'control_caps_json_sha256':hashlib.sha256(CAP.read_bytes()).hexdigest(),'full_extracted_cap_sha256':globalcap['source_sha256'],'physical_gate_counts':{'selected_WL':1280,'PC':1280},'added_gate_loads':{'access_nmos_peractiveWL':1152,'precharge_pmos':1152},'driver_counts':{'buf4_peractiveWL':10,'buf20_PC':10},'global_rail_model':'10nodes at468umspacing; .38um M3; geometryR0.104Ohm/square tempco.00333/K; added measured fullbank-minuslocal explicit incidentC evenly allocated10nodes toground','full_control_cap_ff':{n:globalcap['controls'][n]['incident_capacitance_ff'] for n in capby},'retained_local_control_cap_ff':capby,'qualifications':['Drivers are unplaced ideal-distributed instances with common ideal command inputs; no verified broadcast-input delivery or actual driver location','Other9subbank gate loads use groundedS/D accessMOS and VDD-tiedS/D prechargePMOS; not exact active-array Miller/current loading','Global incidentC collapsed toground for sensitivity, not exact distributed coupling extraction','All10PC and all10localWL terminal phase margins checked; only selected16real-array columns have data/precharge checks','rdd energy now includes1152dummy prechargegate displacement currents; still not fullbank energy']}
 meta['scope']='Full320lane WL/PC loading sensitivity with measured controlmetalC, geometryglobalrailR,10unplacedstockdrivers percontrol anddummyothergate loads. Data/current remain16actual columns and128physicalreceivers; not physically placed fullbank qualification.'
 return new,names,meta,image
s.build=build
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--directory',default='r320-global-load-v1');p.add_argument('--corner',choices=['typical','ss'],required=True);p.add_argument('--period',type=float,required=True);a=p.parse_args();D=W/a.directory/f'{a.corner}-{a.period:g}ns-s32';D.mkdir(parents=True,exist_ok=True);shutil.copyfile(Path(__file__),D/'source-global-sensitivity.py');s.run(W/a.directory,a.corner,a.period,32)
