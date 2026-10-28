#!/usr/bin/env python3
from render_heatmaps import render,W
from PIL import Image
names=['measured320_sram_open_macro_off_baseline_whole_44x53mm_pdn40','measured320_sram_open_macro_off_baseline_encoder_32x38mm_pdn40','measured320_sram_open_macro_off_baseline_decoder_32x38mm_pdn40_pads32']
ims=[render(n) for n in names];joined=Image.new('RGB',(2600,1470),'white');joined.paste(ims[1],(0,0));joined.paste(ims[2],(1300,0));joined.save(W/'measured_two_die_ir_heatmap.png')
# Side-by-side actual OpenROAD rendered layouts, preserving original aspect ratios.
can=Image.new('RGB',(3200,1900),'white')
for j,n in enumerate(names[1:]):
 im=Image.open(W/'runs'/n/'floorplan.png').convert('RGB');im.thumbnail((1600,1900));can.paste(im,(j*1600,0))
can.save(W/'measured_two_die_floorplan.png');print('W3-STATUS: measured one/two-die renders and terminal IR heatmaps saved')
