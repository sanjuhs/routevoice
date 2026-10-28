# W1 group (a): PASS

Decoder body cross/FF and compact decoder self are internal ROM responders in `rv_allonchip_top_v1`. The retained recognizer top is unchanged. The copied C++ providers check every observed RTL reply and its identity against the original binary data; they do not drive either moved service.

| Service | Native ROM bytes | F64 RTL replies | Host replies | Mismatches |
|---|---:|---:|---:|---:|
| Decoder body cross/FF | 8,908,800 | 1,392,000 | 0 | 0 |
| Compact decoder self | 2,519,040 | 787,200 | 0 | 0 |
| Total | 11,427,840 | 2,179,200 | 0 | 0 |

F64 positive passed in **3414.9 seconds**, **312,578,649 common clocks**, identical to baseline. Tokens `[28176,373,278,26068,2]` include EOS. All **18 native output sizes and SHA256 hashes** match the frozen binding. Renderer returned **Switch on the lights**. Lead independently confirmed this result.

Evidence:

- `logs/20261014T005600-lint-full.log`: exit 0.
- `logs/20261014T005708-generate-full.log`: exit 0.
- `logs/20261014T010226-compile.log`: exit 0 after disk interruption described below.
- `logs/20261014T010320-fixture.log`: `COMMON_NUMERIC_FIXTURE_PASS frames=64 values=20480 native_final_flags=1 clocks=0`.
- `logs/20261014T010323-unit-body-run.log`: 278,400 unique packets, 8,908,800 bytes, 204 held cycles, 204 warm-reset cycles, zero mismatches.
- `logs/20261014T010326-unit-self-run.log`: 78,720 unique packets, 2,519,040 bytes, 60 held cycles, 60 warm-reset cycles, zero mismatches.
- `logs/20261014T010334-positive.log`: full conservation assertions, both ONCHIP lines, final EOS PASS. Adjacent JSON records command, elapsed time and exit 0.
- `logs/20261014T020110-compare.log`, `comparison-result.json`: all 18 comparisons.
- `logs/20261014T020110-render.log`: text and five tokens.

Exact argv are in `commands-a.json`; each log's adjacent JSON records the executed command and working directory. Reproduce from repository root:

```sh
.venv/bin/python -B overnight-20261014/onchip/prepare_group_a.py
.venv/bin/python -B overnight-20261014/onchip/run_stage.py lint-full
.venv/bin/python -B overnight-20261014/onchip/run_stage.py generate-full
.venv/bin/python -B overnight-20261014/onchip/run_stage.py compile
.venv/bin/python -B overnight-20261014/onchip/run_stage.py fixture
.venv/bin/python -B overnight-20261014/onchip/run_stage.py unit-body-build
.venv/bin/python -B overnight-20261014/onchip/run_stage.py unit-body-run
.venv/bin/python -B overnight-20261014/onchip/run_stage.py unit-self-build
.venv/bin/python -B overnight-20261014/onchip/run_stage.py unit-self-run
.venv/bin/python -B overnight-20261014/onchip/run_stage.py positive
.venv/bin/python -B overnight-20261014/onchip/run_stage.py compare
.venv/bin/python -B overnight-20261014/onchip/run_stage.py render
```

Archive existing runtime `actual-a` within the authorized runtime directory before a rerun; the runner refuses to overwrite outputs. Objects/binary are under `~/.local/state/routevoice-internal-runs/20261014/onchip/`. ROM input/output SHA256 and round trips are in `rom-manifest.json`; original source pins in `source-provenance.json`; direct build-source pins in `group-a-source-hashes.json`.

Historical failures are retained: initial source audit caught an initialization drive and was corrected; first compile was stopped by the 22 GiB reserve guard (`logs/20261014T005849-compile.log`, exit 2). Other workers' disk use later brought free space below 20 GiB while our build was stopped; compilation resumed after free space recovered to 30 GiB. See `FAILURES.md`. After successful compile, 551,092,400 bytes of our generated intermediates were reclaimed, recorded in `reclaimed-build-intermediates.json`. The executable is retained; regenerate before rebuilding.

This validates functional behavioral ROM integration and cycle schedule, not physical ROM implementation, area, power, or timing. Groups b/c/d are owned by the parallel workers; the all-service merge is in `../onchip-all/` per lead guidance. Root `plan.md` was absent at source review.
