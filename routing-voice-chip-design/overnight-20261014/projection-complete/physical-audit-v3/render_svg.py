from pathlib import Path
import json
W=Path(__file__).resolve().parent;r=json.loads((W/'odb-inspection.json').read_text());c={'VDD':'#b54e42','VSS':'#356ba0'}
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1400" viewBox="0 0 1400 1400">','<rect width="1400" height="1400" fill="white"/>','<style>text {font-family:Arial,sans-serif;fill:#222} .title {font-size:28px} .sub {font-size:18px}</style>']
def text(x,y,t,size=18,anchor='start',color='#222'):s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{t}</text>')
def panel(name,x,y,w,h,limits):
 x0,y0,x1,y1=limits;sx=w/(x1-x0);sy=h/(y1-y0)
 s.append(f'<defs><clipPath id="{name}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>')
 def rec(b,fill,stroke='none',opacity=1):
  a,d,e,f=b
  a=max(a,x0);d=max(d,y0);e=min(e,x1);f=min(f,y1)
  if e<=a or f<=d:return
  s.append(f'<rect clip-path="url(#{name})" x="{x+(a-x0)*sx:.3f}" y="{y+h-(f-y0)*sy:.3f}" width="{(e-a)*sx:.3f}" height="{(f-d)*sy:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="1" opacity="{opacity}"/>')
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#444"/>')
 return rec
text(60,46,'W8 complete-v3: macro placement and PDN evidence',28)
text(60,79,'Saved PDN-stage OpenDB • before signal routing • no DRC/LVS, timing or IR/EM closure claim',17)
whole=panel('whole',65,142,665,665,[0,0,4500,4500]);whole(r['macro']['bbox_um'],'#e9ede8','#222')
for n in ['VDD','VSS']:
 for b in r['power_nets'][n]['global_M5_rectangles']:whole(b,c[n],opacity=.7)
 for pg in r['macro']['selected_pins'][n]['geometry']:
  if pg['layer']=='Metal4':whole(pg['rect_um'],c[n],c[n])
text(65,124,'4500 × 4500 µm die; actual Metal5 power straps',19)
text(216,455,'PITCH_BANK_R1280',17,anchor='middle');text(216,480,'1004 × 2258.85 µm',16,anchor='middle');text(216,505,'origin (500, 1200) µm',15,anchor='middle')
text(65,831,'0',14);text(730,831,'4500 µm',14,anchor='end')
y=min(v['via_origin_um'][1] for v in r['power_nets']['VDD']['macro_pin_intersections'])
zoom=panel('zoom',805,210,495,445,[499,y-2,510,y+7])
for n in ['VDD','VSS']:
 for b in r['power_nets'][n]['global_M5_rectangles']:zoom(b,c[n],opacity=.25)
 for pg in r['macro']['selected_pins'][n]['geometry']:
  if pg['layer']=='Metal4':zoom(pg['rect_um'],c[n],opacity=.5)
 for v in r['power_nets'][n]['macro_pin_intersections']:zoom(v['via_bbox_um'],'none',c[n])
text(805,168,'Actual M4 spine / PDN-via overlap',19)
text(805,192,'Lowest adjacent VDD and VSS contacts',16)
text(805,686,'x = 499–510 µm; y = 1255.77–1264.77 µm',15)
text(825,310,'VSS at x = 501 µm',16,color=c['VSS']);text(1005,578,'VDD at x = 503 µm',16,color=c['VDD'])
text(805,732,'16 same-net PDN-via contacts per supply',19)
text(805,764,'Grid checker: all VDD / VSS shapes connected',16)
text(805,795,'Macro ports bind to the expected power nets.',16)
text(60,864,'Source: 17-openroad-generatepdn ODB; 2000 database units/µm. Other cells and signal routes are not drawn.',14)
s.append('</svg>');(W/'macro-pdn-evidence.svg').write_text('\n'.join(s)+'\n')
