"""Extract new W6 stacked subbank; source layout is read-only."""
from pathlib import Path
import argparse,os,shutil,json,hashlib,subprocess,time,re
import numpy as np
W=Path(__file__).resolve().parent; R=W.parents[2]; A=R/'overnight-20261014/taalas-array'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--rows',type=int,default=1280);p.add_argument('--group',type=int);p.add_argument('--extract-only',action='store_true');args=p.parse_args();H=args.rows
assert shutil.disk_usage('/').free>=22*2**30
geometry=json.loads((args.source.parent/'geometry.json').read_text()); route_by_bit={r['bc']:r for r in geometry['join_routes_subbank0']}; image=np.load(A/'indices.npy')[:H];bits=((image[:,:,None]>>np.arange(4))&1).reshape(H,1280);population=bits.sum(0);records=[]
for n in range(1280):
 bc=n%128;route=route_by_bit[bc];length=sum(route[f'metal{i}_length_um'] for i in [2,3,4])
 resistance=.104*length/.38+4*15
 records.append({'global_bit_column':n,'subbank':n//128,'local_bit_column':bc,'connected_drains':int(population[n]),'join_length_um':length,'join_ohm25':resistance,'selection_proxy':float(population[n]*(resistance+.104*(H*1.44+(H//8-1)*1.8)/.38/2))})
records.sort(key=lambda d:d['selection_proxy'],reverse=True);g=args.group if args.group is not None else records[0]['subbank'];O=W/f'r{H}-g{g:02d}';O.mkdir(exist_ok=False)
(O/'global-proxy-ranking.json').write_text(json.dumps({'method':'Connected-drain population times new geometry joinR+half arrayR; initial all1280-column heuristic, not actual extracted C or worst-case proof','ranking':records},indent=2))
import klayout.db as k
L=k.Layout();L.read(str(args.source));joined=f'PITCH_JOINED_R{H}_G{g:02d}';array=f'PITCH_ARRAY_R{H}_G{g:02d}';opt=k.SaveLayoutOptions();opt.select_cell(L.cell(joined).cell_index());L.write(str(O/'source-joined.gds'),opt)
script=['gds readonly true','gds read source-joined.gds']
for kind,top in [('array',array),('joined',joined)]:
 script.extend([f'load {top}',f'flatten W6_TIMING_{kind.upper()}',f'load W6_TIMING_{kind.upper()}','extract all','ext2spice lvs',f'ext2spice -o {kind}-lvs.spice','ext2spice cthresh 0',f'ext2spice -o {kind}-cap.spice'])
script.append('quit -noprompt');(O/'extract.tcl').write_text('\n'.join(script)+'\n');cmd=['nice','-n','10','magic','-dnull','-noconsole','-rcfile',str(R/'pdks/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc'),'extract.tcl'];(O/'extract-command.json').write_text(json.dumps(cmd,indent=2));start=time.monotonic()
with (O/'extract.log').open('w') as f:r=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PDK_ROOT=str(R/'pdks'),TMPDIR=str(O)),timeout=600)
report={'returncode':r.returncode,'seconds':time.monotonic()-start,'source_gds_sha256':sha(O/'source-joined.gds'),'fullbank_source_gds_sha256':sha(args.source),'rows':H,'bank':0,'subbank':g,'lane_start':g*32,'out_start':g*128,'row_stride':1,'source_top':joined,'array_top':array};(O/'extraction.json').write_text(json.dumps(report,indent=2));np.save(O/'image.npy',image[:,g*32:(g+1)*32]);(O/'source-geometry.json').write_text(json.dumps(geometry,indent=2));print('W6-STATUS: new stacked subbank extracted',report,flush=True)
