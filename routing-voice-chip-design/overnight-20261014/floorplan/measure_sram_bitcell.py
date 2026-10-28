import klayout.db as db
import json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent;p=W/'pdk/gf180mcu_fd_ip_sram__sram512x8m8wm1.gds';l=db.Layout();l.read(str(p));cells=[]
for c in l.each_cell():
 if 'cell1' in c.name or 'strap' in c.name.lower():
  b=c.bbox();cells.append(dict(name=c.name,bbox_dbu=[b.left,b.bottom,b.right,b.top],width_um=b.width()*l.dbu,height_um=b.height()*l.dbu,area_um2=b.width()*b.height()*l.dbu**2))
r=dict(gds=str(p.relative_to(W)),source='pdks/gf180mcuD/libs.ref/gf180mcu_fd_ip_sram/gds/gf180mcu_fd_ip_sram__sram512x8m8wm1.gds',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),dbu_um=l.dbu,cells=cells,scope='MEASURED cell GDS bounding boxes;17.8um2/bit planning pitch from2-bit pair box; strap/edge/peripheral efficiency separate')
(W/'sram_bitcell_measurement.json').write_text(json.dumps(r,indent=2)+'\n');print('W3-STATUS: SRAM bit-cell GDS measurement',json.dumps(r))
