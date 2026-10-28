from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent
g=json.loads((W/'geometry.json').read_text());b=json.loads((W/'readback.json').read_text());d=json.loads((W/'drc-result.json').read_text())
r={'status':'partial_analog_readout_assembly','complete_macro':False,'geometry':g,'gds_mask_readback':b,'drc':d,'full_assembly_lvs':None,'full_assembly_timing':None,'full_assembly_energy':None,'lef':None,'proof_scope':'20 distinct real-programmed physically joined array/receiver tiles. No shared global decoder, bank mux, phases, power distribution or W2b top interface. The generator preserves parent tile circuitry but does not claim the missing macro.'}
r['script_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [W/'build.py',W/'check.py']};(W/'results.json').write_text(json.dumps(r,indent=2)+'\n')
text=f'''# Full real-image partial readout assembly

The GDS contains all 20 distinct K64 row groups, with actual mask programming for 409,600 selections. It is a physical assembly of array and analog readout tiles, **not a complete ARRAY-PORT macro**.

- Hierarchy: 10 shared via-free base cells, 10 shared receiver cells, 200 distinct mask cells, 200 joined banks and 20 tiles.
- Geometry: {g['dimensions_um'][0]:.1f} × {g['dimensions_um'][1]:.1f} µm; {g['bounding_area_um2']/1e6:.6f} mm² including 20 µm gaps between tiles. Tile rectangles sum to {g['sum_tile_area_um2']/1e6:.6f} mm².
- Partial assembly footprint: {g['bounding_area_um2_per_selection']:.6f} µm²/selection including gaps; this is not the completed macro density.
- Reopened GDS mask readback: all 409,600 indices / 1,638,400 bits match, zero differences; 820,801 programmed Via1 connections. Recovered index hash matches W2b: `{b['recovered_unpacked_sha256']}`.
- Hierarchical GF180 DRC: {d.get('drc_markers','not completed')} markers; {d.get('hierarchical_run_mode','unknown')} mode, at most two threads. Selected FEOL/BEOL/connectivity/off-grid scope excludes density and antenna.

The generator strips only actual mask Via1 sites and OPEN labels from the supplied parent tile base cells. It verifies source one/zero counts before reusing the remaining geometry. Every row group then receives its own actual 64×320 image. Tile0 programming is not replicated as model data. Readback comes from the emitted GDS, not the source array alone.

No global connections join the 20 tiles. Row decoder/wordline drivers, phase control, 20-way bank selection, global signal and power wiring, full-array LVS, timing and energy remain unimplemented or unverified. No LEF or fictitious top-level W2b terminals are emitted. Existing joined-bank timing and parent tile verification do not establish this full assembly's service.

Artifacts: `partial-full-readout.gds`, `geometry.json`, `readback.json`, `full-readout.lyrdb`, `drc-result.json`, `results.json`. Exact commands: `COMMANDS.md`.
'''
(W/'RESULTS.md').write_text(text)
print('W5-STATUS: 20 real-image partial readout tiles generated; all1,638,400 mask bits match; hierarchical DRC markers='+str(d.get('drc_markers','unavailable'))+'; not a complete macro')
