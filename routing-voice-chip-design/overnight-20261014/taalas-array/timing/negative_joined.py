from pathlib import Path
import subprocess,json
B=Path(__file__).resolve().parent;W=B/'joined-bank0-v2';R=B.parents[2]
s=(W/'reference.spice').read_text();pos=s.index('w=0.36u');bad=s[:pos]+s[pos:].replace('w=0.36u','w=0.72u',1)
(W/'negative-width-reference.spice').write_text(bad)
args=['nice','-n','10','netgen','-batch','lvs',f'{W/"joined-lvs-canonical.spice"} RV_JOINED_FLAT',f'{W/"negative-width-reference.spice"} RV_JOINED_REF',str(R/'pdks/gf180mcuD/libs.tech/netgen/setup.tcl'),str(W/'negative-width-comparison.log')]
with (W/'negative-width-netgen.log').open('w') as f:subprocess.run(args,cwd=W,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
s=(W/'negative-width-comparison.log').read_text();r={'negative_control':'First access device width doubled from0.36um to0.72um in independent reference only','mismatch_detected':'Property errors were found.' in s};(W/'negative-width-result.json').write_text(json.dumps(r,indent=2));print(r)
