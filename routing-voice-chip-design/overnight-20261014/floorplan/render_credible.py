#!/usr/bin/env python3
import json
from PIL import Image
from render_heatmaps import render,W
runs=json.loads((W/'credible_runs.json').read_text());ims=[render(r['name']) for r in runs]
for label,a,b in [('on',1,2),('books',3,4)]:
 joined=Image.new('RGB',(2600,1470),'white');joined.paste(ims[a],(0,0));joined.paste(ims[b],(1300,0));joined.save(W/f'credible_open_{label}_two_die_ir_heatmap.png')
 layouts=Image.new('RGB',(3200,1950),'white')
 for pos,idx in enumerate([a,b]):
  im=Image.open(W/'runs'/runs[idx]['name']/'floorplan.png').convert('RGB');im.thumbnail((1600,1950));layouts.paste(im,(1600*pos,0))
 layouts.save(W/f'credible_open_{label}_two_die_floorplan.png')
print('W3-STATUS: credible5layout/IR renders and2two-die composites complete')
