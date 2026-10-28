#!/usr/bin/env python3
"""Synthetic one-inverter API qualification; never projection evidence."""
import os, subprocess, sys
from pathlib import Path
p=Path(__file__).resolve().parent; r=p.parents[2]; f=p/'api-fixture'
e=dict(os.environ); e.update({'W8_LIB_LIST':str(r/'pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib'),'W8_MACRO_LIB':str(p.parent/'macro/PITCH_BANK_R1280.lib'),'W8_NETLIST':str(f/'probe.v'),'W8_ACTIVITY_NETLIST':str(f/'probe.v'),'W8_TOP':'probe','W8_SDC':str(f/'probe.sdc'),'W8_SPEF':str(f/'probe.spef'),'W8_VCD':str(f/'probe.vcd'),'W8_OUT_DIR':str(p/sys.argv[1]),'W8_CORNER':'API_fixture_TT_not_projection','W8_STA':e.get('W8_STA','/nix/store/sc7lam0v6gsfzzcn993qcnkdzkzvnsk9-opensta/bin/sta'),'W8_ACTIVITY_NOTE':'Synthetic one-cell API fixture; no projection correctness or power evidence','W8_RATE_HZ':'25','PYTHONDONTWRITEBYTECODE':'1'})
sys.exit(subprocess.run([sys.executable,str(p/'run_power.py')],env=e,check=False).returncode)
