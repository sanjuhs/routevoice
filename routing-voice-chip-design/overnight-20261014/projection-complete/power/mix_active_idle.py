#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from idle_accounting import mix_active_idle
p=argparse.ArgumentParser();p.add_argument('active');p.add_argument('idle');p.add_argument('--rate-hz',type=float,required=True);p.add_argument('--output',required=True);a=p.parse_args()
r=mix_active_idle(json.loads(Path(a.active).read_text()),json.loads(Path(a.idle).read_text()),a.rate_hz)
with Path(a.output).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print('W8-POWER: always-clocked conditional mixture written; full-array power remains unknown')
