#!/usr/bin/env python3
"""Deterministic geometric search only; no EDA sweep."""
import sys,json,copy
from pathlib import Path
from make_floorplan import pack,tile_blocks
from area_models import configure
W=Path(__file__).resolve().parent;c=configure(json.loads((W/'blocks_measured.json').read_text()));choices=[]
for partition in ['whole','encoder','decoder']:
 t,a=tile_blocks(c,'measured320',partition)
 trials=[dict(width_mm=x,height_mm=y,area_mm2=x*y,pass_placement=pack(copy.deepcopy(t),x*1000,height=y*1000)) for x in range(18,61) for y in range(x,65) if y/x<=33/26]
 feasible=[(q['area_mm2'],q['width_mm'],q['height_mm']) for q in trials if q['pass_placement']];best=min(feasible)
 choices.append(dict(partition=partition,area_mm2=sum(z['area_mm2'] for z in a),minimum_integer_rectangle=best,reticle_pass=pack(copy.deepcopy(t),26000,height=33000),search='integer mm, width18..60 height18..64, width<=height, aspect<=33/26, deterministic shelf packing',trials=trials))
 print('W3-STATUS: geometric minimum',partition,best,'reticle26x33',choices[-1]['reticle_pass'])
(W/'measured_outline_search.json').write_text(json.dumps(choices,indent=2)+'\n')
