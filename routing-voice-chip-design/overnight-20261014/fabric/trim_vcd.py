#!/usr/bin/env python3
"""Retain exactly the five-vector dumpon interval, zero origin, no X shutdown."""
import gzip,json
from pathlib import Path
r=Path(__file__).resolve().parent
records=[]
for p in (r/'vectors').glob('rv_*.vcd.gz'):
    if '.power.' in p.name:continue
    out=p.with_name(p.name.replace('.vcd.gz','.power.vcd.gz'))
    header=True;active=False;current=0;begin=None;end=None
    with gzip.open(p,'rt') as src,gzip.open(out,'wt',compresslevel=1) as dst:
        for line in src:
            if header:
                dst.write(line)
                if '$enddefinitions' in line:header=False
                continue
            if line.startswith('#'):
                current=int(line[1:])
                if active:dst.write(f'#{current-begin}\n')
                continue
            if '$dumpon' in line:
                assert begin is None
                begin=current;active=True;dst.write('#0\n$dumpvars\n');continue
            if '$dumpoff' in line and active:
                end=current;break
            if active:dst.write(line)
    assert begin is not None and end is not None
    records.append({'source_vcd':str(p.relative_to(r)),'power_trace':str(out.relative_to(r)),'source_begin_ps':begin,'source_end_ps':end,'duration_ns':(end-begin)/1000,'vectors':5,'source_vectors':[4,5,6,7,8],'source':'RTL Icarus VCD, NumPy seed 20261014, 50 MHz; includes start/drain/readout checks'})
(r/'evidence/power-traces.json').write_text(json.dumps(records,indent=2)+'\n')
print('W2-STATUS: isolated five-vector VCD activity windows; timestamps start at zero')
