"""One-driver sensitivity to measured full-bank WL/PC fanout and wire load.

This retains the primary actual16-column current model; it is not fullbank SPICE.
"""
from pathlib import Path
import argparse,json,re,hashlib,shutil
import simulate as s
W=Path(__file__).resolve().parent;BASE=s.build;CAP=W/'fullbank-caps/rank.json'
def build(O,corner,vdd,temp,period,segments):
 lines,names,meta,image=BASE(O,corner,vdd,temp,period,segments)
 globalcap=json.loads(CAP.read_text());ex=json.loads((O/'extraction.json').read_text());G=ex['subbank'];sheet=meta['metal_sheet_ohm_square'];active=meta['active_rows'];extras=[];new=[];capby={};joined=s.caps((O/'joined-canonical.spice').read_text().splitlines())
 for net in ['PC']+[f'WL{row}' for row in active]:capby[net]=sum(v for pair,v in joined.items() if net in pair)
 def pcnode(g):return 'pc' if g==G else f'pcglobal{g}'
 def wlnode(row,g):return f'wl{row}' if g==G else f'wl{row}g{g}'
 for l in lines:
  f=l.split()
  if l.startswith('Xpcdrv '):new.append(' '.join([f[0]]+['pcroot' if n=='pc' else n for n in f[1:]]))
  elif re.match(r'Rwl\d+ ',l):pass
  else:new.append(l)
 extras.append(f'Rpcroot pcroot {pcnode(0)} {sheet*96.4/.38:g}')
 for row in active:extras.append(f'Rwlroot{row} wd{row} {wlnode(row,0)} {sheet*103.48/.38:g}')
 for g in range(10):
  if g:extras.append(f'Rpcglobal{g} {pcnode(g-1)} {pcnode(g)} {sheet*100/.38:g}')
  addpc=globalcap['control_metal_capacitance']['PC']['capacitance_ff']-capby['PC'];assert addpc>=0
  extras.append(f'Cpcglobal{g} {pcnode(g)} 0 {addpc/10:g}f')
  if g!=G:
   for j in range(128):extras.append(s.mos(f'pcdummy{g}_{j}','rdd',pcnode(g),'rdd','rdd','pfet',2.88))
  for row in active:
   if g:extras.append(f'Rwlglobal{row}_{g} {wlnode(row,g-1)} {wlnode(row,g)} {sheet*100/.38:g}')
   addwl=globalcap['control_metal_capacitance'][f'WL{row}']['capacitance_ff']-capby[f'WL{row}'];assert addwl>=0
   extras.append(f'Cwlglobal{row}_{g} {wlnode(row,g)} 0 {addwl/10:g}f')
   if g!=G:
    for j in range(128):extras.append(s.mos(f'wldummy{row}_{g}_{j}','0',wlnode(row,g),'0','0','nfet',.36))
 names += [pcnode(g) for g in range(10) if g!=G]+[wlnode(row,g) for row in active for g in range(10) if g!=G]
 start=new.index('.control');new[start:start]=extras
 for i,l in enumerate(new):
  if l.startswith('wrdata trace.dat '):new[i]='wrdata trace.dat '+' '.join(n if n in ['pr','pw','pp','pa'] or n.startswith('pcolumn') else f'v({n})' for n in names)
 meta['phase_precharge_nodes']=[pcnode(g) for g in range(10)];meta['phase_wordline_nodes']=[wlnode(row,g) for row in active for g in range(10)]
 meta['global_control_load_sensitivity']={'control_caps_source':str(CAP),'control_caps_json_sha256':hashlib.sha256(CAP.read_bytes()).hexdigest(),'full_extracted_cap_sha256':globalcap['source_uncompressed_sha256'],'physical_gate_counts':{'selected_WL':1280,'PC':1280},'added_gate_loads':{'access_nmos_peractiveWL':1152,'precharge_pmos':1152},'driver_counts':{'buf4_peractiveWL':1,'buf20_PC':1},'global_rail_model':'Ten RC nodes100um apart, lumped at right boundary of each group; firstWLnode103.48um from driver, firstPCnode96.4um from driver.0.38umM3,0.104ohm/square tempco0.00333/K. Additional measured fullbank-minuslocal incidentC evenly allocated ten grounded lumps. This is a loading sensitivity, not a native extracted distributed net or proven physical discretization.','full_control_cap_ff':{n:globalcap['control_metal_capacitance'][n]['capacitance_ff'] for n in capby},'retained_local_control_cap_ff':capby,'qualifications':['One unplaced stockbuf4 per activeWL and one unplacedstockbuf20PC at left of macro. Same driver count as primary harness; no favorable driver replication. Ideal command distribution to drivers.','Other9subbank gate loads use groundedS/D accessMOS and VDD-tiedS/D prechargePMOS; not exact actual-array Miller/current loading.','Global incidentC collapsed toground for sensitivity; actual mutual coupling and two-dimensional eight-rowPCnetwork are not retained. No conservative-bound claim.','All tenPC/allWL terminal phase margins checked; only selected16real-array columns have data/precharge checks.','rdd energy includes dummy precharge-gate displacement; remains partial source energy, not fullbank energy.']}
 meta['scope']='Full1280-column WL/PC loading sensitivity with actual fullbank controlmetalC, geometry-derived ten-node commonrailR, one unplacedstockbuf4 peractiveWL/onebuf20PC, and1152dummyothergate loads. Data/current remain16actual columns,112idealaggressors and128physicalreceivers. Not a physically placed fullbank timing/energy qualification.'
 return new,names,meta,image
s.build=build
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--directory',required=True);p.add_argument('--corner',choices=['typical','ss'],default='ss');p.add_argument('--period',type=float,default=60);a=p.parse_args();D=W/a.directory/f'{a.corner}-{a.period:g}ns-s32'
 try:s.run(W/a.directory,a.corner,a.period,32)
 finally:
  if D.exists():shutil.copyfile(Path(__file__),D/'source-global-control-sensitivity.py')
