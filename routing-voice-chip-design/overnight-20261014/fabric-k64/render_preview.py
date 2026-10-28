from pathlib import Path
import json,sys
import pya
W=Path(__file__).resolve().parent
v=sys.argv[1];stage=sys.argv[2];c=json.loads((W/'runs'/f'{v}-v2/resolved.json').read_text())
p=W/'runs'/f'{v}-v2'/stage/f'rv_k64_{v}.def'
tech=pya.Technology();tech.load(c['KLAYOUT_TECH'])
opts=tech.load_layout_options;opts.lefdef_config.map_file=c['KLAYOUT_DEF_LAYER_MAP'];opts.lefdef_config.macro_resolution_mode=1;opts.lefdef_config.read_lef_with_def=False;opts.lefdef_config.lef_files=[c['TECH_LEFS']['nom_*'],*c['CELL_LEFS']]
lv=pya.LayoutView();lv.set_config('background-color','#FFFFFF');lv.set_config('grid-visible','false');lv.set_config('text-visible','false');lv.load_layout(str(p),opts,c['KLAYOUT_TECH']);lv.max_hier();lv.load_layer_props(c['KLAYOUT_PROPERTIES']);bbox=lv.active_cellview().layout().top_cell().dbbox()
out=W/'evidence'/f'{v}-placed.png';lv.save_image_with_options(str(out),1600,int(1600*bbox.height()/bbox.width()))
(W/'evidence'/f'{v}-placed-image.json').write_text(json.dumps({'stage':stage,'input_def':str(p),'output_png':str(out),'routed':False,'bbox_um':[bbox.left,bbox.bottom,bbox.right,bbox.top]},indent=2));print(out)
