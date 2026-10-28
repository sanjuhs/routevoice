"""Read-only ODB inspection. Never writes database or mutates design."""
import os
os.environ['OMP_NUM_THREADS']='1'
# Affinity restriction guarantees this audit uses at most one remote CPU.
if hasattr(os,'sched_getaffinity'):
 allowed=os.sched_getaffinity(0);os.sched_setaffinity(0,{min(allowed)})
import odb,json,hashlib
from pathlib import Path
W=Path('/workspace/rv/overnight-20261014/projection-complete/physical-audit-v3')
P=W.parent/'runs/complete-v3/17-openroad-generatepdn/rv_k64_projection_complete.odb'
db=odb.dbDatabase.create();odb.read_db(db,str(P));b=db.getChip().getBlock();u=b.getDbUnitsPerMicron();inst=b.findInst('bank')
assert inst is not None
print('AUDIT_API',json.dumps({'dbSBox':[x for x in dir(odb.dbSBox) if any(s in x for s in ['Via','Box','Tech','Layer'])],'dbVia':[x for x in dir(odb.dbVia) if 'Box' in x or 'Layer' in x],'orient':str(inst.getOrient()),'location':inst.getLocation()},default=str),flush=True)
def box(v):return [v.xMin()/u,v.yMin()/u,v.xMax()/u,v.yMax()/u]
loc=inst.getLocation();assert str(inst.getOrient()) in ['R0','N']
pins={}
for it in inst.getITerms():
 n=it.getMTerm().getName();net=it.getNet()
 if n not in ['VDD','VSS','PC','WL0','WL1279','OUT0','OUT1279']:continue
 geo=[]
 for mp in it.getMTerm().getMPins():
  for g in mp.getGeometry():
   if g.getTechLayer() is None:continue
   bb=box(g);geo.append({'layer':g.getTechLayer().getName(),'rect_um':[bb[0]+loc[0]/u,bb[1]+loc[1]/u,bb[2]+loc[0]/u,bb[3]+loc[1]/u]})
 pins[n]={'net':net.getName() if net else None,'sig_type':str(it.getMTerm().getSigType()),'geometry':geo}
def overlap(a,b):return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
masters={}
for item in b.getInsts():
 master=item.getMaster();name=master.getName()
 if name not in masters:masters[name]={'instances':0,'width_um':master.getWidth()/u,'height_um':master.getHeight()/u,'type':str(master.getType()),'area_um2_per_instance':master.getWidth()*master.getHeight()/u/u}
 masters[name]['instances']+=1
areas={'macro':{'count':0,'area_um2':0.0},'tap':{'count':0,'area_um2':0.0},'endcap':{'count':0,'area_um2':0.0},'other_standard_cells':{'count':0,'area_um2':0.0}}
for name,m in masters.items():
 typ=m['type']
 category='macro' if name=='PITCH_BANK_R1280' else ('tap' if 'WELLTAP' in typ or name.endswith('__filltie') else ('endcap' if 'ENDCAP' in typ or name.endswith('__endcap') else 'other_standard_cells'))
 areas[category]['count']+=m['instances'];areas[category]['area_um2']+=m['instances']*m['area_um2_per_instance']
(W/'physical-area.json').write_text(json.dumps({'source':'Exact ODB master width times height, multiplied by actual instance occurrences','units_per_um':u,'breakdown':areas,'all_instances':sum(z['count'] for z in areas.values()),'all_instance_area_um2':sum(z['area_um2'] for z in areas.values()),'masters':masters},indent=2)+'\n')
net_stats={}
for n in ['VDD','VSS']:
 net=b.findNet(n);assert net is not None
 counters={'special_wire_count':len(net.getSWires()),'rectangles_by_layer':{},'via_count':0,'macro_pin_intersections':[],'global_M5_rectangles':[]}
 for sw in net.getSWires():
  for sh in sw.getWires():
   if sh.isVia():
    counters['via_count']+=1
    if any(overlap(box(sh),pg['rect_um']) for pg in pins[n]['geometry']):
     via=sh.getTechVia() or sh.getBlockVia()
     if via is None:raise RuntimeError('Via has no definition')
     vx,vy=sh.getViaXY()
     hit=[]
     for vg in via.getBoxes():
      if vg.getTechLayer() is None:continue
      rr=box(vg);rr=[rr[0]+vx/u,rr[1]+vy/u,rr[2]+vx/u,rr[3]+vy/u]
      layer=vg.getTechLayer().getName()
      for pg in pins[n]['geometry']:
       if layer==pg['layer'] and overlap(rr,pg['rect_um']):hit.append({'layer':layer,'via_metal_rect_um':rr,'macro_pin_rect_um':pg['rect_um']})
     if hit:counters['macro_pin_intersections'].append({'via_name':via.getName(),'via_origin_um':[vx/u,vy/u],'via_bbox_um':box(sh),'same_net':n,'intersections':hit})
   else:
    layer=sh.getTechLayer();lname=layer.getName() if layer else '?';counters['rectangles_by_layer'][lname]=counters['rectangles_by_layer'].get(lname,0)+1
    if lname=='Metal5':counters['global_M5_rectangles'].append(box(sh))
 net_stats[n]=counters
r={'stage':'17-openroad-generatepdn, before placement/CTS/signal routing','source_odb':str(P),'source_odb_bytes':P.stat().st_size,'database_units_per_um':u,'die_bbox_um':box(b.getDieArea()),'macro':{'instance':inst.getName(),'master':inst.getMaster().getName(),'placement_status':str(inst.getPlacementStatus()),'orientation':str(inst.getOrient()),'location_um':[loc[0]/u,loc[1]/u],'bbox_um':box(inst.getBBox()),'iterm_count':len(inst.getITerms()),'selected_pins':pins},'power_nets':net_stats,'scope':'Logical PG connectivity and actual same-net PDN-via metal intersection at macro power pins. No routing completion, LVS or IR/EM inference.'}
h=hashlib.sha256()
with P.open('rb') as stream:
 for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
r['source_odb_sha256']=h.hexdigest()
r['source_odb_mtime_ns']=P.stat().st_mtime_ns
r['cpu_affinity'] = sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None
(W/'odb-inspection.json').write_text(json.dumps(r,indent=2)+'\n');print('AUDIT_COMPLETE',flush=True)
