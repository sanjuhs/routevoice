#!/usr/bin/env python3
"""Download each archive back from HF, stream-hash every tar member, compare with the pod manifest and live files."""
import hashlib, json, os, shutil, subprocess, sys, tarfile
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

REPO = 'sanjuhs/routevoice-pod-final-20261022'
W = Path('/workspace'); V = W / 'hfverify'
os.environ['HF_TOKEN'] = (Path('/root/.hf_token').read_text().strip())
api = HfApi()

manifest = {}
for line in (W / 'pod-manifest.sha256').read_text().splitlines():
    h, p = line.split(None, 1); manifest[p.strip()] = h
manifest['setup.log'] = hashlib.sha256((W / 'setup.log').read_bytes()).hexdigest()

files = api.list_repo_files(REPO, repo_type='dataset')
names = sorted({f.split('/')[1] for f in files if f.startswith('archives/')})
seen, bad, report = {}, [], {}
for name in names:
    shutil.rmtree(V, ignore_errors=True); V.mkdir()
    parts = sorted(f for f in files if f.startswith(f'archives/{name}/') and '.tar.zst.part' in f)
    local = [hf_hub_download(REPO, f, repo_type='dataset', local_dir=V) for f in parts]
    want = dict(l.split()[::-1] for l in (W / f'{name}.parts.sha256').read_text().splitlines())
    for f in local:
        got = hashlib.sha256(Path(f).read_bytes()).hexdigest()
        if want.get(Path(f).name) != got: bad.append(f'part-sha {name} {Path(f).name}')
    cat = subprocess.Popen(['cat', *local], stdout=subprocess.PIPE)
    z = subprocess.Popen(['zstd', '-dc'], stdin=cat.stdout, stdout=subprocess.PIPE)
    n = 0
    with tarfile.open(fileobj=z.stdout, mode='r|') as t:
        for m in t:
            if not m.isfile(): continue
            h = hashlib.sha256()
            fo = t.extractfile(m)
            for chunk in iter(lambda: fo.read(1 << 20), b''): h.update(chunk)
            p = m.name.removeprefix('./'); n += 1
            if p in seen: bad.append(f'duplicate {p}')
            seen[p] = h.hexdigest()
            if manifest.get(p) != seen[p]: bad.append(f'content {name} {p}')
    z.wait(); cat.wait()
    if z.returncode or cat.returncode: bad.append(f'stream-error {name}')
    report[name] = {'parts': len(local), 'files': n}
    print(name, report[name], 'bad_so_far', len(bad), flush=True)
missing = sorted(set(manifest) - set(seen))
out = {'archives': report, 'files_checked': len(seen), 'manifest_files': len(manifest),
       'missing_from_hf': len(missing), 'missing_sample': missing[:20], 'problems': len(bad), 'problem_sample': bad[:20]}
shutil.rmtree(V, ignore_errors=True)
(W / 'hf-verify.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
sys.exit(0 if not bad and not missing else 1)
