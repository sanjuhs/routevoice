#!/usr/bin/env python3
"""Reclaim duplicate completed-stage views using APFS copy-on-write clones.
Never touch an unfinished step; bytes stay identical and later writes are COW.
"""
import hashlib,json,os,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
candidates=[]
for state in (r/'runs').glob('*/*/state_out.json'):
    for p in state.parent.rglob("*"):
        if p.is_file() and not p.is_symlink() and p.suffix in ['.v','.def','.odb','.sdc','.sdf','.lib','.spef'] and p.stat().st_size>1_000_000:
            candidates.append(p)
for run in (r/'runs').iterdir():
    receipt=r/'evidence'/f'{run.name}.supervisor.json'
    if not receipt.exists() or json.loads(receipt.read_text()).get('exit_code')!=0:continue
    for p in (run/'final').rglob('*'):
        if p.is_file() and not p.is_symlink() and p.suffix in ['.v','.def','.odb','.sdc','.sdf','.lib','.spef'] and p.stat().st_size>1_000_000:candidates.append(p)
known={}
for receipt in (r/'evidence').glob('clones-*.json'):
    for item in json.loads(receipt.read_text()).get('changes',[]):known[item['path']]=item['sha256']
by_size={}
for p in set(candidates):by_size.setdefault(p.stat().st_size,[]).append(p)
changes=[]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
for size,group in by_size.items():
    if len(group)<2:continue
    canonical={}
    for p in sorted(group):
        h=digest(p)
        if h not in canonical:canonical[h]=p;continue
        src=canonical[h]
        if known.get(str(p.relative_to(r)))==h or p.stat().st_ino==src.stat().st_ino:continue
        tmp=p.with_name(p.name+'.w2clone')
        subprocess.run(['/bin/cp','-c',str(src),str(tmp)],check=True)
        assert tmp.stat().st_size==size and digest(tmp)==h
        os.replace(tmp,p)
        changes.append({'path':str(p.relative_to(r)),'clone_source':str(src.relative_to(r)),'sha256':h,'bytes':size})
receipt={'unix':time.time(),'method':'APFS cp -c copy-on-write, exact content hash checked before atomic replacement','nominal_duplicate_bytes_shared':sum(c['bytes'] for c in changes),'changes':changes}
(r/'evidence'/f'clones-{int(time.time())}.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('W2-STATUS: copy-on-write cloned',len(changes),'identical completed views;',round(receipt['nominal_duplicate_bytes_shared']/1024**3,3),'GiB nominal duplicate data shared')
