from pathlib import Path
import argparse,os,shutil,json,hashlib,subprocess,time,re
W=Path(__file__).resolve().parent;A=W.parents[1];R=A.parents[1]
p=argparse.ArgumentParser();p.add_argument('--rows',type=int,default=320);p.add_argument('--version',default='v1');p.add_argument('--group',type=int);args=p.parse_args();H=args.rows;O=W/f'r{H}-{args.version}';O.mkdir(exist_ok=True);source=W.parent/f'r{H}';geo=json.loads((source/'geometry.json').read_text());assert shutil.disk_usage('/').free>=22*2**30
shutil.copyfile(source/'geometry.json',O/'source-geometry.json');joined=geo['tops']['timing_subbank'];m=re.fullmatch(r'TALL_JOINED_R\d+_B(\d+)_G(\d+)',joined);assert m; b,g=int(m[1]),int(m[2]);
if args.group is not None:
 import klayout.db as k
 g=args.group;joined=f'TALL_JOINED_R{H}_B{b:02d}_G{g:02d}';L=k.Layout();L.read(str(source/'assembly.gds'));opt=k.SaveLayoutOptions();opt.select_cell(L.cell(joined).cell_index());L.write(str(O/'source-joined.gds'),opt)
else:shutil.copyfile(source/'timing-subbank.gds',O/'source-joined.gds')
array=f'TALL_ARRAY_B{b:02d}_G{g:02d}'
script=['gds readonly true','gds read source-joined.gds']
for kind,top in [('array',array),('joined',joined)]:
 script.extend([f'load {top}',f'flatten TALL_TIMING_{kind.upper()}',f'load TALL_TIMING_{kind.upper()}','extract all','ext2spice lvs',f'ext2spice -o {kind}-lvs.spice','ext2spice cthresh 0',f'ext2spice -o {kind}-cap.spice'])
script.append('quit -noprompt');(O/'extract.tcl').write_text('\n'.join(script)+'\n');cmd=['nice','-n','10','magic','-dnull','-noconsole','-rcfile',str(R/'pdks/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc'),'extract.tcl'];(O/'extract-command.json').write_text(json.dumps(cmd,indent=2));start=time.monotonic()
with (O/'extract.log').open('w') as f:r=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PDK_ROOT=str(R/'pdks'),TMPDIR=str(O)),timeout=600)
report={'returncode':r.returncode,'seconds':time.monotonic()-start,'source_gds_sha256':hashlib.sha256((O/'source-joined.gds').read_bytes()).hexdigest(),'rows':H,'bank':b,'subbank':g,'lane_start':g*32,'out_start':g*128,'row_stride':1280//H,'source_top':joined,'array_top':array};(O/'extraction.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
