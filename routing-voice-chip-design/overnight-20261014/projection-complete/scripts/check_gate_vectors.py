"""Fail before compilation if retained gate input files are missing or changed."""
from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[1]
entries=json.loads((w/'evidence/gate-vector-staging.json').read_text())
for e in entries:
 p=w/e['file'];assert p.is_file(),p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'],p
a=[int(x,16) for x in (w/'vectors/inputs.hex').read_text().split()[:1280]]
a=[x-512 if x>=256 else x for x in a]
assert len(a)==1280 and any(a)
print(json.dumps(dict(status='PASS exact retained vector hashes',first_vector=dict(
 samples=len(a),minimum=min(a),maximum=max(a),zero_count=a.count(0),mean_absolute=sum(abs(x) for x in a)/len(a)),
 provenance='Saved captured-speech vector0 from W2b affine inputs; not a fresh speech capture'),indent=2))
