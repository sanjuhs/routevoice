"""Run unchanged retained postflight predicates on W1b logs/outputs, plus W1b coverage."""
import ast,hashlib,json,re,struct,sys
from pathlib import Path
W=Path(__file__).resolve().parent
R=W.parents[1]
RUN=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-enc'
source=R/'scripts/run_routevoice_Q8_learned_fulltables_numerical_20261012_v2.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Extract only the pure artifact parser; never invoke original dispatch/admission code.
node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='postflight')
env=dict(re=re,json=json,Path=Path,sha=sha,ACTIVE=RUN,SOURCE_BINDING=R/'experiments/voice-e2e-20261012-onboard-numerical-binding-v1/binding-audit.json')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),env)
log=Path(sys.argv[1]);raw=log.read_text();record=json.loads(log.with_suffix('.json').read_text());assert record['exit_code']==0
for path,info in json.loads((W/'run-input-pins.json').read_text()).items():
 assert Path(path).stat().st_size==info['bytes'] and sha(path)==info['sha256'],path
for path,digest in json.loads((W/'source-provenance.json').read_text()).items():assert sha(path)==digest,path
manifest=json.loads((W/'rom-manifest.json').read_text())
for path,info in manifest['inputs'].items():assert sha(path)==info['sha256'],path
for info in manifest['outputs']:assert sha(info['path'])==info['sha256'],info['path']
result=env['postflight'](raw)
counts={}
for service,n in [('encoder_QKV',368640),('encoder_O',15360),('encoder_immutable',1947520)]:
 line=f'ONCHIP service={service} rtl_replies={n} host_replies=0 mismatches=0'
 assert raw.splitlines().count(line)==1
 counts[service]=dict(rtl_replies=n,host_replies=0,mismatches=0)
tokens=list(struct.unpack('<5I',(RUN/'actual/actual-winning-tokens.bin').read_bytes()))
assert tokens==[28176,373,278,26068,2]
result.update(passed=True,services=counts,tokens=tokens,positive_log=str(log),elapsed_seconds=record['elapsed_seconds'],postflight_source_sha256=sha(source))
(W/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print('W1b-STATUS: all 18 frozen output comparisons PASS; tokens='+str(tokens)+'; all encoder host_replies=0 mismatches=0')
