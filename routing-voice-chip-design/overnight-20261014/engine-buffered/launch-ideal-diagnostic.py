from pathlib import Path
import json,hashlib,subprocess
W=Path('/workspace/rv/overnight-20261014/engine-buffered')
assert not (W/'runs/buf-v4-idealprects').exists()
sp=W/'runs/buf-v4/25-checker-powergridviolations/state_out.json';state=json.loads(sp.read_text());sdc=Path(state['sdc']);old=sdc.read_text();line='set_propagated_clock [get_clocks {clk}]';assert old.count(line)==1
new=old.replace(line,'unset_propagated_clock [get_clocks {clk}]');out=W/'evidence/ideal-prects.sdc';out.write_text(new);state['sdc']=str(out)
(W/'evidence/ideal-prects-state.json').write_text(json.dumps(state,indent=2)+'\n')
r={'status':'diagnostic_deviation_from_requested_STA_behavior','change':'Only pre-CTS clock propagation changes from propagated to ideal; CTS script line 91 explicitly sets propagated clocks after constructing the tree. 20ns, all numeric constraints and all repair/signoff settings unchanged.','original_state':str(sp),'original_sdc':str(sdc),'original_sdc_sha256':hashlib.sha256(old.encode()).hexdigest(),'diagnostic_sdc':str(out),'diagnostic_sdc_sha256':hashlib.sha256(new.encode()).hexdigest(),'original_run_continues':'buf-v4-physical','observed_preCTS_clock_loads':11784,'observed_preCTS_clock_slew_ns':300.452423,'cts_source':'/nix/store/1v4pl3wcjvysadks22gj14b8qj9qz20d-python3-3.13.9-env/lib/python3.13/site-packages/librelane/scripts/openroad/cts.tcl:91'}
(W/'evidence/ideal-prects-deviation.json').write_text(json.dumps(r,indent=2)+'\n')
with (W/'logs/flow-v4-idealprects-launcher.log').open('w') as f:p=subprocess.Popen(['bash','run-flow-v4-idealprects.sh'],cwd=W,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(W/'evidence/flow-v4-idealprects.pid').write_text(str(p.pid)+'\n');print(p.pid)
