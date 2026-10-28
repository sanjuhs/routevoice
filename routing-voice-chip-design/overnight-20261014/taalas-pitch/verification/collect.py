"""Collect completed immutable evidence without granting unfinished stages credit."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent
def read(path):
 return json.loads(path.read_text()) if path.exists() else None
records=[]
for rows in (64,1280):
 name=f'r{rows}-v2';lvs_name=name;o=P/lvs_name
 record=dict(rows=rows,lvs_run=lvs_name,lvs_receipt=str((o/'full-bank-netgen-result.json').relative_to(P)),extraction_mode='connectivity_only_no_C_R' if lvs_name.endswith('-connectivity') else 'full_C_ext_LVS_spice',input=read(o/'input.json'),
  readback=read(P/f'{name}-independent-readback.json'),
  extraction=read(o/'extract-process.json'),
  connectivity=read(o/'connectivity.json'),
  lvs=read(o/'full-bank-netgen-result.json'),
  negative_control=read(o/'negative-width-netgen-result.json'))
 record['verified']=all((record['readback'] is not None and record['readback']['bit_mismatches']==0,
  record['extraction'] is not None and record['extraction']['returncode']==0 and record['extraction']['status']=='finished',
  record['connectivity'] is not None and record['connectivity']['exact_device_tuples_and_dimensions_match'],
  record['lvs'] is not None and record['lvs']['pass'],
  record['negative_control'] is not None and record['negative_control']['negative_control_rejected']))
 log=o/'extract-console.log'
 record['extraction_warning_lines']=[line for line in log.read_text().splitlines() if 'warning' in line.lower()] if log.exists() else None
 record['watchdog_extension']=read(o/'watchdog-extension.json')
 record['native_ext_archive']=read(o/'native-ext-compression.json')
 record['spice_evidence_archives']=read(o/'spice-evidence-compression.json')
 record['slice_evidence_archives']=read(o/'slice-evidence-compression.json')
 nglog=o/'full-bank-netgen-console.log'
 ngtext=nglog.read_text() if nglog.exists() else ''
 setup=P.parents[2]/'pdks/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl'
 record['netgen_reduction']=dict(raw_devices_checked_independently=record['connectivity']['extracted_devices'] if record['connectivity'] else None,device_counts_printed=[int(v) for v in re.findall(r'Circuit W6_PITCH_BANK_FLAT contains (\d+) device instances',ngtext)],explicit_log_explanation='Circuit was modified by parallel/series device merging.' if 'Circuit was modified by parallel/series device merging.' in ngtext else None,setup_sha256=hashlib.sha256(setup.read_bytes()).hexdigest(),setup_mos_rules='gf180mcuD_setup.tcl MOS section enables parallel, length critical, width add on both circuits. No claim about which individual raw devices were merged.',raw_graph_scope='Independent exact full device/node/model/W/L multiset equality before Netgen reductions.')
 if rows==1280:
  c=P/name
  record['cancelled_connectivity_only_attempt']=dict(run=name+'-connectivity',process=read(P/(name+'-connectivity')/'extract-process.json'),cancellation=read(P/(name+'-connectivity')/'cancelled-after-full-C-success.json'))
  record['separate_full_C_extraction']=dict(run=name,process=read(c/'extract-process.json'),watchdog_3600=read(c/'watchdog-extension.json'),watchdog_5400=read(c/'watchdog-extension-5400.json'))
 records.append(record)
report=dict(scope='Actual complete 64-row and 1,280-row array + 1,280 pre2 receiver GDS extraction versus independent original K64 packed-tensor reference. No partition-only credit.',
 source_identity=read(P/'independent-image-check.json'),variants=records,
 scripts_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'verify.py',P/'verify-connectivity.py',P/'readback.py',P/'collect.py']},
 proof_exclusions=['Timing and energy are separate worker results','No missing driver/decoder/latch or whole-chip proof','Selected DRC is a parent-worker result'])
(P/'results.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# W6 independent verification','',report['scope'],'',
 '| Rows | Selections | GDS readback | Exact graph/W/L | Full Netgen | Width negative |',
 '|---:|---:|---|---|---|---|']
for r in records:
 def state(v,key):return 'PASS' if v and v[key] else ('FAIL' if v else 'pending')
 rb=r['readback'];rbtxt=f"{rb['compared_bits']:,} bits, {rb['bit_mismatches']} mismatches" if rb else 'pending'
 lines.append(f"| {r['rows']} | {r['rows']*320:,} | {rbtxt} | {state(r['connectivity'],'exact_device_tuples_and_dimensions_match')} | {state(r['lvs'],'pass')} | {state(r['negative_control'],'negative_control_rejected')} |")
lines+=['','The independent reference is decoded directly from the original K64 packed',
 'tensor. Source identity also checks all 409,600 selections against W5 indices',
 'and W2b frozen RTL. Each Netgen pass requires unique matching and no property',
 'errors. Full 1,280-row Netgen prints 1,643,520 raw devices and 827,201 after its',
 'reported parallel/series merging under the standard GF180 setup; independent',
 'raw exact graph/W/L equality checks every device before that reduction.',
 'The negative reports precharge width 2.88 µm versus 5.76 µm (66.7% delta,',
 '1% cutoff), explicitly rejected despite the topology unique-match phrase.',
 'Only a checked bijective hierarchical-prefix removal is permitted; devices',
 'and node topology are unchanged. Each saved-GDS readback audits actual Via1',
 'programming sites and each group array instantiated exactly once.','',
 'The full 1,280-row LVS path is the original completed `r1280-v2/` extraction.',
 'A separate connectivity-only attempt was cancelled with recorded SIGTERM',
 'after the original full-C extraction succeeded. It receives no pass/fail',
 'verification credit, and its native receipt and cancellation reason remain.',
 'The full-C extraction returned 0 after 3,122.505 seconds. Its transparently',
 'logged owned-watchdog extensions preserve native exit status; the final',
 'guard observed at least 24.7397 GiB free. Positive and negative full-bank',
 'Netgen runs finished in 438.701 and 454.969 seconds, respectively.',
 'The native full-bank .ext is losslessly archived as',
 '`r1280-v2/W6_PITCH_BANK_FLAT.ext.gz`; native and independently decompressed',
 'SHA-256 match. See `native-ext-compression.json` for bytes, hashes, two',
 'no-reader checks and restoration instructions. The archived source still',
 'supports reproduction of the official capacitance export.',
 'The four completed full-bank SPICE netlists are likewise archived as',
 '`*.spice.gz`; `spice-evidence-compression.json` records individual native,',
 'gzip and independently decompressed hashes and restoration instructions.',
 'The 64-row native extraction and four SPICE files are also losslessly',
 'archived; `r64-v2/slice-evidence-compression.json` records their independent',
 'roundtrip hashes, no-reader checks, and restoration commands.',
 'Failures and intermediate evidence remain in their original directories.',
 'The earlier r64-v1 DRC failure is reported by the parent; its independent',
 'readback passed but receives no clean-layout credit.','',
 'See [results.json](results.json), [README.md](README.md), and',
 '[source-reading.json](source-reading.json) for exact scope, methods and inputs.','']
(P/'RESULTS.md').write_text('\n'.join(lines))
print('W6-STATUS: verification evidence collected',[(r['rows'],r['verified']) for r in records])
