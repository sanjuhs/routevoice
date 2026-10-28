# W11 Taalas end-to-end v4: PASS

Completed 2026-10-21T03:45:02.456843+05:30. **“Switch on the lights” passes bit-identically:** tokens `[28176, 373, 278, 26068, 2]`, all **18/18** frozen output hashes, **312,578,649 common clocks**, **zero clock delta**. All 27 milestone clocks and all 63 non-progress console lines match v2 exactly. Positive run took 4046.959 seconds.

## Representation and storage

All seven responder modules are additive v4 copies. Encoder/decoder UINT8 coefficient images and the position table use four-bit indices plus sixteen UINT8 representatives per 64-input × one-output group. Position groups may use fewer entries; unused entries remain charged. Frontend weights use the exact original signed INT8, FP32 scale and additive offset representation, with separate RNE multiply/add in RTL. FP32 biases and other metadata retain their bytes. Existing embedding/head and source-KV index/book services remain onboard. Dynamic attention and both live A/B bank pairs remain instantiated.

| Service | Before B | Index bits | Book B | Affine INT8 B | Metadata/bias B | After B |
|---|---:|---:|---:|---:|---:|---:|
| decoder_body | 8,908,800 | 34,406,400 | 2,150,400 | 0 | 307,200 | 6,758,400 |
| decoder_self | 2,519,040 | 9,830,400 | 614,400 | 0 | 61,440 | 1,904,640 |
| encoder_head | 1,843,200 | 7,372,800 | 460,800 | 0 | 0 | 1,382,400 |
| encoder_O | 614,400 | 2,457,600 | 153,600 | 0 | 0 | 460,800 |
| encoder_memory | 5,146,880 | 19,660,800 | 1,228,800 | 0 | 231,680 | 3,918,080 |
| frontend | 8,298,240 | 0 | 0 | 2,073,600 | 16,640 | 2,090,240 |
| positions | 1,310,720 | 5,242,880 | 327,680 | 0 | 0 | 983,040 |
| Total | 28,641,280 | 78,970,880 | 4,935,680 | 2,073,600 | 616,960 | 17,497,600 |

**Saved 11,143,680 logical payload bytes (38.91%).** Index bytes = index bits / 8. Hex text sizes are not payload sizes. Including unchanged 8,847,360 B of the five existing large onboard tables gives **26,344,960 B**; small arithmetic LUTs and mutable state are additional. No area or power reduction is inferred from these byte counts.

## Verification

- Generator roundtrip: zero mismatches across all 28,641,280 original service bytes, including retained metadata. `storage-accounting.json`, `coefficients/image-results.json`, `frontend/images.json`, `positions/manifest.json` contain grouping, per-image sizes and hashes.
- Exhaustive RTL: 565,960 encoder/decoder packets, 2,074,560 frontend packets and 163,840 position packets against original binary fixtures. Same read latencies; held replies, warm resets, identity and illegal-address cases checked. See component reports and logs.
- Full F64: fixture, positive, compare and render exit 0; all six service observers report zero host responses and zero mismatches. `comparison-result.json` and `v2-v4-comparison.json` bind actual outputs and clocks.
- All 166 original v2 direct input pins remain unchanged. `build-input-pins.json` pins v4 source/include/ROM closure; `binary-pin.json` and `tool-pins.json` bind executable/tools. `archive-receipt.json` records the verified copy of all 18 pre-existing v2 outputs. Original v1–v3 evidence is unchanged.

| Stage | Exit | Seconds |
|---|---:|---:|
| lint-full | 0 | 34.527 |
| generate-full | 0 | 74.559 |
| compile | 0 | 260.564 |
| fixture | 0 | 0.766 |
| positive | 0 | 4046.959 |
| compare | 0 | 0.039 |
| render | 0 | 0.090 |

## Reproduction and constraints

Run from the repository root. Exact argv is in `commands.json`; timestamped `logs/*.json` record command, cwd, PID, exit and elapsed time. Generate component images/RTL using their recorded commands, then:

```sh
.venv/bin/python -B overnight-20261014/finish-1023/w11-taalas-e2e/prepare_positions.py
.venv/bin/python -B overnight-20261014/finish-1023/w11-taalas-e2e/prepare_v4.py
.venv/bin/python -B overnight-20261014/finish-1023/w11-taalas-e2e/audit_inputs.py
# Run run_stage.py for lint-full, generate-full, compile, fixture.
.venv/bin/python -B overnight-20261014/finish-1023/w11-taalas-e2e/archive_reference.py
# Run run_stage.py for positive, compare, render.
.venv/bin/python -B overnight-20261014/finish-1023/w11-taalas-e2e/finalize.py
```

Runtime: `~/.local/state/routevoice-internal-runs/20261021/w11/`. A positive run refuses a nonempty `actual/`; archive it first. Local only, nice, at most six combined worker cores, 23 GiB disk guard protecting the 22 GiB floor. No git or cloud actions. `FAILURES.md` retains caveats and any failures.

## Additional clips and limits

Extra clip evidence is recorded separately in `frontend/extra-clips/`; only completed positive + compare + render receipts count. `results.json` carries its current status. The main F64 result is an integration repeat, not a new corpus tally or held-out accuracy test.

This implements functional immutable index/book lookup and exact frontend decoding. It does not establish custom access-cell geometry, synthesis feasibility of the whole recognizer, routed timing, power, real-time operation, one-die fit or sub-watt STT. In particular, the combinational frontend decoder preserves logical clock count without proving a physical cycle time.

Reading basis: repository Taalas skill, complete source notes, patent atlas, architecture/numerics and implementation references; relevant primary US20250123802A1 and US20260023566A1 description/claims; current parent `../plan.md` (root copy absent; old pause superseded by explicit 21 October resumption); every named W11 baseline file. Fixed selection identity, coefficient precision and activation precision remain distinct.
