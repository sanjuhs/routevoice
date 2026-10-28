# W1b encoder on-chip services — PASS

Completed 14 October 2026. The encoder-only `rv_allonchip_top_w1b` passes the requested F64 fixture and positive stages, all 18 frozen output comparisons, and native rendering to **“Switch on the lights”**. The exact token sequence is **[28176, 373, 278, 26068, 2]**, including EOS.

**7,604,480 native bytes** are supplied by the new RTL ROM responders. The positive simulation took **3,451.004 seconds (57 minutes 31 seconds)**. It completed **312,578,649 common clocks**, including **55,302,920 encoder clocks**. Every existing conservation/numerical predicate in the retained postflight passed.

| Service | Actual RTL replies | Host replies | Mismatches |
|---|---:|---:|---:|
| Encoder QKV | 368,640 | 0 | 0 |
| Encoder O | 15,360 | 0 | 0 |
| Encoder immutable regions 4..12 | 1,947,520 | 0 | 0 |

The other workers' services remain unchanged in this wrapper. The lead must merge the independently verified wrappers and test that combined design.

## Implemented scope

Only encoder services were moved into `rv_allonchip_top_w1b`, which instantiates the existing top unchanged:

| Responder | Native ROM bytes | Unique tested transactions | First response |
|---|---:|---:|---|
| `rv_onchip_encoder_head_v1.sv` | 1,843,200 | 46,080 | PRE N+3 |
| `rv_onchip_encoder_O_v1.sv` | 614,400 | 1,920 | PRE N+3 |
| `rv_onchip_encoder_memory_v1.sv` | 5,146,880 | 160,840 | PRE N+6 |
| Total | 7,604,480 | 208,840 | |

All native bytes were compared against original binary images in `responder_test.cpp`. Independent ROM hex round trips, all-lane comparisons, response timing, held output backpressure, warm-reset held ACK fencing, illegal layer handling and POR cancellation passed. Each test prints `mismatches=0`. The integrated full recognizer also passed below. These results establish RTL service and numerical behavior; custom macro synthesis/layout/PPA is not measured here.

## Merge-facing change inventory

- `prepare.py`: extracts original encoder manifest paths; keeps source bits unchanged; reorders QKV rows into layer/role/head/row order, separates O rows, concatenates immutable regions; emits three hex images, SHA-256 manifests, wrapper, copied host and commands. Region 5 begins at original normalization packet 240. Regions 6/7 use original learned vectors 21/20. Regions 8/9/10/11 map to images 15/16/17/18. Final layer 6 region 12 uses the global learned vector. No active model inputs are modified.
- Three responders: one outstanding request each; registered response payload/identity, held valid, precise N+3/N+6 latency. No runtime ROM write ports. POR clears pending/fault. Warm reset blocks request/ACK while a pending countdown continues; only standalone held-response warm behavior is tested.
- `rv_allonchip_top_w1b.sv`: QKV/O response ports become debug outputs driven by the responders. Encoder client/backing-owner 2, regions 4..12 on the original external bus select the immutable responder; all other traffic retains original host ports. `onchip_external_*` exports the entire original shared interface; `onchip_*_fault`, `onchip_memory_idle`, `onchip_memory_rsp_valid` expose diagnostics. Frontend host service remains on the original external interface. Decoder and positions are untouched.
- `encoder_services.hpp`: removes all QKV/O response/ready/idle drivers and immutable response payload drivers. During encoder phase it only quiesces the frontend host external interface. Adds checks for each offered RTL response, complete identity, all lanes, exact first/held timing, no escaped encoder requests, and exact F64 counts. Existing request/reply/mutable state checks remain. Adds `onchip_conservation()` printing three ONCHIP lines only after all checks pass.
- `four_stage.cpp`: uses generated W1b top class, removes QKV/O initialization writes, calls `e.onchip_conservation()` at successful whole-run closure. No decoder/frontend service logic changes.
- All other copied `.hpp` files remain byte-identical to the originals, asserted by preparation. `source-provenance.json` pins original top/host/header hashes.
- `run_stage.py`: adapts W1 logging/nice/disk guard to W1b paths; six compile jobs; own F64 lock and own-binary process guard permit the user-authorized other workers' simulations. Stops its own process group if free disk falls below 22 GiB to protect the 20 GiB floor.
- `test_responders.py`, `responder_test.cpp`: independent native binary exhaustive responder tests.
- `verify_outputs.py`: extracts only the unchanged retained Q8 postflight function, redirects its artifact directory to W1b, and adds exact W1b service counts/token checks. It does not run old dispatch/admission code.
- `host-changes.patch`: exact diff of the two modified host source files for merge review.
- `run-input-pins.json`: source/header/binary hashes captured during the run and rechecked at successful postflight. The ROM input/output and original top/host/header hashes were also rechecked.
- `commands.json`, `no-pch.mk`, `rom/`, `rom-manifest.json`, `logs/`: generated reproducibility/evidence artifacts.
- `verification.json`, `result.json`, `finalize_results.py`: all 18 output hashes, original conservation results, exact moved-service counts, tokens, native stage records and final report closure.

