"""Render measured macro/PDN geometry, not routed signal nets."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
W=Path(__file__).resolve().parent;r=json.loads((W/'odb-inspection.json').read_text())
colors={'VDD':'#b74a43','VSS':'#2c65a5'}
fig,(ax,detail)=plt.subplots(1,2,figsize=(12,7),gridspec_kw={'width_ratios':[1.5,1]})
die=r['die_bbox_um'];mb=r['macro']['bbox_um']
def rect(axis,b,**kw):axis.add_patch(Rectangle((b[0],b[1]),b[2]-b[0],b[3]-b[1],**kw))
rect(ax,die,fill=False,edgecolor='#333',linewidth=1)
rect(ax,mb,facecolor='#eef0ed',edgecolor='#222',linewidth=1.2)
for n in ['VDD','VSS']:
 for b in r['power_nets'][n]['global_M5_rectangles']:rect(ax,b,facecolor=colors[n],edgecolor='none',alpha=.65)
 for pg in r['macro']['selected_pins'][n]['geometry']:
  if pg['layer']=='Metal4':
   x=(pg['rect_um'][0]+pg['rect_um'][2])/2
   ax.plot([x,x],pg['rect_um'][1::2],color=colors[n],linewidth=.8)
ax.text(1002,2400,'PITCH_BANK_R1280\n1004 × 2258.85 µm\n(500, 1200) µm',ha='center',va='center',fontsize=10,bbox={'facecolor':'white','alpha':.92,'edgecolor':'none'})
ax.set(xlim=(-80,4580),ylim=(-80,4580),xlabel='x (µm)',ylabel='y (µm)',title='4500 × 4500 µm die; actual Metal5 PDN')
ax.set_aspect('equal')
# Actual lowest VDD and VSS contacts, shown together. No fabricated pin escape.
y0=min(x['via_origin_um'][1] for x in r['power_nets']['VDD']['macro_pin_intersections'])
for n in ['VDD','VSS']:
 for pg in r['macro']['selected_pins'][n]['geometry']:
  if pg['layer']=='Metal4':rect(detail,pg['rect_um'],facecolor=colors[n],edgecolor='none',alpha=.3)
 for b in r['power_nets'][n]['global_M5_rectangles']:rect(detail,b,facecolor=colors[n],edgecolor='none',alpha=.3)
 for via in r['power_nets'][n]['macro_pin_intersections']:
  if y0-2<via['via_origin_um'][1]<y0+7:
   rect(detail,via['via_bbox_um'],fill=False,edgecolor=colors[n],linewidth=1.4)
   detail.annotate(n+' Via4',xy=via['via_origin_um'],xytext=(505,via['via_origin_um'][1]),color=colors[n],fontsize=10,va='center',arrowprops={'arrowstyle':'-','color':colors[n]})
detail.set(xlim=(499,511),ylim=(y0-2,y0+7),xlabel='x (µm)',ylabel='y (µm)',title='Actual PG vias overlap exported M4 spines')
detail.set_aspect('equal')
fig.suptitle('W8 complete-v3 — saved PDN-stage ODB\nBefore signal routing; no routed timing, DRC/LVS or IR/EM claim',fontsize=13)
fig.text(.5,.02,'16 same-net PDN-via intersections per macro supply; OpenROAD grid checks report all VDD/VSS shapes connected.',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.04,1,.91]);fig.savefig(W/'macro-pdn-evidence.png',dpi=180);plt.close(fig)
print('Rendered measured PDN geometry preview')
