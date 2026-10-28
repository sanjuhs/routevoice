"""Preserve finished generated objects internally; retain active executable in place."""
from pathlib import Path
import hashlib,json,tarfile,time
W=Path(__file__).resolve().parent
R=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-front'
obj=R/'obj';binary='Vrv_allonchip_top_w1c';archive=R/'compiled-intermediates.tar.gz'
assert not archive.exists()
files=[p for p in sorted(obj.iterdir()) if p.is_file() and p.name!=binary]
records={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files}
with tarfile.open(archive,'w:gz',compresslevel=1) as t:
 for p in files:t.add(p,arcname=p.name,recursive=False)
with tarfile.open(archive,'r:gz') as t:
 assert set(t.getnames())==set(records)
 for name,r in records.items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==r['sha256']
for p in files:
 assert hashlib.sha256(p.read_bytes()).hexdigest()==records[p.name]['sha256']
 p.unlink()
result={'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':records,'input_bytes':sum(r['bytes'] for r in records.values()),'archive_bytes':archive.stat().st_size,'active_binary_retained':str(obj/binary),'all_archived_contents_verified':True}
(W/'build-archive.json').write_text(json.dumps(result,indent=2)+'\n')
print('W1c-STATUS: build intermediates archived and verified internally; reclaimed bytes',result['input_bytes']-result['archive_bytes'])
