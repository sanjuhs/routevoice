"""Bijection-only name view for Netgen; no electrical node merging."""
from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent/'joined-bank0-v2'
s=(W/'joined-ports.spice').read_text();nodes=set()
for l in s.splitlines():
 if l.startswith('X'):nodes.update(l.split()[1:5])
mapping={n:n.rsplit('.',1)[-1] for n in nodes};assert len(set(mapping.values()))==len(mapping)
lines=[]
for l in s.splitlines():
 t=l.split()
 if not t:lines.append(l);continue
 if t[0].lower()=='.subckt':t=t[:2]+[mapping[n] for n in t[2:]]
 elif t[0].startswith('X'):t=t[:1]+[mapping[n] for n in t[1:5]]+t[5:]
 lines.append(' '.join(t))
(W/'joined-lvs-canonical.spice').write_text('\n'.join(lines)+'\n')
(W/'lvs-node-bijection.json').write_text(json.dumps({'node_count':len(mapping),'distinct_canonical_names':len(set(mapping.values())),'source_sha256':hashlib.sha256((W/'joined-ports.spice').read_bytes()).hexdigest(),'canonical_sha256':hashlib.sha256((W/'joined-lvs-canonical.spice').read_bytes()).hexdigest(),'mapping':mapping},indent=2)+'\n')
print('Canonicalized',len(mapping),'nodes bijectively')
