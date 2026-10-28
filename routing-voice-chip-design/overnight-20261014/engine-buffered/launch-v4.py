import subprocess,json,os
from pathlib import Path
W=Path('/workspace/rv/overnight-20261014/engine-buffered')
assert not (W/'runs/buf-v4').exists()
for x in ['synthesis-fanout.json','gate-full.status','gate-activity.status','rtl-full.status']:
 p=W/'evidence'/x
 if p.exists():p.rename(p.with_name('pre-v4-'+x))
cmds={'flow-v4':['bash','run-flow-v4.sh'],'watch-gate-v4':['bash','watch-gate-v4.sh'],'finish-v4':['bash','run-finish.sh'],'rtl-v4':['bash','-c','. /nix/var/nix/profiles/default/etc/profile.d/nix.sh; export NIX_REMOTE=local NIX_BUILD_SHELL=/bin/bash; nix-shell /workspace/rv/tools/librelane/shell.nix --run "bash /workspace/rv/overnight-20261014/engine-buffered/run-rtl.sh"']}
for name,args in cmds.items():
 with (W/'logs'/f'{name}-launcher.log').open('w') as f:
  p=subprocess.Popen(args,cwd=W,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 (W/'evidence'/f'{name}.pid').write_text(str(p.pid)+'\n');print(name,p.pid)
