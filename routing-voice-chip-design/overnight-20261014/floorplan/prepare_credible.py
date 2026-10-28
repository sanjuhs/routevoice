#!/usr/bin/env python3
"""Area/geometry search; generate only requested physical cases."""
import json,copy,itertools,subprocess,sys
from pathlib import Path
from area_models import configure,block_area
from make_floorplan import tile_blocks,pack
W=Path(__file__).resolve().parent;cfg=json.loads((W/'blocks_credible.json').read_text());rows=[]
for m,l in itertools.product(cfg['memory_scenarios'],['off','on','books']):
 c=configure(cfg,m,l);a=[block_area(c,b,'pitch1280v2') for b in c['blocks']];rows.append(dict(memory=m,levers=l,**{k:sum(p[k] for p in a) for k in a[0]}))
choices=[];runs=[]
for mem,l,part,run in [('sram_dense_custom','on','whole',True),('sram_dense_custom','off','whole',False),('sram_open_macro','on','encoder',True),('sram_open_macro','on','decoder',True),('sram_open_macro','books','encoder',True),('sram_open_macro','books','decoder',True),('sram_open_macro','books','whole',False)]:
 c=configure(cfg,mem,l);tt,aa=tile_blocks(c,'pitch1280v2',part);trials=[dict(width_mm=x,height_mm=y,area_mm2=x*y,placement_pass=pack(copy.deepcopy(tt),x*1000,height=y*1000)) for x in range(16,50) for y in range(x,55) if y/x<=33/26];best=min((q['area_mm2'],q['width_mm'],q['height_mm']) for q in trials if q['placement_pass']);fit=pack(copy.deepcopy(tt),26000,height=33000)
 choice=dict(memory=mem,levers=l,partition=part,minimum_rectangle=best,reticle26x33_pass=fit,trials=trials,search='integer mm width16..49 height16..54, width<=height, aspect<=33/26, same shelf packer/700um margin/30um halo',physical_requested=run);choices.append(choice)
 if run:
  pads=48 if part=='whole' else 32
  cmd=[sys.executable,str(W/'make_floorplan.py'),'--blocks',str(W/'blocks_credible.json'),'--scenario','pitch1280v2','--memory',mem,'--levers',l,'--partition',part,'--die-mm',str(best[1]),'--height-mm',str(best[2]),'--pdn-width-um','40','--supply-pad-pairs',str(pads)]
  subprocess.run(cmd,check=True);name=f'pitch1280v2_{mem}_{l}_baseline_{part}_{best[1]}x{best[2]}mm_pdn40_pads{pads}';runs.append(dict(name=name,command=cmd,**{k:v for k,v in choice.items() if k!='trials'}))
(W/'credible_area_table.json').write_text(json.dumps(rows,indent=2)+'\n');(W/'credible_outline_search.json').write_text(json.dumps(choices,indent=2)+'\n');(W/'credible_runs.json').write_text(json.dumps(runs,indent=2)+'\n')
print('W3-STATUS: credible9area rows (off/on/books-only),5requested physical cases generated; no KV8 or dedup credited')
