#!/usr/bin/env python3
import json
from PIL import Image
from render_heatmaps import render,W
runs=json.loads((W/'final_runs.json').read_text());ims=[render(r['name']) for r in runs]
joined=Image.new('RGB',(2600,1470),'white');joined.paste(ims[2],(0,0));joined.paste(ims[3],(1300,0));joined.save(W/'final_open_two_die_ir_heatmap.png')
layouts=Image.new('RGB',(3200,1950),'white')
for pos,idx in enumerate([2,3]):
 im=Image.open(W/'runs'/runs[idx]['name']/'floorplan.png').convert('RGB');im.thumbnail((1600,1950));layouts.paste(im,(1600*pos,0))
layouts.save(W/'final_open_two_die_floorplan.png');print('W3-STATUS: final4layout/IR renders and two-die composites complete')
