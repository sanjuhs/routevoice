# W1c frontend and positions — PASS

Implemented `rv_allonchip_top_w1c`, instantiating the retained recognizer top unchanged. Only frontend immutable scalar regions 0,1,4,5,8 (8,298,240 native FP32 bytes) and fixed producer positions (1,310,720 native bytes) are moved into RTL ROMs. Total: **9,608,960 bytes**. These are functional RTL ROMs; no physical area, timing, power, or whole-chip feasibility claim is made.

**Measured result:** F64 fixture and positive passed. All **18** actual output files match the retained native binding byte-for-byte by size and SHA-256. Tokens are `[28176, 373, 278, 26068, 2]`, including EOS; rendered text is **Switch on the lights**. Positive simulation elapsed **3308.270 seconds** (55.14 minutes).

```
ONCHIP service=frontend_immutable rtl_replies=55720960 host_replies=0 mismatches=0
ONCHIP service=producer_positions rtl_replies=2560 host_replies=0 mismatches=0
```

The frontend isolated test checked all 2,074,560 native FP32 words, 1,521 held cycles, 1,521 warm-reset cycles, five invalid addresses and an immutable-write rejection. Retained position four-state controls passed 6 legal requests, 11 invalid/X/Z offers and 18 held cycles. Full-top lint/generation/compile passed; lint reported only 164 TIMESCALEMOD warnings. No additional full-chain fault suite, F144 run or new speech corpus was executed. Functional RTL closure of these two services does not establish fabricated ROM density or whole-chip physical closure.

The lead explicitly clarified that the one-long-simulation limit applies per worker and authorized concurrent W1/W1b/W1c runs. This worker ran one positive simulation with `nice -n 10`; compile commands use at most six jobs and the launcher protects the 20 GiB disk floor with a 22 GiB reserve.

All W1c source/report changes are within this directory. Objects, binaries, active ROM images, temporary files and numerical outputs are under `/Users/sanju/.local/state/routevoice-internal-runs/20261014/onchip-front/`. No cloud, commits, pushes, or edits to W1/W1b folders.

## Source and host changes

- `prepare_w1c.py`: reproducible exact little-endian hex conversion, binary/hex SHA-256 manifests, wrapper generation, service-specific host copying/patching, and full commands.
- `rv_onchip_frontend_v1.sv`: 32-bit FP32 ROMs without runtime writes, legal-region/bounds checks, one held response at PRE N+1, complete captured metadata, zero scalar padding, warm-reset retention and POR clear.
- `rv_source_position_immutable_rom_v1.sv`: byte-identical copy of the retained responder. 163,840 × 64-bit image, N+3 held response, generation-zero/address checks, warm-reset countdown retention and asynchronous POR.
- `rv_allonchip_top_w1c.sv`: position service inputs become debug outputs; frontend client-0 immutable requests are intercepted on the shared external interface, with effective service buses exported as `w1c_external_*`. All other services retain their original host interfaces.
- `frontend_services.hpp`: stops driving immutable responses, quiesces the host external provider while frontend runs, and checks every RTL response's exact timing, identity, metadata, padding and native FP32 bits against the original mirror. Original counts/assertions remain.
- `taalas_adapter_session_compact_token_services_f500_v1.hpp`: removes position drivers only; checks every offered position response against the original queue and binary, including N+3 timing and held identity/data. Original counters retire actual RTL replies.
- `four_stage.cpp`: changes generated top class, removes position initialization assignments, adds exact expected coverage and final ONCHIP lines for W1c's two services.
- `producer_services.hpp`, `encoder_services.hpp`, `taalas_decoder_token_compact_services.hpp`, `learned_observer.hpp`, `greedy_observer.hpp`: byte-identical original copies. Decoder and encoder services are unchanged.
- `run_stage.py`, `no-pch.mk`, `commands.json`: niced stages, at most six compile jobs, disk guard, positive process check, fresh numerical output protection, unique log/command/time records.
- `responder_test.cpp`, `tb_source_position_immutable_rom_v1.sv`: exhaustive frontend binary oracle and retained position four-state tests.
- `compare_outputs.py`: compares the retained 18-output binding hashes and five exact token IDs; requires a successful positive log and both W1c zero-host/zero-mismatch service lines.
- `audit_sources.py`: hashes ordered project compiler inputs, proves other service headers unchanged and absence of position host drivers; emits exact host patches and `source-audit.json`.

## Reading

