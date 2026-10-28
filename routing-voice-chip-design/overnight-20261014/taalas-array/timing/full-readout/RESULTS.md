# Full real-image partial readout assembly

The GDS contains all 20 distinct K64 row groups, with actual mask programming for 409,600 selections. It is a physical assembly of array and analog readout tiles, **not a complete ARRAY-PORT macro**.

- Hierarchy: 10 shared via-free base cells, 10 shared receiver cells, 200 distinct mask cells, 200 joined banks and 20 tiles.
- Geometry: 4669.7 × 4780.0 µm; 22.321166 mm² including 20 µm gaps between tiles. Tile rectangles sum to 20.546680 mm².
- Partial assembly footprint: 54.495034 µm²/selection including gaps; this is not the completed macro density.
- Reopened GDS mask readback: all 409,600 indices / 1,638,400 bits match, zero differences; 820,801 programmed Via1 connections. Recovered index hash matches W2b: `ba628b676d59721c268868d6720be1f58a4f8d4edfd9a26009403c9a8c4fce8e`.
- Hierarchical GF180 DRC: 0 markers; deep mode, at most two threads. Selected FEOL/BEOL/connectivity/off-grid scope excludes density and antenna.

The generator strips only actual mask Via1 sites and OPEN labels from the supplied parent tile base cells. It verifies source one/zero counts before reusing the remaining geometry. Every row group then receives its own actual 64×320 image. Tile0 programming is not replicated as model data. Readback comes from the emitted GDS, not the source array alone.

No global connections join the 20 tiles. Row decoder/wordline drivers, phase control, 20-way bank selection, global signal and power wiring, full-array LVS, timing and energy remain unimplemented or unverified. No LEF or fictitious top-level W2b terminals are emitted. Existing joined-bank timing and parent tile verification do not establish this full assembly's service.

Artifacts: `partial-full-readout.gds`, `geometry.json`, `readback.json`, `full-readout.lyrdb`, `drc-result.json`, `results.json`. Exact commands: `COMMANDS.md`.
