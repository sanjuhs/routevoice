"""Close W1b evidence after native positive, independent postflight, and render."""
from pathlib import Path
import hashlib,json
W=Path(__file__).resolve().parent
verification=json.loads((W/'verification.json').read_text())
renderpath=W/'logs/20261014T020810-render.log'
render=json.loads(renderpath.read_text())
assert verification['passed'] and len(verification['actual_outputs'])==18
assert render['passed'] and render['text']=='Switch on the lights' and render['tokens']==verification['tokens']==[28176,373,278,26068,2]
stages=[json.loads(p.read_text()) for p in sorted((W/'logs').glob('*.json'))]
assert all(p['exit_code']==0 for p in stages)
result=dict(passed=True,scope='W1b encoder QKV/O and immutable regions4..12 integrated on-chip in RTL; other host fixed services unchanged.',native_ROM_bytes=7604480,physical_PPA_credit=False,services=verification['services'],tokens=verification['tokens'],text=render['text'],output_comparisons=18,positive_seconds=verification['elapsed_seconds'],clocks=verification['whole'],stages=stages,verification='verification.json',render_log=str(renderpath))
(W/'result.json').write_text(json.dumps(result,indent=2)+'\n')
p=W/'RESULTS.md';s=p.read_text()
if s.startswith('# W1b encoder on-chip services — PASS'):
 print('W1b-STATUS: final PASS evidence rechecked; RESULTS.md already finalized')
 raise SystemExit(0)
start=s.index('## Implemented scope')
s='''# W1b encoder on-chip services — PASS

Completed 14 October 2026. The encoder-only `rv_allonchip_top_w1b` passes the requested F64 fixture and positive stages, all 18 frozen output comparisons, and native rendering to **“Switch on the lights”**. The exact token sequence is **[28176, 373, 278, 26068, 2]**, including EOS.

**7,604,480 native bytes** are supplied by the new RTL ROM responders. The positive simulation took **3,451.004 seconds (57 minutes 31 seconds)**. It completed **312,578,649 common clocks**, including **55,302,920 encoder clocks**. Every existing conservation/numerical predicate in the retained postflight passed.

| Service | Actual RTL replies | Host replies | Mismatches |
|---|---:|---:|---:|
| Encoder QKV | 368,640 | 0 | 0 |
| Encoder O | 15,360 | 0 | 0 |
| Encoder immutable regions 4..12 | 1,947,520 | 0 | 0 |

The other workers' services remain unchanged in this wrapper. The lead must merge the independently verified wrappers and test that combined design.

'''+s[start:]
s=s.replace('These are functional behavioral ROM results, not custom macro synthesis/layout/PPA results or whole-recognizer success yet.','The integrated full recognizer also passed below. These results establish RTL service and numerical behavior; custom macro synthesis/layout/PPA is not measured here.')
s=s.replace('- `commands.json`, `no-pch.mk`, `rom/`, `rom-manifest.json`, `logs/`: generated reproducibility/evidence artifacts.','''- `host-changes.patch`: exact diff of the two modified host source files for merge review.
- `run-input-pins.json`: source/header/binary hashes captured during the run and rechecked at successful postflight. The ROM input/output and original top/host/header hashes were also rechecked.
- `commands.json`, `no-pch.mk`, `rom/`, `rom-manifest.json`, `logs/`: generated reproducibility/evidence artifacts.
- `verification.json`, `result.json`, `finalize_results.py`: all 18 output hashes, original conservation results, exact moved-service counts, tokens, native stage records and final report closure.''')
s=s.replace('.venv/bin/python overnight-20261014/onchip-enc/run_stage.py positive\n', '''.venv/bin/python overnight-20261014/onchip-enc/run_stage.py positive
.venv/bin/python -B overnight-20261014/onchip-enc/verify_outputs.py overnight-20261014/onchip-enc/logs/20261014T011032-positive.log
.venv/bin/python -B overnight-20261014/onchip-enc/run_stage.py render
.venv/bin/python -B overnight-20261014/onchip-enc/finalize_results.py
''')
a=s.index('Passed logs:');b=s.index('\nSee `FAILURES.md`',a)
table='''## Executed evidence

All commands exited 0. Full-top lint/generation logs contain no warnings or errors.

| Stage | Seconds | Log |
|---|---:|---|
'''
for x in stages:
 table+=f"| {x['stage']} | {x['elapsed_seconds']:.3f} | [{Path(x['log']).name}](logs/{Path(x['log']).name}) |\n"
table+='''
`verification.json` records the exact file size and SHA-256 match for each of the **18/18** expected output files and the retained full-run conservation predicates. `result.json` records final PASS and every native launch. `logs/20261014T020810-render.log` records the pinned renderer/tokenizer hashes and exact text/token output.

The three exhaustive standalone tests independently read the original `.bin` files: QKV **46,080 packets / 1,843,200 bytes**; O **1,920 packets / 614,400 bytes**; immutable **160,840 packets / 5,146,880 bytes**. Combined held-response cycles: **313,260**; warm-reset held-response cases: **211**. Original binary bytes, source bits, scales, zero points and accumulator/numerical contracts were preserved.

## Limits and remaining integration work

- No requested W1b work remains unfinished. F64 success covers the requested positive path. Standalone responders additionally cover held responses, warm-reset held ACK fencing, illegal layers and POR cancellation; a full connected reset/orphan/negative suite is not newly qualified.
- These are native immutable payload ROMs with `$readmemh` initialization and no runtime weight write ports. They do not constitute a fabricated mask-ROM/shared-product access-cell implementation, a whole-chip synthesizability report, or an area/timing/power result. The existing compute datapath and dynamic state remain unchanged.
- Decoder, frontend and producer-position host services remain in this encoder-only wrapper, as required by the parallel split. Combined W1/W1b/W1c merge and rerun belong to the lead.
- No failed native stage occurred. The absent root `plan.md` remains the recorded reading gap; no substitute root file was created.
'''
s=s[:a]+table+s[b:]
p.write_text(s)
print('W1b-STATUS: complete PASS; RESULTS.md and result.json finalized; requested W1b work finished')
