#!/usr/bin/env python3
"""Read an existing physical checkpoint and retain exact instance geometry."""
import os
os.environ['OMP_NUM_THREADS'] = '1'
if hasattr(os, 'sched_getaffinity'):
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
import argparse, hashlib, json
from pathlib import Path
import odb

p = argparse.ArgumentParser()
p.add_argument('--state', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
out = Path(a.output)
assert not out.exists(), 'Preserve previous audit'
state = Path(a.state)
source = Path(json.loads(state.read_text())['odb'])
db = odb.dbDatabase.create()
odb.read_db(db, str(source))
b = db.getChip().getBlock()
u = b.getDbUnitsPerMicron()
masters = {}
for inst in b.getInsts():
    m = inst.getMaster()
    name = m.getName()
    if name not in masters:
        masters[name] = dict(count=0, type=str(m.getType()),
                             width_um=m.getWidth()/u, height_um=m.getHeight()/u,
                             area_um2=m.getWidth()*m.getHeight()/u**2)
    masters[name]['count'] += 1
groups = {}
for name, m in masters.items():
    group = ('macro' if m['type'] == 'BLOCK' else
             'tap' if 'WELLTAP' in m['type'] or name.endswith('__filltie') else
             'endcap' if 'ENDCAP' in m['type'] or name.endswith('__endcap') else
             'filler' if m['type'] == 'CORE_SPACER' else 'logic_and_clock')
    g = groups.setdefault(group, dict(count=0, area_um2=0.0))
    g['count'] += m['count']
    g['area_um2'] += m['count'] * m['area_um2']
die = b.getDieArea()
h = hashlib.sha256()
with source.open('rb') as f:
    for chunk in iter(lambda: f.read(1024**2), b''):
        h.update(chunk)
r = dict(scope='Exact saved OpenDB instance geometry; routing/signoff status must be established separately',
         state=str(state), source_odb=str(source), source_odb_sha256=h.hexdigest(),
         die_um=[die.xMin()/u, die.yMin()/u, die.xMax()/u, die.yMax()/u],
         die_area_mm2=die.dx()*die.dy()/u**2/1e6,
         groups=groups, masters=masters,
         instance_count=sum(x['count'] for x in groups.values()),
         total_instance_area_mm2=sum(x['area_um2'] for x in groups.values())/1e6)
out.write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k != 'masters'}, indent=2))
