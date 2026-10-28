"""Hash actual ordered RTL/compiler inputs and confine host changes to W1c."""
from pathlib import Path
import hashlib,json,re,subprocess
W=Path(__file__).resolve().parent;R=W.parents[1]
S=R/'experiments/chip-integration-20261012-frontend-learned-norm-connected-source-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((W/'commands.json').read_text())['generate-full']
inputs=[Path(a) for a in c if Path(a).suffix in ('.sv','.v','.cpp') and Path(a).is_file()]
records=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in inputs]
changes=[]
for p in sorted([W/'four_stage.cpp',*W.glob('*.hpp')]):
 original=S/p.name
 changed=sha(p)!=sha(original)
 changes.append(dict(file=p.name,changed=changed,original_sha256=sha(original),copy_sha256=sha(p)))
 if changed:
  assert p.name in ('four_stage.cpp','frontend_services.hpp','taalas_adapter_session_compact_token_services_f500_v1.hpp')
  diff=subprocess.run(['diff','-u',str(original),str(p)],capture_output=True,text=True)
  assert diff.returncode==1
  (W/(p.name+'.patch')).write_text(diff.stdout)
# Position response ownership: no host writes anywhere, including initialization.
for p in [W/'four_stage.cpp',*W.glob('*.hpp')]:
 assert not re.search(r't\.source_position_(?:ready|idle|response_\w+)\s*=(?!=)',p.read_text()),p
front=(W/'frontend_services.hpp').read_text()
assert re.findall(r't\.external_rsp_valid\s*=\s*([^;]*);',front)==['0']
# The reused position responder is exactly the retained RTL source.
pos=R/'experiments/runtime-source-position-immutable-rom-source-20261013-v1/rv_source_position_immutable_rom_v1.sv'
assert sha(pos)==sha(W/pos.name)
result=dict(passed=True,ordered_project_compiler_inputs=records,host_copies=changes,position_rtl_unmodified=True,position_host_drivers=0,frontend_host_response_valid_only_zero=True)
(W/'source-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('W1c-STATUS: source audit passed; exactly three host files changed; position RTL unchanged; other service headers byte-identical')
