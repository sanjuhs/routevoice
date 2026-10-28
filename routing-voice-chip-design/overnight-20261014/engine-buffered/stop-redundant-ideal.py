import os,signal,subprocess,json
from pathlib import Path
W=Path(__file__).resolve().parent;root=int((W/'evidence/flow-v4-idealprects.pid').read_text())
assert b'run-flow-v4-idealprects.sh' in Path(f'/proc/{root}/cmdline').read_bytes()
rows=[tuple(map(int,l.split())) for l in subprocess.check_output(['ps','-eo','pid=,ppid='],text=True).splitlines()];owned={root}
while True:
 expanded=owned|{pid for pid,ppid in rows if ppid in owned}
 if expanded==owned:break
 owned=expanded
for pid in sorted(owned,reverse=True):
 try:os.kill(pid,signal.SIGTERM)
 except ProcessLookupError:pass
r={'status':'stopped_redundant_diagnostic','stopped_owned_pids':sorted(owned),'reason':'Pinned repair_design.tcl explicitly executes unset_propagated_clock before all repairs. The ideal-input-SDC diagnostic cannot change this repair clock state and is redundant. DESIGN_REPAIR_REMOVE_BUFFERS=false preserves synthesis buffers. Main requested-settings repair remains running.','source':'/nix/store/1v4pl3wcjvysadks22gj14b8qj9qz20d-python3-3.13.9-env/lib/python3.13/site-packages/librelane/scripts/openroad/repair_design.tcl'}
(W/'evidence/ideal-prects-stopped.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
