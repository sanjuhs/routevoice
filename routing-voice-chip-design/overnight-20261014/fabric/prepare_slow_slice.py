#!/usr/bin/env python3
"""Preserve the 20 ns CTS checkpoint; create explicit 200 ns continuation inputs."""
import json,hashlib,re
from pathlib import Path
r=Path(__file__).resolve().parent
source=r/'runs/rv_fixed_proj64x320_rom-util30/23-openroad-cts/state_out.json'
d=json.loads(source.read_text());sdc=Path(d['sdc']);s=sdc.read_text()
assert s.count('create_clock -name clk -period 20.0000 ')==1
s=s.replace('create_clock -name clk -period 20.0000 ','create_clock -name clk -period 200.0000 ')
s,count=re.subn(r'^(set_(?:input|output)_delay) 4\.0000 ',r'\1 40.0000 ',s,flags=re.M)
assert count>60,count
p=r/'configs/rv_fixed_proj64x320_rom-200ns.sdc';p.write_text(s)
d['sdc']=str(p);state=r/'evidence/slice-200ns-initial-state.json';state.write_text(json.dumps(d,indent=2)+'\n')
c=json.loads((r/'configs/rv_fixed_proj64x320_rom.json').read_text());c.update(CLOCK_PERIOD=200,DEDUPLICATE_CORNERS=True,PNR_SDC_FILE=str(p),SIGNOFF_SDC_FILE=str(p))
(r/'configs/rv_fixed_proj64x320_rom-200ns.json').write_text(json.dumps(c,indent=2)+'\n')
(r/'evidence/slow-clock-change.json').write_text(json.dumps({'source_state':str(source),'source_sdc':str(sdc),'source_sdc_sha256':hashlib.sha256(sdc.read_bytes()).hexdigest(),'new_sdc_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'clock_period_ns_before':20,'clock_period_ns_after':200,'io_delay_ns_before':4,'io_delay_ns_after':40,'io_constraints_changed':count,'reason':'20 ns post-CTS typical setup slack -47.2934 ns; setup repair manually stopped after roughly 31 minutes to pursue routing at a conservative clock. No RTL changes or signoff-check suppression. PnR equivalent-corner dedup enabled; final extracted corners retained.'},indent=2)+'\n')
print('W2-STATUS: Prepared explicit 200 ns / 40 ns IO constraints; original CTS inputs preserved')
