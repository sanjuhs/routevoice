from pathlib import Path
import os,subprocess,json,shutil,time
W=Path(__file__).resolve().parent;R=W.parents[3];O=W/'v1';PDK=R/'pdks/gf180mcuD'
assert shutil.disk_usage('/').free>=22*2**30
(O/'extract.tcl').write_text('''gds readonly true
gds read decoded-tile.gds
load RV_K64_DECODED_TILE_00
flatten W5_DECODED_TILE_FLAT
load W5_DECODED_TILE_FLAT
extract all
ext2spice lvs
ext2spice -o decoded-tile-extracted.spice
quit -noprompt
''')
cmd=['nice','-n','10','magic','-dnull','-noconsole','-rcfile',str(PDK/'libs.tech/magic/gf180mcuD.magicrc'),'extract.tcl'];(O/'extract-command.json').write_text(json.dumps(cmd,indent=2))
t=time.monotonic()
with (O/'extract.log').open('w') as f:r=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PDK_ROOT=str(PDK.parent),TMPDIR=str(O)))
print({'returncode':r.returncode,'seconds':time.monotonic()-t},flush=True)
