"""Archive completed proof artifacts; omit regenerable compiler intermediates."""
import hashlib
import json
import tarfile
import shutil
import sys
from pathlib import Path

W=Path(__file__).resolve().parent
files=set()
for sub in ['configs','rtl','tb','vectors','evidence','logs']:
    files.update(p for p in (W/sub).rglob('*') if p.is_file() and p.name!='array_port-mapped-speech.saif')
files.update(p for p in W.iterdir() if p.is_file() and p.suffix in {'.py','.sh','.tcl','.md','.json'})
for p in (W/'runs').rglob('*'):
    if not p.is_file() or 'tmp' in p.relative_to(W/'runs').parts:
        continue
    if p.name in {'_env.tcl','COMMANDS','runtime.txt','resolved.json','config.json','extra.json','state_in.json','state_out.json'} or p.suffix in {'.rpt','.log','.abc'} or 'metrics' in p.name:
        files.add(p)
for tag in ['buf-v2','buf-v3','buf-v4']:
    for p in (W/'runs'/tag).glob('*-yosys-synthesis/rv_k64_array_port.nl.v*'):
        files.add(p)
states=sorted((W/'runs/buf-v4-physical').glob('*/state_out.json'),key=lambda p:int(p.parent.name.split('-')[0]))
def add_views(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k!='metrics':add_views(x)
    elif isinstance(v,list):
        for x in v:add_views(x)
    elif isinstance(v,str) and v.startswith(str(W)):
        p=Path(v)
        if p.is_file():files.add(p)
for tag in ['buf-v4','buf-v4-physical','buf-v4-idealprects']:
    chain=sorted((W/'runs'/tag).glob('*/state_out.json'),key=lambda p:int(p.parent.name.split('-')[0]))
    if chain:add_views(json.loads(chain[-1].read_text()))
for p in (W/'runs/supplemental-klayout-drc').rglob('*'):
    if p.is_file():files.add(p)
archive=W/(sys.argv[1] if len(sys.argv)>1 else 'completed-evidence.tar.gz')
assert not archive.exists()
snapshot=W/('snapshot-'+archive.name.removesuffix('.tar.gz'));snapshot.mkdir()
manifest=[]
baseline={}
if len(sys.argv)>2 and sys.argv[2]=='--delta-morning':
    baseline={r['path']:r['sha256'] for r in json.loads((W/'snapshot-morning-partial-evidence/archive-manifest.json').read_text())}
    basis=json.loads((W/'morning-partial-evidence.tar.gz.receipt.json').read_text())
    bp=snapshot/'delta-base.json';bp.write_text(json.dumps({'apply_after':'morning-partial-evidence.tar.gz','base_sha256':basis['sha256'],'method':'Overlay these new or changed files onto the verified morning archive; unchanged files omitted.'},indent=2)+'\n')
for p in sorted(files):
    if str(p.relative_to(W)) in baseline:
        with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
        if h==baseline[str(p.relative_to(W))]:continue
    dest=snapshot/p.relative_to(W);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    with dest.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
    manifest.append({'path':str(p.relative_to(W)),'bytes':dest.stat().st_size,'sha256':h})
if (snapshot/'delta-base.json').exists():
    p=snapshot/'delta-base.json';manifest.append({'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
mp=snapshot/'archive-manifest.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(archive,'w:gz',compresslevel=3) as out:
    for p in sorted(snapshot.rglob('*')):
        if p.is_file():out.add(p,arcname=str(p.relative_to(snapshot)),recursive=False)
with archive.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
receipt={'path':str(archive),'bytes':archive.stat().st_size,'sha256':h,'files':len(manifest)+1,'uncompressed_bytes':sum(x['bytes'] for x in manifest),'snapshot_directory':str(snapshot)}
(W/(archive.name+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
(W/'archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
