# Decoded tile interface and limits

`v1/decoded-tile.gds`, top `RV_K64_DECODED_TILE_00`, stores actual projection rows 0–63. It is one partial projection tile, not a complete ARRAY-PORT macro.

- `ROW0` through `ROW5` carry the six-bit row address, least significant bit first.
- `EVAL` enables the ten local row decoders. With stable address and EVAL high, each decoder asserts its corresponding local wordline. Each bank drives 128 access gates rather than a common rail across all ten banks.
- `PC` is the precharge transistor gate: low enables PMOS precharge; high disables it. PC must be high before a wordline rises. All wordlines must fall before PC goes low again. The required delays and safe transitions have not been qualified for this integrated tile.
- `OUT0` through `OUT1279` are analog receiver inverter outputs. `OUT(4*lane+bit)` corresponds to the actual four-bit index bit. They are not capture latches.
- `VDD` and `VSS` connect the analog readout and decoders through actual conductor/via paths.

The physical interface intentionally exposes ROW, EVAL and PC separately. W2b still needs a qualified phase controller, twenty-tile address selection and output mux/global wiring, and output capture. A routed ARRAY-PORT engine cannot directly substitute this tile for the missing whole array. No timing or energy from earlier ideal-source slices is assigned to this decoded tile.

The decoder is the frozen `periphery/handoff-v2` implementation. A future decoder with generated phase output requires independent pin mapping, routing and requalification; it is not present here.
