"""Correct only runtime vector paths in the already-generated simulator source.

The elaborated circuit and all numeric checks are unchanged. Incremental make
rebuilds the affected translation unit and relinks the simulator normally.
"""
from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[1]
p=w/'gate-trace/Vtb___024root__0.cpp'
old='/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric-k64/vectors/'
new='/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/projection-complete/vectors/'
t=p.read_text();assert t.count(old)==4, 'Expected only the four testbench readmem paths'
q=w/'evidence/gate-generated-before-vector-path-fix.cpp'
assert not q.exists(), 'Preserve previous evidence'
q.write_text(t)
u=t.replace(old,new)
assert len([(a,b) for a,b in zip(t.splitlines(),u.splitlines()) if a!=b])==4
p.write_text(u)
entries=json.loads((w/'evidence/gate-vector-staging.json').read_text())
for e in entries:
 f=w/e['file'];assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==e['sha256']
(w/'evidence/gate-vector-path-fix.json').write_text(json.dumps(dict(
 source_cpp=str(p),old_sha256=hashlib.sha256(t.encode()).hexdigest(),
 corrected_sha256=hashlib.sha256(u.encode()).hexdigest(),changed_lines=4,
 old_prefix=old,new_prefix=new,scope='Only four readmem filename literals; no gate equations or expected numeric values changed',
 input_vectors=entries),indent=2)+'\n')
print('Verified four path-only C++ edits and all staged input hashes.')
