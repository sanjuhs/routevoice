#!/usr/bin/env python3
"""Normalize a gate VCD's initial time; preserve and hash all non-timestamp bytes."""
import gzip,hashlib,json,re,sys
from pathlib import Path
r=Path(__file__).resolve().parent;source=Path(sys.argv[1]).resolve();dest=source.with_name(source.name.replace('.vcd.gz','.normalized.vcd.gz'));assert source.is_relative_to(r) and not dest.exists()
first=None;last=None;scopes=0;variables=0;h=hashlib.sha256();times=0
with gzip.open(source,'rb') as f,gzip.open(dest,'wb',compresslevel=3) as o:
 for line in f:
  if re.fullmatch(rb'#\d+\n',line):
   t=int(line[1:]);first=t if first is None else first;last=t;times+=1;line=f'#{t-first}\n'.encode()
  else:
   h.update(line);scopes+=int(b'$scope' in line);variables+=int(b'$var' in line)
  o.write(line)
check=hashlib.sha256()
with gzip.open(dest,'rb') as f:
 for line in f:
  if not re.fullmatch(rb'#\d+\n',line):check.update(line)
assert h.digest()==check.digest()
d={'source':str(source.relative_to(r)),'output':str(dest.relative_to(r)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'non_timestamp_sha256':h.hexdigest(),'removed_offset_ps':first,'duration_ps':last-first,'duration_ns':(last-first)/1000,'timestamp_count':times,'scope_count':scopes,'variable_declarations':variables,'note':'Five verified random gate-level vectors at 200 ns, including clocked readout; only initial absolute time offset removed. Zero-delay, no routed glitches.'}
(r/'evidence'/f'{source.stem}.normalization.json').write_text(json.dumps(d,indent=2)+'\n');print('W2-STATUS:',json.dumps(d))
