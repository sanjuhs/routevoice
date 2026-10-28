from pathlib import Path
import os,json,subprocess,hashlib
import numpy as np
B=Path(__file__).resolve().parent;W=B/'joined-bank0-v2';R=B.parents[2]
ix=np.load(B.parent/'indices.npy')[:64,:32]
ports=['VDD','VSS','PC']+[f'WL{i}' for i in range(64)]+[f'IDX{c}_{b}' for c in range(32) for b in range(4)]+[f'OUT{i}' for i in range(128)]
lines=['* Independent actual mask and physical receiver schematic','.subckt RV_JOINED_REF '+' '.join(ports)]
n=0
def mos(d,g,s,b,m,w):
 global n
 lines.append(f'X{n} {d} {g} {s} {b} {m}_03v3 w={w}u l=0.28u');n+=1
for row in range(64):
 for col in range(32):
  for bit in range(4):
   d=f'IDX{col}_{bit}' if ix[row,col]>>bit&1 else f'OPEN_R{row}_C{col}_B{bit}'
   mos(d,f'WL{row}','VSS','VSS','nfet',0.36)
for i in range(128):
 idx=f'IDX{i//4}_{i%4}';out=f'OUT{i}'
 mos(idx,'PC','VDD','VDD','pfet',1.44);mos(idx,out,'VDD','VDD','pfet',0.36);mos(out,idx,'VSS','VSS','nfet',0.36);mos(out,idx,'VDD','VDD','pfet',0.72)
lines.append('.ends RV_JOINED_REF');(W/'reference.spice').write_text('\n'.join(lines)+'\n')
args=['netgen','-batch','lvs',f'{W/"joined-lvs-canonical.spice"} RV_JOINED_FLAT',f'{W/"reference.spice"} RV_JOINED_REF',str(R/'pdks/gf180mcuD/libs.tech/netgen/setup.tcl'),str(W/'comparison.log')]
(W/'netgen-command.json').write_text(json.dumps(args,indent=2))
with (W/'netgen.log').open('w') as f:subprocess.run(['nice','-n','10',*args],cwd=W,stdout=f,stderr=subprocess.STDOUT,timeout=300,check=True)
s=(W/'comparison.log').read_text();result={'circuits_match_uniquely':'Circuits match uniquely.' in s,'property_error_summary_present':'Property errors were found.' in s,'pass':'Circuits match uniquely.' in s and 'Property errors were found.' not in s,'reference_transistors':n,'scope':'Independent native Netgen transistor schematic vs flattened Magic layout with unique existing nodes promoted as pins; vendor setup','comparison_sha256':hashlib.sha256((W/'comparison.log').read_bytes()).hexdigest()}
(W/'netgen-result.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
