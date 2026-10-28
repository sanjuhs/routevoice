#!/usr/bin/env python3
"""Bounded synthetic API tests; no actual projection timing/power evidence."""
import json,os,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parent;r=p.parents[2];f=p/'api-fixture'
e=dict(os.environ);e.update({'W8_LIB_LIST':str(r/'pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib'),'W8_MACRO_LIB':str(p.parent/'macro/PITCH_BANK_R1280.lib'),'W8_NETLIST':str(f/'probe.v'),'W8_ACTIVITY_NETLIST':str(f/'probe.v'),'W8_TOP':'probe','W8_SDC':str(f/'probe.sdc'),'W8_SPEF':str(f/'probe.spef'),'W8_CORNER':'API_fixture_TT_not_projection','W8_STA':e.get('W8_STA','/nix/store/sc7lam0v6gsfzzcn993qcnkdzkzvnsk9-opensta/bin/sta'),'W8_ACTIVITY_NOTE':'Synthetic API fixture only','PYTHONDONTWRITEBYTECODE':'1'})
prefix=sys.argv[1] if len(sys.argv)>1 else 'idle-timing-api'
e.update({'W8_WORKLOAD_KIND':'idle','W8_COMPLETED_PROJECTIONS':'0','W8_VCD':str(f/'idle.vcd'),'W8_OUT_DIR':str(p/(prefix+'-idle'))})
subprocess.run([sys.executable,str(p/'run_power.py')],env=e,check=True)
idle=json.loads((Path(e['W8_OUT_DIR'])/'results.json').read_text());assert idle['modeled_total_J_per_projection_in_trace'] is None and idle['requested_rate_projection'] is None
idle_result=str(Path(e['W8_OUT_DIR'])/'results.json')
e.update({'W8_WORKLOAD_KIND':'active','W8_COMPLETED_PROJECTIONS':'1','W8_VCD':str(f/'probe.vcd'),'W8_OUT_DIR':str(p/(prefix+'-active')),'W8_RATE_HZ':'50','W8_IDLE_RESULT':idle_result})
subprocess.run([sys.executable,str(p/'run_power.py')],env=e,check=True)
active=json.loads((Path(e['W8_OUT_DIR'])/'results.json').read_text());mix=active['requested_rate_projection'];assert mix['conditional_modeled_power_W'] is not None and mix['complete_projection_power_W'] is None
# Standard-cell output substitute exercises only Tcl selection/exception API.
e.update({'W8_OUT_DIR':str(p/(prefix+'-timing')),'W8_MACRO_OUTPUT_PATTERN':'_cell_/ZN'})
subprocess.run([sys.executable,str(p/'run_timing.py')],env=e,check=True)
timing=json.loads((Path(e['W8_OUT_DIR'])/'results.json').read_text())
assert timing['scenarios']['original']['setup_worst_slack_report_units'] is not None
assert timing['scenarios']['macro-multicycle-3-2']['hold_worst_slack_report_units'] is not None
print('W8-STATUS: synthetic idle, active/idle accounting and two timing scenarios API tests PASS')
