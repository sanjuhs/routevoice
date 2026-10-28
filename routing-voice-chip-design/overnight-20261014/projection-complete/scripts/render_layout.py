"""Run with KLayout -b -r; render the actual DEF with its real macro abstract."""
from pathlib import Path
import os,json,pya
c=json.loads(Path(os.environ['W8_IMAGE_CONFIG']).read_text())
source=Path(os.environ['W8_IMAGE_DEF']);out=Path(os.environ['W8_IMAGE_OUTPUT'])
tech=pya.Technology();tech.load(c['KLAYOUT_TECH'])
opts=tech.load_layout_options
opts.lefdef_config.map_file=c['KLAYOUT_DEF_LAYER_MAP']
opts.lefdef_config.macro_resolution_mode=1
opts.lefdef_config.read_lef_with_def=False
opts.lefdef_config.lef_files=[c['TECH_LEFS']['nom_*'],*c['CELL_LEFS'],*c['MACROS']['PITCH_BANK_R1280']['lef']]
lv=pya.LayoutView();lv.set_config('background-color','#FFFFFF');lv.set_config('grid-visible','false');lv.set_config('text-visible','false')
lv.load_layout(str(source),opts,c['KLAYOUT_TECH']);lv.max_hier();lv.load_layer_props(c['KLAYOUT_PROPERTIES'])
b=lv.active_cellview().layout().top_cell().dbbox()
lv.save_image_with_options(str(out),1600,int(1600*b.height()/b.width()))
out.with_suffix('.json').write_text(json.dumps(dict(source_def=str(source),source_config=os.environ['W8_IMAGE_CONFIG'],bbox_um=[b.left,b.bottom,b.right,b.top],note='Actual DEF plus technology/standard-cell/macro LEF; source step determines route completeness.'),indent=2)+'\n')
print(out)
