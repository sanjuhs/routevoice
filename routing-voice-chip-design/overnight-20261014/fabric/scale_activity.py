#!/usr/bin/env python3
"""Change only VCD timestamp spacing to match a slower STA clock."""
import gzip,hashlib,json,re,sys
from fractions import Fraction
from pathlib import Path
r=Path(__file__).resolve().parent
variant=sys.argv[1];period=int(sys.argv[2]);factor=Fraction(period,20)
assert factor.denominator==1 and factor>=1
source=r/'vectors'/f'{variant}.power.vcd.gz';dest=r/'vectors'/f'{variant}.power-{period}ns.vcd.gz'
h=hashlib.sha256();last=0;count=0
with gzip.open(source,'rt') as src,gzip.open(dest,'wt',compresslevel=6) as out:
 for line in src:
  m=re.fullmatch(r'#(\d+)\n',line)
  if m:
   last=int(m[1])*int(factor);line=f'#{last}\n';count+=1
  h.update(line.encode());out.write(line)
with gzip.open(dest,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h.hexdigest()
(r/'evidence'/f'{variant}-activity-{period}ns.json').write_text(json.dumps({'source':str(source.relative_to(r)),'output':str(dest.relative_to(r)),'source_clock_period_ns':20,'clock_period_ns':period,'timestamp_multiplier':int(factor),'timestamp_count':count,'last_timestamp_ps':last,'uncompressed_sha256':h.hexdigest(),'note':'Same five random vectors and readout workload. Only timestamp spacing changed; not a gate-level glitch simulation.'},indent=2)+'\n')
print('W2-STATUS: Scaled and verified activity timestamps for',period,'ns clock')