Read W1 brief, both copies of the Taalas skill, complete supplied source notes, patent atlas, architecture/numerics and implementation workflow references, and relevant retained primary P1/P3 descriptions and claims. P1 shared coefficient products/fixed selection/row control/serial transport/access-transistor cells are distinct from a physical macro proof; P3 requires actual peripheral/routing characterization. This task retains native FP32 frontend coefficients and exact fixed position bytes rather than quantizing them. The requested root `plan.md` is absent; this is recorded in `FAILURES.md`. Current W1c/W1/AGENTS authorization permits this bounded implementation and simulation.

Completed C++ build intermediates were compressed into internal `compiled-intermediates.tar.gz`, every archived member was hash-verified, and redundant loose files were removed to reclaim 533,718,221 bytes. The active executable remains at its recorded path. `archive_build.py` and `build-archive.json` record this storage-only operation. Regenerate before rebuilding, or extract the archive into `obj`.


## Reproduce and evidence

From the repository root:

```sh
.venv/bin/python overnight-20261014/onchip-front/prepare_w1c.py
.venv/bin/python overnight-20261014/onchip-front/run_stage.py lint-full
.venv/bin/python overnight-20261014/onchip-front/run_stage.py generate-full
.venv/bin/python overnight-20261014/onchip-front/run_stage.py compile
.venv/bin/python overnight-20261014/onchip-front/run_stage.py unit-front-build
.venv/bin/python overnight-20261014/onchip-front/run_stage.py unit-front
.venv/bin/python overnight-20261014/onchip-front/run_stage.py unit-position-build
.venv/bin/python overnight-20261014/onchip-front/run_stage.py unit-position
.venv/bin/python overnight-20261014/onchip-front/run_stage.py fixture
.venv/bin/python overnight-20261014/onchip-front/run_stage.py positive
.venv/bin/python overnight-20261014/onchip-front/run_stage.py compare
.venv/bin/python overnight-20261014/onchip-front/run_stage.py render
.venv/bin/python overnight-20261014/onchip-front/audit_sources.py
```

The positive runner refuses a nonempty `actual` directory; preserve the prior outputs before an intentional rerun. `commands.json` contains every exact subprocess argument, and each log has a paired JSON recording the niced command, working directory, PID, exit status and elapsed time. The initial compile launcher lost its completion record across a steering turn; the final incremental compile rebuilt the host and linked successfully. This evidence gap is preserved in `FAILURES.md`.

| Stage | Exit | Seconds | Log |
| --- | ---: | ---: | --- |
| lint-full | 0 | 36.554 | [20261014T010352-lint-full.log](logs/20261014T010352-lint-full.log) |
| generate-full | 0 | 75.838 | [20261014T010457-generate-full.log](logs/20261014T010457-generate-full.log) |
| unit-front-build | 0 | 1.811 | [20261014T010444-unit-front-build.log](logs/20261014T010444-unit-front-build.log) |
| unit-front | 0 | 2.181 | [20261014T010457-unit-front.log](logs/20261014T010457-unit-front.log) |
| unit-position-build | 0 | 0.040 | [20261014T010507-unit-position-build.log](logs/20261014T010507-unit-position-build.log) |
| unit-position | 0 | 0.077 | [20261014T010518-unit-position.log](logs/20261014T010518-unit-position.log) |
| compile | 0 | 6.956 | [20261014T010858-compile.log](logs/20261014T010858-compile.log) |
| fixture | 0 | 1.419 | [20261014T010920-fixture.log](logs/20261014T010920-fixture.log) |
| positive | 0 | 3308.270 | [20261014T010943-positive.log](logs/20261014T010943-positive.log) |
| compare | 0 | 0.042 | [20261014T020511-compare.log](logs/20261014T020511-compare.log) |
| render | 0 | 0.132 | [20261014T020511-render.log](logs/20261014T020511-render.log) |

`comparison-result.json` contains all 18 actual output hashes and the original binding hash. `rom-manifest.json` records original binary and emitted hex hashes, widths, counts and exact round trips. `run-binding.json` binds the executed binary and source copies. Finalization rehashed all original source inputs, copied runtime sources, ROM binaries, emitted images and the executable and found them unchanged.

`source-audit.json` and the three `*.patch` files show exact host changes for the lead's merge. `monitor.py` and `positive-status.json` provide bounded process/disk/progress observations. `archive_build.py` and `build-archive.json` preserve and verify the finished C++ build intermediates in an internal archive while retaining the active executable; this reclaimed 533,718,221 bytes. `completion.json` records the final service counts, tokens, text and simulation duration. `finalize_results.py` verifies the completion evidence before writing this final report. `logs/`, `FAILURES.md`, and the other JSON manifests retain execution evidence. No services remain unfinished within W1c scope. W1/W1b integration is for the lead; this wrapper deliberately leaves their services at the original interfaces.
