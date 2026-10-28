"""Actual K64 slice + existing physical receiver strip, lumped-C, ideal joined.
Not complete macro timing. Run serially, preserve each corner deck/log/trace.
"""
from pathlib import Path
import os,json,re,hashlib,subprocess,time,sys
import numpy as np
BASE=Path(__file__).resolve().parent;R=BASE.parents[2]
W=BASE/sys.argv[1]
PDK=R/'pdks/gf180mcuD/libs.tech/ngspice'
ARRAY=W/'joined-cap-ports.spice'
RX=R/'experiments/taalas-access/mask-index-comparator/receiver-strip/receiver-strip-cap.spice'
IMAGE=np.load(BASE.parent/'indices.npy')[:64,:32]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def subckt(p):return next(x.split() for x in re.sub(r'\n\+\s*',' ',p.read_text()).splitlines() if x.lower().startswith('.subckt'))
def joinpin(n):
 n=n.rsplit('.',1)[-1]
 if n=='VDD':return 'vdd'
 if n=='PC':return 'pc'
 m=re.fullmatch('OUT([0-9]+)',n)
 if m:
  num=int(m[1]);return f'out{num//4}_{num%4}'
 return n
def run(corner,vdd,temp,period_ns):
 directory=W/f'{corner}-{period_ns}ns';directory.mkdir(exist_ok=True)
 period=period_ns*1e-9;rows=[0,1,6,7,15,31,47,63];sample=period-7.5e-9
 a=subckt(ARRAY)
 lines=['* K64 actual joined 64x32 bank0 array and receiver',f'.include "{PDK/"design.ngspice"}"',f'.lib "{PDK/"sm141064.ngspice"}" {corner}',f'.include "{ARRAY}"',f'.temp {temp}', '.options reltol=1e-4 abstol=1e-13 klu',f'Vdd vdd 0 {vdd}','Vground VSS 0 0',f'Vpc pc 0 PULSE(0 {vdd} 2n .2n .2n {period_ns-5}n {period_ns}n)','Xjoined '+' '.join(joinpin(p) for p in a[2:])+' '+a[1]]
 powers=['v(vdd)*i(Vdd)','v(pc)*i(Vpc)']
 for row in range(64):
  if row not in rows:
   lines.append(f'VWL{row} WL{row} 0 0');continue
  t=rows.index(row)*period
  lines.append(f'VWL{row} WL{row} 0 PWL(0 0 {t+2.5e-9:g} 0 {t+2.7e-9:g} {vdd} {t+period-5e-9:g} {vdd} {t+period-4.8e-9:g} 0 {len(rows)*period:g} 0)')
  powers.append(f'v(WL{row})*i(VWL{row})')
 pins=[f'{c}_{b}' for c in range(32) for b in range(4)]
 lines += [f'Cload{p} out{p} 0 10f' for p in pins]
 lines += ['Bpower power 0 V=-('+'+'.join(powers)+')','.control','set wr_singlescale','set wr_vecnames',f'tran .25n {len(rows)*period:g}','wrdata trace.dat '+' '.join([f'v(IDX{p})' for p in pins]+[f'v(out{p})' for p in pins]+['v(power)']),'quit','.endc','.end']
 deck=directory/'test.cir';deck.write_text('\n'.join(lines)+'\n')
 begin=time.monotonic()
 with (directory/'ngspice.log').open('w') as out:
  proc=subprocess.run(['nice','-n','10','ngspice','-b','test.cir'],cwd=directory,stdout=out,stderr=subprocess.STDOUT,timeout=600)
 assert proc.returncode==0
 trace=np.loadtxt(directory/'trace.dat',skiprows=1);assert trace[-1,0]>=len(rows)*period*.999
 expected=((IMAGE[:,:,None]>>np.arange(4))&1).reshape(64,128).astype(bool)
 bad_raw=bad_out=0;max_good_ns=0;samples=[];row_energies=[]
 for slot,row in enumerate(rows):
  t=slot*period;capture=t+sample
  point=np.array([np.interp(capture,trace[:,0],trace[:,i]) for i in range(1,258)])
  raw,out=point[:128],point[128:256];e=expected[row]
  rawok=np.where(e,raw<=.3*vdd,raw>=.7*vdd);outok=np.where(e,out>=.9*vdd,out<=.1*vdd)
  bad_raw+=int((~rawok).sum());bad_out+=int((~outok).sum())
  window=trace[(trace[:,0]>=t+2.5e-9)&(trace[:,0]<=capture)]
  ok=np.where(e,window[:,1:129]<=.3*vdd,window[:,1:129]>=.7*vdd)&np.where(e,window[:,129:257]>=.9*vdd,window[:,129:257]<=.1*vdd)
  for bit in range(128):
   bad=np.flatnonzero(~ok[:,bit]);first_good=window[min(bad[-1]+1,len(window)-1),0] if len(bad) else t+2.5e-9
   max_good_ns=max(max_good_ns,(first_good-t-2.5e-9)*1e9)
  samples.append({'local_row':row,'raw_failures':int((~rawok).sum()),'restored_failures':int((~outok).sum()),'min_undischarged_bitline_fraction':float(np.min(raw[~e]/vdd)) if (~e).any() else None,'max_discharged_bitline_fraction':float(np.max(raw[e]/vdd)) if e.any() else None})
  if slot:
   ti=np.concatenate(([t],trace[(trace[:,0]>t)&(trace[:,0]<(t+period)),0],[t+period]));pw=np.interp(ti,trace[:,0],trace[:,-1]);row_energies.append(float(np.trapezoid(pw,ti)*1e12))
 result={'corner':corner,'voltage_v':vdd,'temperature_c':temp,'period_ns':period_ns,'evaluate_start_ns':2.5,'capture_ns':sample*1e9,'checked_bits':len(rows)*128,'addressed_local_rows':rows,'raw_70_30_failures':bad_raw,'restored_90_10_failures':bad_out,'maximum_sampled_settled_time_ns_after_evaluate':max_good_ns,'mean_net_source_energy_pj_per_32_lane_row_read':float(np.mean(row_energies)),'maximum_net_source_energy_pj_per_32_lane_row_read':max(row_energies),'mean_energy_pj_per_four_bit_index':float(np.mean(row_energies))/32,'excludes_startup_row':0,'deck_sha256':sha(deck),'trace_sha256':sha(directory/'trace.dat'),'wall_seconds':time.monotonic()-begin,'rows':samples}
 (directory/'result.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='rows'},flush=True)
 return result
if __name__=='__main__':
 cases=[]
 for period in [25,20]:
  for corner,vdd,temp in [('typical',3.3,25),('ss',2.97,125)]:
   assert __import__('shutil').disk_usage('/').free>=22*1024**3
   cases.append(run(corner,vdd,temp,period))
 report={'scope':'Measured physical joined bank0 array and receiver strip with actual routed join capacitance','image_region':{'rows':[0,64],'columns':[0,32]},'array_sha256':sha(ARRAY),'cases':cases,'limitations':['Bank0 geometry is tested; not worst-bank timing proof','No distributed wire resistance','Ideal WL, precharge and supply drivers','Only 32 lanes; full 320-lane wordline loading and global clock/precharge distribution excluded','10fF assumed output loads; latch and bank mux timing/energy absent','No complete macro row-read time, macro energy or real-time recognizer proof']}
 (W/'results.json').write_text(json.dumps(report,indent=2)+'\n')
