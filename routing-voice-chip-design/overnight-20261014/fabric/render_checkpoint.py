#!/usr/bin/env python3
"""Render a preserved DEF checkpoint, explicitly labelled pre-route/non-signoff."""
import json,os,shutil,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;variant=sys.argv[1];source=Path(sys.argv[2]).resolve();base=Path(sys.argv[3]).resolve();tag='pre-route-render';assert not (r/'runs'/f'{variant}-{tag}').exists()
d=json.loads(source.read_text());assert d.get('def');minimal={k:(v if k in ['def','metrics'] else None) for k,v in d.items()};state=r/'evidence'/f'{variant}-{tag}-state.json';state.write_text(json.dumps(minimal,indent=2)+'\n')
env=os.environ.copy();env.update(W2_FROM_STEP='KLayout.Render',W2_TO_STEP='KLayout.Render',W2_INITIAL_STATE=str(state),W2_CONFIG_PATH=str(base),W2_NUM_THREADS='1',W2_MIN_FREE_GIB='23',W2_LIMIT_SECONDS='600')
status=subprocess.run([sys.executable,str(r/'supervise.py'),variant,tag],env=env).returncode
pngs=list((r/'runs'/f'{variant}-{tag}').glob('*-klayout-render/*.png'))
if status==0 and pngs:
 out=r/f'{variant}-PRE-ROUTE-NOT-SIGNOFF.png';shutil.copy2(pngs[0],out)
 (r/'evidence'/f'{variant}-{tag}-image.json').write_text(json.dumps(dict(source_state=str(source),source_def=d['def'],output=str(out.relative_to(r)),scope='Pre-route placement/PDN view; not final routed layout or signoff evidence'),indent=2)+'\n');print('W2-STATUS: pre-route KLayout image saved',out)
raise SystemExit(status)
