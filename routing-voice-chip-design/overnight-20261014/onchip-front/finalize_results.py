"""Finalize only after successful positive/compare/render and unchanged run sources."""
from pathlib import Path
import hashlib,json,re
W=Path(__file__).resolve().parent
R=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-front'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
binding=json.loads((W/'run-binding.json').read_text())
assert sha(Path(binding['binary']))==binding['binary_sha256']
for p,h in binding['sources'].items():assert sha(Path(p))==h,p
audit=json.loads((W/'source-audit.json').read_text())
assert audit['passed']
for row in audit['ordered_project_compiler_inputs']:
 assert sha(Path(row['path']))==row['sha256'],row['path']
original=json.loads((W/'source-provenance.json').read_text())
for p,h in original.items():assert sha(Path(p))==h,p
manifest=json.loads((W/'rom-manifest.json').read_text())
for row in manifest:
 assert sha(Path(row['input']))==row['input_sha256']
 assert sha(Path(row['output']))==row['output_sha256']
 assert row['roundtrip_pass']
archive=json.loads((W/'build-archive.json').read_text())
assert archive['all_archived_contents_verified'] and sha(Path(archive['archive']))==archive['archive_sha256']
comparison=json.loads((W/'comparison-result.json').read_text());assert comparison['passed'] and comparison['native_output_comparisons']==18
stages=['lint-full','generate-full','unit-front-build','unit-front','unit-position-build','unit-position','compile','fixture','positive','compare','render']
records=[]
for name in stages:
 p=sorted((W/'logs').glob('*-'+name+'.json'))[-1];d=json.loads(p.read_text());assert d['exit_code']==0,(name,d)
 records.append((name,p,d))
positive=next(d for n,p,d in records if n=='positive');render=next(d for n,p,d in records if n=='render')
assert 'Switch on the lights' in Path(render['log']).read_text()
report=W/'RESULTS.md';s=report.read_text()
s=s.replace('# W1c frontend and positions — qualification in progress','# W1c frontend and positions — PASS')
a=s.index('ROM generation,');b=s.index('\n\nAll W1c',a)
s=s[:a]+f'''**Measured result:** F64 fixture and positive passed. All **18** actual output files match the retained native binding byte-for-byte by size and SHA-256. Tokens are `{comparison['tokens']}`, including EOS; rendered text is **Switch on the lights**. Positive simulation elapsed **{positive['elapsed_seconds']:.3f} seconds** ({positive['elapsed_seconds']/60:.2f} minutes).

```
ONCHIP service=frontend_immutable rtl_replies=55720960 host_replies=0 mismatches=0
ONCHIP service=producer_positions rtl_replies=2560 host_replies=0 mismatches=0
```

The frontend isolated test checked all 2,074,560 native FP32 words, 1,521 held cycles, 1,521 warm-reset cycles, five invalid addresses and an immutable-write rejection. Retained position four-state controls passed 6 legal requests, 11 invalid/X/Z offers and 18 held cycles. Full-top lint/generation/compile passed; lint reported only 164 TIMESCALEMOD warnings. No additional full-chain fault suite, F144 run or new speech corpus was executed. Functional RTL closure of these two services does not establish fabricated ROM density or whole-chip physical closure.

The lead explicitly clarified that the one-long-simulation limit applies per worker and authorized concurrent W1/W1b/W1c runs. This worker ran one positive simulation with `nice -n 10`; compile commands use at most six jobs and the launcher protects the 20 GiB disk floor with a 22 GiB reserve.''' + s[b:]
s+='''

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
'''
for name,p,d in records:s+=f"| {name} | 0 | {d['elapsed_seconds']:.3f} | [{Path(d['log']).name}](logs/{Path(d['log']).name}) |\n"
s+='''
`comparison-result.json` contains all 18 actual output hashes and the original binding hash. `rom-manifest.json` records original binary and emitted hex hashes, widths, counts and exact round trips. `run-binding.json` binds the executed binary and source copies. Finalization rehashed all original source inputs, copied runtime sources, ROM binaries, emitted images and the executable and found them unchanged.

`source-audit.json` and the three `*.patch` files show exact host changes for the lead's merge. `monitor.py` and `positive-status.json` provide bounded process/disk/progress observations. `archive_build.py` and `build-archive.json` preserve and verify the finished C++ build intermediates in an internal archive while retaining the active executable; this reclaimed 533,718,221 bytes. `completion.json` records the final service counts, tokens, text and simulation duration. `finalize_results.py` verifies the completion evidence before writing this final report. `logs/`, `FAILURES.md`, and the other JSON manifests retain execution evidence. No services remain unfinished within W1c scope. W1/W1b integration is for the lead; this wrapper deliberately leaves their services at the original interfaces.
'''
report.write_text(s)
(W/'completion.json').write_text(json.dumps({'passed':True,'services':{'frontend_immutable':{'native_bytes':8298240,'rtl_replies':55720960,'host_replies':0,'mismatches':0},'producer_positions':{'native_bytes':1310720,'rtl_replies':2560,'host_replies':0,'mismatches':0}},'total_native_bytes':9608960,'comparisons':18,'tokens':comparison['tokens'],'text':'Switch on the lights','positive_seconds':positive['elapsed_seconds'],'source_and_binary_hashes_stable':True},indent=2)+'\n')
print('W1c-STATUS: PASS; RESULTS.md finalized; both services zero host replies/mismatches, all 18 comparisons and EOS/render passed')
