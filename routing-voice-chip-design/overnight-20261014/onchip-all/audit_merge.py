"""Pin merged compile inputs, verify worker provenance/ROM hashes and check-only host."""
from pathlib import Path
import hashlib,json,re,sys
W=Path(__file__).resolve().parent;R=W.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((W/'rom-manifest.json').read_text())
for p,d in manifest['inputs'].items():assert sha(Path(p))==d['sha256'],p
for d in manifest['outputs']:assert sha(Path(d['path']))==d['sha256'],d['path']
assert sum(d['native_bytes'] for d in manifest['outputs'])==28641280
for p,d in json.loads((W/'source-provenance.json').read_text()).items():assert sha(Path(p))==d['sha256'],p
ports=json.loads((W/'port-audit.json').read_text());moved=ports['moved_inputs_to_debug_outputs']
sv=(W/'rv_allonchip_top_all_v1.sv').read_text();header=sv[:sv.index('\n);')]
for n in moved:
 assert re.search(r'output wire\s*(\[[^]]+\])?\s*'+n+r'\s*[,\n]',header),n
 assert not re.search(r'input wire\s*(\[[^]]+\])?\s*'+n+r'\s*[,\n]',header),n
for p in [W/'four_stage.cpp',*W.glob('*.hpp')]:
 s=p.read_text()
 for n in moved:assert not re.search(r'\bt\.'+n+r'(?:\[[^]]*\])?\s*=(?!=)',s),(p,n)
paths=set()
for x in json.loads((W/'commands.json').read_text())['generate-full']:
 p=Path(x)
 if p.is_absolute() and p.is_file() and p.suffix in ['.sv','.v','.cpp']:paths.add(p)
paths.update(W.glob('*.hpp'));paths.update(W.glob('*.py'));paths.add(W/'commands.json');paths.add(W/'no-pch.mk')
record={str(p):sha(p) for p in sorted(paths)}
if '--verify-pins' in sys.argv:assert record==json.loads((W/'build-input-pins.json').read_text()),'build inputs changed'
else:(W/'build-input-pins.json').write_text(json.dumps(record,indent=2)+'\n')
print(f'MERGE_AUDIT_PASS ROM_bytes=28641280 ROM_images={len(manifest["outputs"])} moved_inputs={len(moved)} remaining_inputs={len(ports["remaining_inputs"])} host_drives=0 pinned_files={len(paths)}')
