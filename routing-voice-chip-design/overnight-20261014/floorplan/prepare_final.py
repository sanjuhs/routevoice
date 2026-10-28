#!/usr/bin/env python3
import json,copy,subprocess,sys
from pathlib import Path
from area_models import configure,block_area
from make_floorplan import tile_blocks,pack
W=Path(__file__).resolve().parent;cfg=json.loads((W/'blocks_final.json').read_text());rows=[]
for mem in cfg['memory_scenarios']:
 c=configure(cfg,mem,'lossless');aa=[block_area(c,b,'final_pitch') for b in c['blocks']];rows.append(dict(memory=mem,levers='frontend_native_int8_lossless + books_in_array',**{k:sum(a[k] for a in aa) for k in aa[0]},status=cfg['memory_scenarios'][mem]['status']))
choices=[];runs=[]
for mem,part in [('sram_bitcell_large_macro','whole'),('sram_dense_custom','whole'),('sram_open_macro','encoder'),('sram_open_macro','decoder')]:
 c=configure(cfg,mem,'lossless');tt,aa=tile_blocks(c,'final_pitch',part);trials=[dict(width_mm=x,height_mm=y,area_mm2=x*y,placement_pass=pack(copy.deepcopy(tt),x*1000,height=y*1000)) for x in range(16,50) for y in range(x,55) if y/x<=33/26];best=min((q['area_mm2'],q['width_mm'],q['height_mm']) for q in trials if q['placement_pass']);fit=pack(copy.deepcopy(tt),26000,height=33000)
 choice=dict(memory=mem,partition=part,minimum_rectangle=best,reticle26x33_pass=fit,trials=trials,search='integer-mm width16..49 height16..54, width<=height, aspect<=33/26, deterministic shelf packer/700um margin/30um halo');choices.append(choice)
 pads=48 if part=='whole' else 32;cmd=[sys.executable,str(W/'make_floorplan.py'),'--blocks',str(W/'blocks_final.json'),'--scenario','final_pitch','--memory',mem,'--levers','lossless','--partition',part,'--die-mm',str(best[1]),'--height-mm',str(best[2]),'--pdn-width-um','40','--supply-pad-pairs',str(pads)]
 subprocess.run(cmd,check=True);name=f'final_pitch_{mem}_lossless_baseline_{part}_{best[1]}x{best[2]}mm_pdn40_pads{pads}';runs.append(dict(name=name,command=cmd,**{k:v for k,v in choice.items() if k!='trials'}))
(W/'final_area_table.json').write_text(json.dumps(rows,indent=2)+'\n');(W/'final_outline_search.json').write_text(json.dumps(choices,indent=2)+'\n');(W/'final_runs.json').write_text(json.dumps(runs,indent=2)+'\n');print('W3-STATUS: final4physical cases generated; all use exact native frontend, original mutable state and readable-array books')
