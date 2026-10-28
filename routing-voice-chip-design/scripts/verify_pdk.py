#!/usr/bin/env python3
"""Fail-closed installation inventory; this is not a foundry signoff check."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
pdk=ROOT/'pdks/gf180mcuD'
if not pdk.is_dir():raise SystemExit('GF180MCU-D is not enabled in the project PDK root')
lock=json.loads((ROOT/'tools/lock.json').read_text())
if lock['open_pdks_revision'] not in str(pdk.resolve()):raise SystemExit('Unexpected PDK revision path')
groups={
 'standard_cell_liberty':list(pdk.glob('libs.ref/gf180mcu_fd_sc_*/lib/*.lib')),
 'standard_cell_lef':list(pdk.glob('libs.ref/gf180mcu_fd_sc_*/lef/*.lef')),
 'standard_cell_gds':list(pdk.glob('libs.ref/gf180mcu_fd_sc_*/gds/*.gds')),
 'technology_lef':list(pdk.glob('libs.ref/gf180mcu_fd_sc_*/techlef/*.tlef')),
 'magic_technology':list(pdk.glob('libs.tech/magic/*.tech')),
 'netgen_setup':list(pdk.glob('libs.tech/netgen/*setup.tcl')),
 'klayout_technology':list(pdk.glob('libs.tech/klayout/tech/*.lyt')),
}
missing=[k for k,v in groups.items() if not v]
report={'status':'fail' if missing else 'pass','pdk':'gf180mcuD','revision':lock['open_pdks_revision'],'missing':missing,'groups':{}}
for kind,paths in groups.items():
 entries=[]
 for p in sorted(paths):
  entries.append({'file':str(p.relative_to(pdk)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 report['groups'][kind]=entries
report['proof_boundary']='Pinned prepared PDK installed; no source rebuild, DRC/LVS result or silicon qualification implied.'
(ROOT/'reports/pdk-installation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'files':sum(map(len,groups.values())),'missing':missing}))
raise SystemExit(bool(missing))
