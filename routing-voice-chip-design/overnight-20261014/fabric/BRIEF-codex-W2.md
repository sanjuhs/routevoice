# Codex brief W2 — measure the fixed-weight fabric in GF180 (overnight, 14 Oct 2026)

You are a worker on the RouteVoice 180 nm speech-recognition chip. The lead (Claude) will re-run and check everything you produce, so report honestly: if something fails, say so and show the log. Do NOT fabricate numbers.

## Where things are
- Repo: `/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design`
- Your workspace (write ONLY here): `overnight-20261014/fabric/`
- Python with numpy: `routing-voice-chip-design/.venv/bin/python`
- Tools on PATH: verilator, iverilog, yosys (Homebrew). LibreLane 3.0.11 + OpenROAD + Magic + KLayout + Netgen via Nix: see `scripts/run_physical.sh` (it runs `nix-shell tools/librelane/shell.nix --run 'librelane --pdk gf180mcuD --pdk-root pdks <config.json>'`). An earlier working config is `physical/die1-serial.json`. PDK is in `pdks/` (gf180mcuD).
- Real model weights (UINT8, layout W[k][n] = image[k*320+n]): `~/.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3/cross/coefficients.bin` = 12 images of 320×320 bytes. Use image 0 (first 102,400 bytes).
- Verified fact: for every output n and every group of 64 consecutive inputs k (g = k/64, 5 groups), the 64 values W[g*64..g*64+63][n] contain exactly 16 distinct UINT8 values. So each weight is exactly a 4-bit index into a 16-entry book (book per (g,n), 8-bit entries).

## What to build

A fixed-weight 320×320 projection engine, Taalas-style: weights are frozen into the hardware, the only runtime input is activations.

Function: for an input vector of 320 signed 9-bit activations x[k], compute for each of 320 outputs
`y[n] = sum_k x[k] * W[k][n]` (W unsigned 8-bit), exact, signed 27-bit accumulators. Also output `asum = sum_k x[k]` (needed for the weight-zero-point correction done downstream).

Micro-architecture (time-multiplexed over k, all 320 output lanes in parallel):
1. One activation x[k] per cycle is broadcast (k = 0..319, 320 cycles per vector, plus pipeline latency).
2. Shared product generator: P[d] = x * d for d = 0..15 (16 shared products, shift/add, signed 13-bit). These 16 products are shared by all 320 lanes — this is the shared-product idea.
3. Fixed selection: for row k, each lane n needs its 4-bit index idx[k][n] and its book entry v = book[k/64][n][idx]. Resolve hi = v>>4, lo = v&15, product = (P[hi] << 4) + P[lo]. acc[n] += product.
4. Handshake: `start` pulse, `x_valid/x_ready` stream for the 320 activations, `done` pulse, then outputs readable (a flat output bus or a 320-entry read port with an address — your choice, keep IO pins reasonable: use an output read port `rd_addr[8:0]`/`rd_data[26:0]`, since a real chip cannot have 8,640 output pins).

Write a Python generator `gen_fabric.py` that reads the real weights, builds idx and books, ASSERTS that book[g][n][idx[k][n]] == W[k][n] for every k,n, and emits SystemVerilog.

Build two variants from the same generator:
- **V1 `rv_fixed_proj320_rom`**: index array and books are constants inside the RTL (synthesized `case`/constant tables → standard-cell ROM logic). This is the honest "all weights on-chip in standard cells" number.
- **V2 `rv_fixed_proj320_dp`**: same engine but the 320×4-bit index row and the books for the current group come in through ports from a separate array (to be the custom one-transistor cell array later). This measures datapath + shared products + control per lane.
If V1 at 320×320 is too big to finish place-and-route in about 2 hours on this Mac, ALSO produce a V1 slice of 64 rows × 320 outputs (`rv_fixed_proj64x320_rom`, one book group) and report per-weight numbers from it — and tell the lead so the full V1 can go to a bigger cloud machine.

## Verification (must pass before physical)
- Testbench (Verilator or Icarus, your choice) that runs at least: 20 random activation vectors including extremes (-256, 255, all zeros, alternating), and checks all 320 outputs + asum exactly against a numpy reference computed directly from the original W bytes (not from your own idx/book). Report pass/fail counts.
- Dump a VCD (or SAIF) from a run of ~5 random vectors for power analysis.

## Physical (GF180, LibreLane, gf180mcuD)
For V2 (320×320) and V1 (full, or the 64-row slice):
- Run the full LibreLane flow: synthesis, floorplan, power distribution network (PDN — keep the default power grid, it must be present and connected), placement, CTS, global+detailed routing, fill, Magic+KLayout DRC, Netgen LVS, multi-corner STA, antenna. Start with CLOCK_PERIOD 20 (50 MHz); if timing is met with slack, note the achievable frequency from STA (1/(period - worst slack)).
- Pick FP_CORE_UTIL / density so it routes (start ~40–50%).
- Power: report OpenROAD/OpenSTA power at the typical corner; if you can annotate switching activity from your VCD (`read_vcd` or SAIF) do it and report both default-activity and annotated numbers, clearly labelled.
- Use `nice` and at most 8 threads so the Mac stays usable for other jobs. Check `df -h /` first: never let free space drop below 20 GiB.

## Deliverables (in `overnight-20261014/fabric/`)
- `gen_fabric.py`, generated RTL, testbench, LibreLane configs, run directories (LibreLane `runs/` can stay in place).
- `RESULTS.md` and `results.json` with, per variant: verification pass counts; synthesized cell count and cell area; die/core area; utilization; worst setup/hold slack at each corner and achieved MHz; DRC/LVS/antenna counts; power (mW) with the corner and activity source; and derived **mm² per weight, µm² per weight, mW per weight at the achieved clock, and cycles + µs per 320×320 matvec**. Include the exact commands used.
- A PNG render of the final layout (KLayout batch mode can save an image; LibreLane may produce one too).

## Rules
- Do not touch files outside `overnight-20261014/fabric/` except reading. Do not git commit/push (the lead does that). No cloud, no RunPod.
- Keep going autonomously until deliverables are done; prefer a smaller verified result over a bigger unverified one.
- Print a short status line `W2-STATUS: <what just finished>` after each major step so the lead can follow the log.
