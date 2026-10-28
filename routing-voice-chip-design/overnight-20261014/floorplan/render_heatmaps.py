#!/usr/bin/env python3
"""Spatial per-macro terminal voltage heatmaps from OpenROAD's voltage CSVs."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,json
W=Path(__file__).resolve().parent
fontpath='/System/Library/Fonts/Supplemental/Arial.ttf'
def font(n):
 try:return ImageFont.truetype(fontpath,n)
 except OSError:return ImageFont.load_default()
def values(p):
 out={}
 for net in ['VDD','VSS']:
  with (p/f'{net}_voltage.rpt').open() as f:
   for r in csv.DictReader(f):
    name=r['Instance'];v=float(r['Voltage']);d=out.setdefault(name,{})
    d[net]=(min(d.get(net,v),v) if net=='VDD' else max(d.get(net,v),v))
 return {n:3.3-d['VDD']+d['VSS'] for n,d in out.items() if len(d)==2}
def color(v):
 f=max(0,min(1,v/.165));return (int(255-60*f),int(245-210*f),int(210-165*f))
def render(run):
 p=W/'runs'/run;m=json.loads((p/'manifest.json').read_text());v=values(p)
 im=Image.new('RGB',(1300,1470),'white');d=ImageDraw.Draw(im);dw=m.get('die_width_mm',m['die_mm']);dh=m.get('die_height_mm',m['die_mm']);s=1120/(max(dw,dh)*1000);x0=90+(1120-dw*1000*s)/2;y0=180
 height_px=dh*1000*s;width_px=dw*1000*s
 label=({'whole':'One die','encoder':'Two-die A','decoder':'Two-die B'}[m['partition']] if m['scenario'].startswith(('measured','pitch','final')) else m['partition'].title())
 d.text((60,35),f"{label} | {dw:g} x {dh:g} mm",fill='#142638',font=font(32))
 d.text((60,85),'Abstract macro terminal supply loss: (3.3 V - VDD) + VSS',fill='#26394b',font=font(22))
 d.text((60,120),'Assumed loads; screening RC. No macro-internal or package drop.',fill='#536477',font=font(19))
 d.rectangle((x0,y0,x0+width_px,y0+height_px),fill='#e8ecf0',outline='#26394b',width=3)
 for pad in m['pads']:
  w,h=(75,350) if pad['orientation'] in ('R0','R180') else (350,75)
  x=x0+pad['x']*s;y=y0+height_px-(pad['y']+h)*s
  d.rectangle((x,y,x+w*s,y+h*s),fill='#33465b')
 records=[]
 for t in m['tiles']:
  drop=v.get(t['name']);x=x0+t['x']*s;y=y0+height_px-(t['y']+t['h'])*s
  d.rectangle((x,y,x+t['w']*s,y+t['h']*s),fill=color(drop) if drop is not None else '#b6bfca',outline='white',width=1)
  label=t['block'].replace('codebooks_and_other_metadata','books/meta').replace('encoder_fabric_','enc ').replace('decoder_fabric_','dec ').replace('embedding_head_tied_once','tied table').replace('producer_mutable_regions0_1_2','producer RAM').replace('encoder_owner2_region0_1_2','encoder RAM').replace('compact_committed_shadow_history','history')
  while d.textbbox((0,0),label,font=font(11))[2]>t['w']*s-8 and len(label)>2:label=label[:-2]+'…'
  d.text((x+4,y+6),label,fill='#272727',font=font(11))
  if drop is not None:d.text((x+4,y+22),f'{drop*1000:.1f} mV',fill='#272727',font=font(13))
  records.append(dict(instance=t['name'],combined_terminal_drop_v=drop))
 for i in range(900):d.line((180+i,1340,180+i,1360),fill=color(.165*i/899))
 for i,label in [(0,'0'),(1,'33'),(2,'66'),(3,'99'),(4,'132'),(5,'165 mV (5%)')]:d.text((180+i*180-10,1370),label,fill='#26394b',font=font(16))
 d.text((60,1420),'White boundaries: abstract macros. Dark perimeter: signal and supply pads. Fillers omitted.',fill='#536477',font=font(17))
 im.save(p/'ir_heatmap.png');(p/'macro_terminal_drops.json').write_text(json.dumps(records,indent=2))
 return im
if __name__=='__main__':
 names=['custom7_sram_open_macro_off_baseline_whole_34mm','custom7_sram_open_macro_off_baseline_encoder_25mm','custom7_sram_open_macro_off_baseline_decoder_25mm']
 ims=[render(n) for n in names];joined=Image.new('RGB',(2600,1470),'white');joined.paste(ims[1],(0,0));joined.paste(ims[2],(1300,0));joined.save(W/'two_die_ir_heatmap.png')
 print('W3-STATUS: IR heatmaps rendered from OpenROAD voltage reports')
