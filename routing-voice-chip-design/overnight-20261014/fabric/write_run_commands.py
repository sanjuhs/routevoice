#!/usr/bin/env python3
"""Render exact recorded launch controls without claiming they all succeeded."""
import json,shlex
from pathlib import Path
r=Path(__file__).resolve().parent
out=['# Recorded W2 physical launch commands','', 'These are provenance commands, not a request to rerun failed attempts. Run directories and frozen `resolved.json` files retain each attempt’s actual configuration. Current base configs incorporate documented corrections. Checkpoint paths may require archive restoration; see `evidence/checkpoint-path-audit.json`.','']
for p in sorted((r/'evidence').glob('*.supervisor.json'),key=lambda p:json.loads(p.read_text()).get('start_unix',0)):
 d=json.loads(p.read_text());out.extend([f'## {p.name}', '', f"Exit: `{d.get('exit_code')}`; stop reason: `{d.get('stop_reason')}`; elapsed: {d.get('elapsed_seconds',0):.2f} seconds.", '', '```sh'])
 control=d.get('flow_controls',{});cmd=['env']+[f'{k}={v}' for k,v in control.items()]+d['command'];out.extend([shlex.join(cmd),'```',''])
out.extend(['Every completed LibreLane step has its actual tool command in `runs/<attempt>/<step>/COMMANDS`. Gate compiler/simulator argv are in `evidence/*gate*verification.json` and `evidence/*activity-stream.json`. Original RTL commands are in `verify.sh`; the exact NumPy seed, dimensions and input hashes are in `evidence/generation.json`.',''])
(r/'RUN-COMMANDS.md').write_text('\n'.join(out));print('W2-STATUS: Recorded physical launch command ledger refreshed')
