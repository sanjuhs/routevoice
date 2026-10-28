"""Regenerate a proposed config; the frozen configs/complete.json drove v3."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--output',default='configs/regenerated.json',help='Relative to W8 workspace; frozen active configuration is not overwritten by default')
a=p.parse_args()
R=Path.cwd();W=R/'overnight-20261014/projection-complete';S=R/'overnight-20261014/fabric-k64'
c=json.loads((S/'configs/array_port.json').read_text())
c.update(DESIGN_NAME='rv_k64_projection_complete',VERILOG_FILES=[str(W/'rtl/engine_mapped.nl.v'),str(W/'rtl/rv_k64_projection_complete.sv')],VERILOG_INCLUDE_DIRS=[],CLOCK_PERIOD=20.0,FP_SIZING='absolute',DIE_AREA=[0,0,4500,4500],FP_CORE_UTIL=40,PL_TARGET_DENSITY_PCT=45,DRT_THREADS=10,STA_THREADS=2,RUN_POST_GPL_DESIGN_REPAIR=False,RUN_POST_GRT_DESIGN_REPAIR=False,RUN_POST_CTS_RESIZER_TIMING=False,RUN_POST_GRT_RESIZER_TIMING=False,PDN_MACRO_CONNECTIONS=['bank VDD VSS VDD VSS'],PDN_CONNECT_MACROS_TO_GRID=True,STA_MACRO_PRIORITIZE_NL=False)
c['MACROS']={'PITCH_BANK_R1280':{'gds':[str(W/'macro/bank.gds')],'lef':[str(W/'macro/PITCH_BANK_R1280.lef')],'nl':[str(W/'macro/PITCH_BANK_R1280.v')],'lib':{'*':[str(W/'macro/PITCH_BANK_R1280.lib')]},'instances':{'bank':{'location':[500,1200],'orientation':'N'}}}}
c['LINTER_DISABLE_WARNINGS']=['PINMISSING']
c['RUN_LINTER']=False # v3 reuses mapped engine; raw RTL simulation and Yosys synthesis checks are retained.
# Retain default edge checks initially: do not quietly waive bank timing with a false path.
# Proxy PC->OUT44ns will show single-cycle failure until explicit multicycle phases are qualified.
(W/a.output).write_text(json.dumps(c,indent=2)+'\n')
