"""Real tall joined subbank, physical C allocation and explicit geometry-R model."""
from pathlib import Path
from collections import defaultdict
import argparse,json,re,hashlib,subprocess,time,shutil,gzip,sys
import numpy as np
from protocols import protocol,pwl,wl_stimulus,aggressor,analyze
W=Path(__file__).resolve().parent;A=W.parents[1];R=A.parents[1];OLD=R/'experiments/taalas-access/mask-index-tall';PDK=R/'pdks/gf180mcuD/libs.tech/ngspice'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def parsed(n):
 if (m:=re.fullmatch(r'IDX(\d+)_(\d)',n)):return 'BL',int(m[1])*4+int(m[2]),None
 if (m:=re.fullmatch(r'OPEN_R(\d+)_C(\d+)_B(\d)',n)):return 'OPEN',int(m[2])*4+int(m[3]),int(m[1])
 if (m:=re.fullmatch(r'WL(\d+)',n)):return 'WL',None,int(m[1])
 if (m:=re.fullmatch(r'OUT(\d+)',n)):return 'OUT',int(m[1]),None
 assert n in ['VDD','VSS','PC'],n;return n,None,None

def valueff(s):
 m=re.fullmatch(r'([0-9.eE+-]+)([afpnum]?)',s);assert m,s
 return float(m[1])*{'a':.001,'f':1,'p':1000,'n':1e6,'u':1e9,'m':1e12,'':1e15}[m[2]]

def caps(lines):
 d=defaultdict(float)
 for l in lines:
  if l.startswith('C'):
   f=l.split();d[tuple(sorted(f[1:3]))]+=valueff(f[3])
 return d

def mos(name,d,g,s,b,kind,w,l=.28):return f'X{name} {d} {g} {s} {b} {kind}_03v3 w={w:g}u l={l:g}u ad={w*.44:g}p as={w*.44:g}p pd={2*(w+.44):g}u ps={2*(w+.44):g}u'

