#!/usr/bin/env python3
"""Load configs against the actual PDK without claiming physical execution."""
import json
from pathlib import Path
from librelane.flows.classic import Classic
ROOT=Path(__file__).resolve().parents[1];rows=[]
for p in sorted((ROOT/'physical').glob('die*.json')):
    flow=Classic(str(p),pdk_root=str(ROOT/'pdks'),pdk='gf180mcuD');c=flow.config
    rows.append({'config':p.name,'top':c['DESIGN_NAME'],'library':c['STD_CELL_LIBRARY'],'clock_ns':str(c['CLOCK_PERIOD']),'sources':[str(v) for v in c['VERILOG_FILES']]})
if len(rows)!=6:raise SystemExit('Expected parallel and serial configs for three slices')
(ROOT/'reports/physical-config-check.json').write_text(json.dumps({'status':'pass','scope':'Config load only; no physical run','configs':rows},indent=2)+'\n');print('Validated all six physical configurations')