## Commands and evidence

From repository root:

```sh
.venv/bin/python overnight-20261014/onchip-enc/prepare.py
.venv/bin/python overnight-20261014/onchip-enc/run_stage.py lint-full
.venv/bin/python overnight-20261014/onchip-enc/test_responders.py
.venv/bin/python overnight-20261014/onchip-enc/run_stage.py generate-full
.venv/bin/python overnight-20261014/onchip-enc/run_stage.py compile
.venv/bin/python overnight-20261014/onchip-enc/run_stage.py fixture
.venv/bin/python overnight-20261014/onchip-enc/run_stage.py positive
.venv/bin/python -B overnight-20261014/onchip-enc/verify_outputs.py overnight-20261014/onchip-enc/logs/20261014T011032-positive.log
.venv/bin/python -B overnight-20261014/onchip-enc/run_stage.py render
.venv/bin/python -B overnight-20261014/onchip-enc/finalize_results.py
```

Exact native command arrays are in `commands.json`; per-launch JSON logs record nice-wrapped commands, elapsed seconds and exit codes. All objects/binaries live under `/Users/sanju/.local/state/routevoice-internal-runs/20261014/onchip-enc/`.

## Executed evidence

All commands exited 0. Full-top lint/generation logs contain no warnings or errors.

| Stage | Seconds | Log |
|---|---:|---|
| lint-full | 35.428 | [20261014T010433-lint-full.log](logs/20261014T010433-lint-full.log) |
| test-head-build | 2.167 | [20261014T010600-test-head-build.log](logs/20261014T010600-test-head-build.log) |
| generate-full | 97.848 | [20261014T010601-generate-full.log](logs/20261014T010601-generate-full.log) |
| test-head | 0.989 | [20261014T010602-test-head.log](logs/20261014T010602-test-head.log) |
| test-O-build | 2.065 | [20261014T010603-test-O-build.log](logs/20261014T010603-test-O-build.log) |
| test-O | 1.098 | [20261014T010605-test-O.log](logs/20261014T010605-test-O.log) |
| test-memory-build | 2.299 | [20261014T010606-test-memory-build.log](logs/20261014T010606-test-memory-build.log) |
| test-memory | 0.781 | [20261014T010609-test-memory.log](logs/20261014T010609-test-memory.log) |
| compile | 112.713 | [20261014T010747-compile.log](logs/20261014T010747-compile.log) |
| fixture | 1.853 | [20261014T011022-fixture.log](logs/20261014T011022-fixture.log) |
| positive | 3451.004 | [20261014T011032-positive.log](logs/20261014T011032-positive.log) |
| render | 0.133 | [20261014T020810-render.log](logs/20261014T020810-render.log) |

`verification.json` records the exact file size and SHA-256 match for each of the **18/18** expected output files and the retained full-run conservation predicates. `result.json` records final PASS and every native launch. `logs/20261014T020810-render.log` records the pinned renderer/tokenizer hashes and exact text/token output.

The three exhaustive standalone tests independently read the original `.bin` files: QKV **46,080 packets / 1,843,200 bytes**; O **1,920 packets / 614,400 bytes**; immutable **160,840 packets / 5,146,880 bytes**. Combined held-response cycles: **313,260**; warm-reset held-response cases: **211**. Original binary bytes, source bits, scales, zero points and accumulator/numerical contracts were preserved.

## Limits and remaining integration work

- No requested W1b work remains unfinished. F64 success covers the requested positive path. Standalone responders additionally cover held responses, warm-reset held ACK fencing, illegal layers and POR cancellation; a full connected reset/orphan/negative suite is not newly qualified.
- These are native immutable payload ROMs with `$readmemh` initialization and no runtime weight write ports. They do not constitute a fabricated mask-ROM/shared-product access-cell implementation, a whole-chip synthesizability report, or an area/timing/power result. The existing compute datapath and dynamic state remain unchanged.
- Decoder, frontend and producer-position host services remain in this encoder-only wrapper, as required by the parallel split. Combined W1/W1b/W1c merge and rerun belong to the lead.
- No failed native stage occurred. The absent root `plan.md` remains the recorded reading gap; no substitute root file was created.

See `FAILURES.md` for the absent root `plan.md` and source-reading scope. No cloud, external SSD working directory, source commit/push, or changes to another worker's directory were used.
