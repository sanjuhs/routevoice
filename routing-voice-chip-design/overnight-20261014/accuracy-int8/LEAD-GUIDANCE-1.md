# Lead guidance 1 for W7: test the lossless native-INT8 storage

Your result is valuable and honest: re-quantized symmetric INT8 fails the gates. Keep it.

You also noted that **the source model already stores the three frontend weight tensors as INT8 codes with FP32 multiplicative scales and additive offsets**; the chip ROM holds their expanded FP32 values. Test the lossless option:

1. From the K64 candidate's frontend model, extract the native INT8 codes plus their exact scales/offsets (and axes, e.g. Conv2 along input channels), exactly as the graph's dequantization uses them.
2. Reconstruct FP32 values the way the graph computes them: the same operator, formula and FP32 rounding order, e.g. `(code - zero_point) * scale` or `code * scale + offset`, whichever the graph does, evaluated in float32. Compare **byte for byte** against the chip's FP32 ROM images (`~/.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3/frontend/shared/*.bin` and the ROM hex used by the on-chip design in `overnight-20261014/onchip-front/` or `onchip-all/`). Report mismatch counts per tensor. If any mismatch exists, report max ULP difference and which formula/order you tried.
3. If bit-exact: storage = INT8 codes (2,073,600 B) + scales/offsets (+ FP32 biases 3,840 B). Report the exact byte total. Describe the minimal dequant datapath the frontend would need: one FP32 multiply-add per coefficient fetch, or a fixed per-channel scale. The chip's numerics are then UNCHANGED, so no WER run is needed. Still run the K64 validation once with a model whose frontend constants are rebuilt from the codes, if quick, to demonstrate identical transcripts.
4. Update `RESULTS.md` / `results.json` with a section **"Lossless native INT8 storage"**. Print `W7-STATUS:` lines. Finish by ≈06:30 IST.
