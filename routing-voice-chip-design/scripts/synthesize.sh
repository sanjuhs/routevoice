#!/usr/bin/env bash
# Local Yosys structural check. Mapping requires an explicit GF180 Liberty file.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
name="${1:?Usage: synthesize.sh module_name [liberty]}"
[[ "$name" =~ ^[a-zA-Z_][a-zA-Z_0-9]*$ ]] || { echo 'Invalid module name' >&2; exit 1; }
mkdir -p "$root/build" "$root/reports"
export ROUTING_SYNTH_ROOT="$root" ROUTING_SYNTH_NAME="$name" ROUTING_SYNTH_LIBERTY="${2:-}"
python3 - <<'PY'
import os,pathlib,subprocess
root=pathlib.Path(os.environ['ROUTING_SYNTH_ROOT']);name=os.environ['ROUTING_SYNTH_NAME'];lib=os.environ['ROUTING_SYNTH_LIBERTY']
def q(value):return '"'+str(value).replace('\\','\\\\').replace('"','\\"')+'"'
source=root/'rtl'/f'{name}.sv'
if not source.is_file():raise SystemExit(f'Missing {source}')
commands=[f'read_verilog -sv {q(source)}',f'hierarchy -check -top {name}',f'synth -top {name} -noabc']
if lib:
 if not pathlib.Path(lib).is_file():raise SystemExit('Liberty file missing')
 commands += [f'read_liberty -lib {q(lib)}',f'dfflibmap -liberty {q(lib)}',f'abc -liberty {q(lib)}',f'stat -liberty {q(lib)}']
else:commands += ['abc','stat']
commands += ['check -assert',f'write_json {q(root/"build"/(name+".json"))}',f'write_verilog -noattr {q(root/"build"/(name+".v"))}']
script=root/'build'/f'{name}.ys';script.write_text('\n'.join(commands)+'\n')
with (root/'reports'/f'{name}-synthesis.txt').open('w') as log:subprocess.run(['yosys','-s',str(script)],stdout=log,stderr=subprocess.STDOUT,check=True)
PY
