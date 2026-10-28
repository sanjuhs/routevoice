#!/usr/bin/env python3
"""Create explicit new-clock constraints from a preserved checkpoint; no RTL changes."""
import argparse,hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('variant');p.add_argument('state',type=Path);p.add_argument('period',type=float);p.add_argument('--base-config',type=Path);a=p.parse_args();assert a.period>0
state=a.state.resolve();d=json.loads(state.read_text());source=Path(d['sdc']);s=source.read_text();clock=re.search(r'create_clock -name clk -period ([\d.]+) ',s);assert clock
old=float(clock[1]);ratio=a.period/old;s=s[:clock.start(1)]+f'{a.period:.4f}'+s[clock.end(1):]
changes=[]
def delay(m):
 value=float(m[2]);changes.append([value,value*ratio]);return m[1]+f'{value*ratio:.4f}'+' '
s=re.sub(r'^(set_(?:input|output)_delay )([\d.]+) ',delay,s,flags=re.M);assert changes
slug=f'{a.period:g}ns';dest=r/'configs'/f'{a.variant}-{slug}.sdc';assert not dest.exists();dest.write_text(s)
d['sdc']=str(dest);out=r/'evidence'/f'{a.variant}-{slug}-initial-state.json';out.write_text(json.dumps(d,indent=2)+'\n')
c=json.loads((a.base_config if a.base_config else r/'configs'/f'{a.variant}.json').read_text());c.update(CLOCK_PERIOD=a.period,DEDUPLICATE_CORNERS=True,PNR_SDC_FILE=str(dest),SIGNOFF_SDC_FILE=str(dest));cfg=r/'configs'/f'{a.variant}-{slug}.json';cfg.write_text(json.dumps(c,indent=2)+'\n')
receipt={'source_state':str(state),'source_sdc':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'new_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'old_period_ns':old,'new_period_ns':a.period,'io_delay_pairs_ns':sorted(set(map(tuple,changes))),'io_delays_changed':len(changes),'config':str(cfg),'initial_state':str(out),'scope':'Explicit slower target from preserved checkpoint; no timing qualification claimed until extracted STA'}
(r/'evidence'/f'{a.variant}-{slug}-clock-change.json').write_text(json.dumps(receipt,indent=2)+'\n');print('W2-STATUS:',json.dumps(receipt))
