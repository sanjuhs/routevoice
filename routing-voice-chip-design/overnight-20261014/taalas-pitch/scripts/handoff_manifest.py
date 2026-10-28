"""Bind the final W6 handoff to retained evidence; run only after workers finish."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil

W = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

result = json.loads((W / 'results.json').read_text())
assert result['handoff_finished'] is True
assert result['complete_row_energy_pj'] is None
assert shutil.disk_usage('/').free >= 22 * 2**30
paths = {
    'RESULTS.md', 'results.json', 'INTEGRATION.md', 'COMMANDS.md', 'READING.md',
    'scripts/build.py', 'scripts/build-v1.py', 'scripts/drc.py',
    'scripts/summarize.py', 'scripts/handoff_manifest.py',
    'baseline/manifest.json', 'verification/RESULTS.md', 'verification/results.json',
    'verification/README.md', 'verification/freeze.json', 'timing/RESULTS.md', 'timing/results.json',
    'timing/COMMANDS.md', 'timing/FINAL-PROCESS-STATE.json', 'audit/FINAL-AUDIT.md', 'audit/final-audit.json',
    'audit/final-cap-receipt-audit.json', 'audit/final-timing-trace-audit.json',
    'timing/fullbank-caps/export-caps-result.json', 'timing/fullbank-caps/rank.json',
}
for height in (64, 1280):
    base = f'r{height}-v2'
    g = json.loads((W / base / 'geometry.json').read_text())
    d = json.loads((W / base / 'drc-result.json').read_text())
    v = W / 'verification' / base
    positive = json.loads((v / 'full-bank-netgen-result.json').read_text())
    negative = json.loads((v / 'negative-width-netgen-result.json').read_text())
    current_sha = digest(W / base / 'bank.gds')
    assert current_sha == g['gds_sha256'] == d['gds_sha256'] == positive['input']['gds_sha256'] == negative['input']['gds_sha256']
    assert d['drc_markers'] == 0 and positive['pass'] and negative['negative_control_rejected']
    for name in ('bank.gds', 'geometry.json', 'drc-result.json', 'readback.json'):
        paths.add(f'{base}/{name}')
    for name in ('full-bank-netgen-result.json', 'negative-width-netgen-result.json', 'connectivity.json', 'extract-process.json'):
        paths.add(f'verification/{base}/{name}')
for path in (W / 'verification').rglob('*compression.json'):
    paths.add(str(path.relative_to(W)))
for case in result['timing']['cases']:
    directory = (W / 'timing' / case['path']).parent
    for name in ('result.json', 'build.json', 'test.cir', 'trace.dat.gz'):
        paths.add(str((directory / name).relative_to(W)))
    for path in directory.glob('source-*.py'):
        paths.add(str(path.relative_to(W)))
for name in ('watchdog-extension.json', 'FAILURE.json', 'timeout.json'):
    for path in (W / 'timing').rglob(name):
        paths.add(str(path.relative_to(W)))
        if name == 'FAILURE.json':
            for sibling in path.parent.iterdir():
                if sibling.is_file() and sibling.suffix in ('.json', '.cir', '.log', '.py'):
                    paths.add(str(sibling.relative_to(W)))
for path in (W / 'timing').rglob('*archive*.json'):
    paths.add(str(path.relative_to(W)))
entries = []
for relative in sorted(paths):
    path = W / relative
    assert path.is_file(), relative
    entries.append({'path': relative, 'bytes': path.stat().st_size, 'sha256': digest(path)})
manifest = {
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Critical handoff files, GDS, verification receipts and completed timing decks/traces. Full directory is retained; archival stream hashes and restoration instructions live in compression receipts.',
    'files': entries,
    'final_free_disk_gib': shutil.disk_usage('/').free / 2**30,
    'full_row_energy_measured': False,
}
(W / 'artifact-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'W6-STATUS: final manifest binds {len(entries)} artifacts; GDS hashes match DRC and positive/negative LVS receipts')
