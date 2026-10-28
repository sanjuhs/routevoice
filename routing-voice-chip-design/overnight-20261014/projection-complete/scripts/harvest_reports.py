#!/usr/bin/env python3
"""Pack small physical-flow evidence without compiler objects or large design views."""
import argparse, datetime, hashlib, json, tarfile
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--tag', required=True)
a = p.parse_args()
assert a.tag.replace('-', '').replace('_', '').isalnum()
w = Path(__file__).resolve().parents[1]
out = w / 'evidence' / ('physical-reports-' + a.tag + '.tar.gz')
assert not out.exists(), 'Preserve existing evidence archives'
accepted, skipped = [], []
allowed = {'.json', '.log', '.rpt', '.txt', '.csv', '.sdc', '.tcl', '.yaml', '.yml'}
for root in [w / 'runs', w / 'logs']:
    for q in sorted(root.rglob('*')):
        if not q.is_file() or q.is_symlink():
            continue
        if q.suffix not in allowed and q.name != 'COMMANDS':
            continue
        size = q.stat().st_size
        if size > 32 * 1024**2:
            skipped.append({'path': str(q.relative_to(w)), 'bytes': size,
                            'reason': 'Individual report exceeds 32 MiB'})
            continue
        accepted.append(q)
with tarfile.open(out, 'w:gz', compresslevel=1) as tar:
    for q in accepted:
        tar.add(q, arcname=str(q.relative_to(w)), recursive=False)
manifest = {
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Snapshot of physical/log text evidence; active logs may continue changing. No design-view qualification implied.',
    'archive': out.name, 'archive_bytes': out.stat().st_size,
    'archive_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
    'files': [str(q.relative_to(w)) for q in accepted], 'skipped': skipped}
out.with_suffix('.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({k: v for k, v in manifest.items() if k not in ('files', 'skipped')}))
