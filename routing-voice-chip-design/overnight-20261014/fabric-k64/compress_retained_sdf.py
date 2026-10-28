"""APFS-transparent compression of completed SDF views, preserving exact bytes/paths."""
from pathlib import Path
import subprocess,hashlib,json,time,shutil
W=Path(__file__).resolve().parent
root=W/'runs/array_port-v2/12-openroad-staprepnr'
manifest=W/'evidence/transparent-sdf-compression.json'
records=json.loads(manifest.read_text()) if manifest.exists() else []
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in sorted(root.glob('*/*.sdf')):
 before=p.stat();h=sha(p);tmp=W/'tmp'/('compressed-'+p.name)
 assert not tmp.exists()
 if shutil.disk_usage('/').free<21.5*2**30:break
 subprocess.run(['nice','-n','10','ditto','--hfsCompression',str(p),str(tmp)],check=True)
 assert sha(tmp)==h and sha(p)==h
 after=tmp.stat();applied=after.st_blocks<before.st_blocks
 if applied:tmp.replace(p)
 else:tmp.unlink()
 records.append({'path':str(p.relative_to(W)),'sha256':h,'logical_bytes':before.st_size,'blocks_before':before.st_blocks,'blocks_after':p.stat().st_blocks,'transparent_compression_applied':applied,'exact_bytes_verified':True,'epoch':time.time()})
 manifest.write_text(json.dumps(records,indent=2)+'\n')
print('W2b-STATUS: Retained SDF paths and bytes preserved; APFS compression results',[(r['path'],r['transparent_compression_applied'],r['blocks_before']-r['blocks_after']) for r in records])