def build(O,corner,vdd,temp,period,segments):
 ex=json.loads((O/'extraction.json').read_text());geo=json.loads((O/'source-geometry.json').read_text());image=np.load(O/'image.npy');H=ex['rows'];seldata=json.loads((W/'selection.json').read_text());candidate=next(d for d in seldata['ranked'][str(H)] if d['bank']==ex['bank'] and d['subbank']==ex['subbank']);selected=json.loads((O/'cap-ranking.json').read_text())['selected'] if (O/'cap-ranking.json').exists() else candidate['local_bit_columns']
 bits=((image[:,:,None]>>np.arange(4))&1).reshape(H,128)[:,selected];pop=bits.sum(0);peak=(json.loads((O/'cap-ranking.json').read_text())['ranking'][0]['local_bit_column']-selected[0]) if (O/'cap-ranking.json').exists() else int(pop.argmax());ones=np.flatnonzero(bits[:,peak]);zeros=np.flatnonzero(~bits[:,peak].astype(bool));transition=int(np.count_nonzero(bits[1:]!=bits[:-1],axis=1).argmax());base=[]
 for row in [int(ones[0]),int(zeros[0]),int(ones[-1]),int(zeros[-1]),int(bits.sum(1).argmax()),transition,transition+1,H-2,H-1]:
  if row not in base:base.append(row)
 override=json.loads((O/'pattern-override.json').read_text()) if (O/'pattern-override.json').exists() else None
 if override:base=override['rows']
 addresses=base*2;active=sorted(set(base));p=protocol(period);sheet=.104*(1+.00333*(temp-25));row_y=lambda row:2+row*1.44+(row//8)*1.8+.98;end_y=2+H*1.44+(H//8-1)*1.8+.65+.8;height=end_y-.5
 section=lambda row:min(segments,max(1,round((row_y(row)-.5)/height*segments)))
 lines=['* Actual real-image tall joined subbank: extracted MOS/C; geometry-R approximation',f'.include "{PDK/"design.ngspice"}"',f'.lib "{PDK/"sm141064.ngspice"}" {corner}',f'.param sw_stat_global=0 sw_stat_mismatch=0',f'.temp {temp}','.options reltol=1e-4 abstol=1e-13 klu method=gear maxord=2',f'Vrdd rdd 0 {vdd}',f'Vwdd wdd 0 {vdd}',f'Vpdd pdd 0 {vdd}','Vpcin pcin 0 '+pwl([(0,0)]+[(cycle*period+t,v) for cycle in range(len(addresses)) for t,v in [(p["pc_off_ns"],0),(p["pc_off_ns"]+.2,vdd),(p["pc_on_start_ns"],vdd),(period,0)]])]
 driver_hash={}
 for drive in [4,20]:
  path=OLD/'driver-cells'/f'buf{drive}-cap.spice';lines.extend(path.read_text().splitlines());driver_hash[str(drive)]=sha(path)
 def drive(name,inp,out,supply,size):
  text=(OLD/'driver-cells'/f'buf{size}-cap.spice').read_text();f=next(l.split() for l in text.splitlines() if l.lower().startswith('.subckt'));pins={'Z':out,'I':inp,'VDD':supply,'VSS':'0','VNW':supply,'VPW':'0'};assert set(f[2:])==set(pins);lines.append(f'X{name} '+' '.join(pins[n] for n in f[2:])+' '+f[1])
 drive('pcdrv','pcin','pc','pdd',20)
 for row in active:
  lines.append(f'Vwi{row} wi{row} 0 {wl_stimulus(addresses,row,vdd,p)}');drive(f'wdrv{row}',f'wi{row}',f'wd{row}','wdd',4);lines.append(f'Rwl{row} wd{row} wl{row} {sheet*93.68/.38:g}')
  for other in range(128-len(selected)):lines.append(mos(f'dummy{row}_{other}','0',f'wl{row}','0','0','nfet',.36))
 for n in range(128):
  if n not in selected:lines.append(f'Vagg{n} agg{n} 0 {aggressor(addresses,n,image,vdd,p)}')
 # Retained one-strap model: physical2umM4 height; externally ideal endpoint supplies.
 lines.extend(['Rgndstart gnd0 0 .001',f'Rgndend gnd{segments} 0 .001'])
 for seg in range(1,segments+1):lines.append(f'Rgnd{seg} gnd{seg-1} gnd{seg} {sheet*height/segments/2:g}')
 joinR={}
 for n in selected:
  group,local=divmod(n,16);x=geo['array_origin_um'][0]+2+group*11.56+local*.66+.33;rx=10+3.5*n+2.24;y=geo['fanout_start_y_um']+n*geo['fanout_pitch_um'];length=(geo['array_origin_um'][1]+.5-y)+abs(rx-x)+(y-2);res=sheet*length/.38+4*15;joinR[n]={'length_um':length,'ohm':res,'via_count':4};lines.append(f'Rjoin{n} bl{n}s0 abl{n} {res:g}')
  for seg in range(1,segments+1):lines.append(f'Rbl{n}_{seg} '+(f'abl{n}' if seg==1 else f'bl{n}s{seg-1}')+f' bl{n}s{seg} {sheet*height/segments/.38:g}')
 array=(O/'array-canonical.spice').read_text().splitlines();joined=(O/'joined-canonical.spice').read_text().splitlines();devices=0
 for l in array:
  if not l.startswith('X'):continue
  f=l.split();kind,n,row=parsed(f[1]);row=int(f[2][2:])
  if n not in selected:continue
  seg=section(row);local=n-selected[0];drain=f'bl{n}s{seg}' if kind=='BL' else f[1];wl=f'wl{row}' if row in active else '0'
  lines.append(f'Rsource{row}_{local} '+(f'gnd{seg}' if local==0 else f'sr{row}_{local-1}')+f' sr{row}_{local} {sheet*(.83 if local==0 else .66)/.38:g}')
  lines.extend([f'Rdrain{devices} {drain} dx{devices} {30+15*.26/.36:g}',f'Raccesssource{devices} sr{row}_{local} sx{devices} {15+15*.26/.36:g}',' '.join([f'Xarr{devices}',f'dx{devices}',wl,f'sx{devices}','0']+f[5:])]);devices+=1
 assert devices==H*16
 def mapnet(n,seg=0):
  kind,index,row=parsed(n)
  if kind=='VSS':return '0'
  if kind=='VDD':return 'rdd'
  if kind=='PC':return 'pc'
  if kind=='WL':return f'wl{row}' if row in active else '0'
  if kind=='OPEN':return n if index in selected else '0'
  if kind=='OUT':return f'out{index}'
  return f'bl{index}s{seg}' if index in selected else f'agg{index}'
 receiver_devices=0
 for l in joined:
  if not l.startswith('X'):continue
  f=l.split()
  if f[2].startswith('WL'):continue
  lines.append(' '.join(['Xrecv'+f[0][1:]]+[mapnet(n) for n in f[1:5]]+f[5:]));receiver_devices+=1
 assert receiver_devices==512
 ca,cj=caps(array),caps(joined);count=0;kept_array=kept_join=0.;incident={n:0. for n in selected};negative=sum(max(0.,v-cj.get(pair,0.)) for pair,v in ca.items())
 def addcap(a,b,value,distributed):
  nonlocal count,kept_array,kept_join
  pa,pb=parsed(a),parsed(b)
  relevant=lambda q:(q[0] in ['BL','OPEN'] and q[1] in selected) or(q[0]=='WL' and q[2] in active)
  if distributed and not(relevant(pa) or relevant(pb)):return
  row=next((q[2] for q in [pa,pb] if q[0] in ['WL','OPEN']),None)
  allocation=[(section(row),1)] if row is not None else ([(s,1/segments) for s in range(1,segments+1)] if distributed else [(0,1)])
  for seg,weight in allocation:
   x,y=mapnet(a,seg),mapnet(b,seg)
   if x!=y:lines.append(f'Cphysical{count} {x} {y} {value*weight:g}f');count+=1
  if distributed:kept_array+=value
  else:kept_join+=value
  for q in [pa,pb]:
   if q[0]=='BL' and q[1] in selected:incident[q[1]]+=value
 for (a,b),value in cj.items():
  if value<=0:continue
  overlap=min(value,ca.get((a,b),0.));extra=value-overlap
  if overlap:addcap(a,b,overlap,True)
  if extra:addcap(a,b,extra,any(parsed(n)[0] in ['WL','OPEN'] for n in [a,b]))
 for n in range(128):lines.append(f'Cout{n} out{n} 0 10f')
 wterms='+'.join(f'v(wi{r})*i(Vwi{r})' for r in active);aterms='+'.join(f'v(agg{n})*i(Vagg{n})' for n in range(128) if n not in selected)
 power_equations=['let pr=-v(rdd)*i(Vrdd)',f'let pw=-(v(wdd)*i(Vwdd)+{wterms})','let pp=-(v(pdd)*i(Vpdd)+v(pcin)*i(Vpcin))',f'let pa=-({aterms})']
 names=[f'out{n}' for n in selected]+[f'bl{n}s0' for n in selected]+[f'bl{n}s{segments}' for n in selected]+[f'gnd{segments//2}','pc','pr','pw','pp','pa']+[f'wl{r}' for r in active]
 lines.extend(['.control','set wr_singlescale','set wr_vecnames',f'tran .2n {len(addresses)*period}n 0 .2n']+power_equations+['wrdata trace.dat '+' '.join(n if n in ['pr','pw','pp','pa'] else f'v({n})' for n in names),'quit','.endc','.end'])
 meta={'pattern_override':override,'stimulus_representation':'Explicit PWL PC phases avoid near-coincident PULSE arithmetic versus aggressor PWL breakpoints at fractional protocols; intended phase times unchanged','protocol':p,'rows':H,'selected':selected,'addresses':addresses,'peak_ranked_bit_column':selected[peak],'base_sequence':base,'base_sequence_length':len(base),'active_rows':active,'segments':segments,'array_devices':devices,'receiver_devices':receiver_devices,'driver_hashes':driver_hash,'source_gds_sha256':ex['source_gds_sha256'],'array_cap_sha256':sha(O/'array-cap.spice'),'joined_cap_sha256':sha(O/'joined-cap.spice'),'metal_sheet_ohm_square':sheet,'array_height_um':height,'bitline_array_ohm':sheet*height/.38,'signal_join_resistance':joinR,'retained_array_cap_ff':kept_array,'retained_join_receiver_cap_ff':kept_join,'array_to_joined_negative_pair_delta_ff':negative,'selected_incident_cap_ff':incident,'expanded_capacitors':count,'power_observation':'Posttransient vector equations; removed isolated behavioral power monitor nodes after20ns numerical failure, no feedback into physical circuit','cap_allocation':'For each exact extracted joined capacitor pair, array-distributed portion=min(newarrayC,newjoinedC); remainder at receiver/join end unless WL/OPEN fixes row. Negative pair delta is recorded, not clipped into extra capacitance. Only joined actual C is simulated.','scope':'16fullheight active columns,112ideal legal-state BL aggressors also driving their real receivers, all128physicalpre2receivers; extracted stockbuf4WL/buf20PC. GeometryR signaljoin+arrayWL/BL/one2umgroundstrap. Groundendpoint/global supply and input phases ideal. No full320lane WL/PC rail load, simultaneous allarraycurrent, decoder/latch/mux.'}
 return lines,names,meta,image

def run(O,corner,period,segments):
 assert shutil.disk_usage('/').free>=22*2**30
 vdd,temp=(3.3,25) if corner=='typical' else (2.97,125);D=O/f'{corner}-{period:g}ns-s{segments}';D.mkdir(exist_ok=True);shutil.copyfile(Path(__file__),D/'source-simulate.py');shutil.copyfile(W/'protocols.py',D/'source-protocols.py');lines,names,meta,image=build(O,corner,vdd,temp,period,segments);deck=D/'test.cir';deck.write_text('\n'.join(lines)+'\n');(D/'build.json').write_text(json.dumps(meta,indent=2));start=time.monotonic();cmd=['nice','-n','10','/opt/homebrew/bin/ngspice','-b','test.cir'];(D/'command.json').write_text(json.dumps(cmd))
 try:
  with (D/'ngspice.log').open('w') as f:proc=subprocess.run(cmd,cwd=D,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 except subprocess.TimeoutExpired:
  (D/'timeout.json').write_text(json.dumps({'timeout_seconds':600,'scope':meta['scope']}));raise
 assert proc.returncode==0,proc.returncode
 trace=np.loadtxt(D/'trace.dat',skiprows=1)
 if trace[-1,0]<len(meta['addresses'])*period*1e-9*.999:
  (D/'FAILURE.json').write_text(json.dumps({'status':'incomplete numerical trace','end_time_ns':float(trace[-1,0]*1e9),'required_end_time_ns':len(meta['addresses'])*period,'physical_protocol_claim':None}))
  raise RuntimeError('Incomplete transient; no physical protocol or energy claim')
 result={**analyze(trace,names,meta,image,vdd),'corner':corner,'voltage_v':vdd,'temperature_c':temp,'period_ns':period,'protocol':meta['protocol'],'scope':meta['scope'],'conditional20ns_interleave_factor':int(np.ceil(period/20)),'interleave_factor_qualified':False,'interleave_qualification':'Only sampled32lane protocol if pass; not full320lane bank throughput','deck_sha256':sha(deck),'trace_sha256':sha(D/'trace.dat'),'wall_seconds':time.monotonic()-start,'source_gds_sha256':meta['source_gds_sha256']}
 (D/'result.json').write_text(json.dumps(result,indent=2,default=lambda x:x.item())+'\n')
 with gzip.open(D/'trace.dat.gz','wb') as f:f.write((D/'trace.dat').read_bytes())
 (D/'trace.dat').unlink();print('W5-STATUS: tall slice',corner,period,'ns',result['failures'],'latency',result['maximum_sampled_settled_ns'],'energy',result['energy_pj_per_sampled_read'],flush=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--directory',default='r320-v1');p.add_argument('--corner',choices=['typical','ss'],required=True);p.add_argument('--period',type=float,required=True);p.add_argument('--segments',type=int,default=32);a=p.parse_args();run(W/a.directory,a.corner,a.period,a.segments)
