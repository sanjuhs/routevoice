import odb,sys,json
from collections import defaultdict
p=sys.argv[1];db=odb.dbDatabase.create();odb.read_db(db,p);b=db.getChip().getBlock();scale=b.getDbUnitsPerMicron()
rects=[]
for n in b.getNets():
 if n.getName() not in ('VDD','VSS'):continue
 for sw in n.getSWires():
  for s in sw.getWires():
   if s.isVia():
    dx,dy=s.getViaXY();via=s.getBlockVia() or s.getTechVia()
    for r in via.getBoxes():
     layer=r.getTechLayer()
     if layer.getType()=='ROUTING':rects.append((n.getName(),layer.getName(),r.xMin()+dx,r.yMin()+dy,r.xMax()+dx,r.yMax()+dy,'via_enclosure'))
   else:
    r=s;rects.append((n.getName(),s.getTechLayer().getName(),r.xMin(),r.yMin(),r.xMax(),r.yMax(),'wire'))
 for it in n.getITerms():
  inst=it.getInst()
  if not inst.getMaster().getName().startswith('M_'):continue
  dx,dy=inst.getLocation()
  for pin in it.getMTerm().getMPins():
   for s in pin.getGeometry():
    r=s;rects.append((n.getName(),s.getTechLayer().getName(),r.xMin()+dx,r.yMin()+dy,r.xMax()+dx,r.yMax()+dy,inst.getName()))
bins=defaultdict(list);errors=[];seen=set();step=int(500*scale)
for i,a in enumerate(rects):
 for x in range(a[2]//step,a[4]//step+1):
  for y in range(a[3]//step,a[5]//step+1):
   key=(a[1],x,y,a[0]);other=(a[1],x,y,'VSS' if a[0]=='VDD' else 'VDD')
   for j in bins[other]:
    c=rects[j]
    if a[0]!=c[0] and min(a[4],c[4])>max(a[2],c[2]) and min(a[5],c[5])>max(a[3],c[3]) and (j,i) not in seen:
     errors.append((a,c));seen.add((j,i))
   bins[key].append(i)
res=dict(scope='Positive-area VDD/VSS metal rectangle overlaps, special wires + macro pins; via enclosures included; IO internals excluded',rectangles=len(rects),short_count=len(errors),examples=errors[:20])
open(p+'.shorts.json','w').write(json.dumps(res,indent=2));print(json.dumps(res)[:3000])
