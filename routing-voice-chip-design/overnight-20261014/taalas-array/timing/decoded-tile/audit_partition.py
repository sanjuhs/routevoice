from pathlib import Path
from collections import defaultdict,Counter
import re,json
W=Path(__file__).resolve().parent;O=W/'v1';shared={'VDD','VSS','PC','EVAL'}|{f'ROW{i}' for i in range(6)}
def group(n):
 if (m:=re.match(r'RV_DECODED_BANK_00_(\d+)_0/',n)):return int(m[1])
 if (m:=re.match(r'WL_G(\d+)_',n)):return int(m[1])
 if (m:=re.match(r'a_(-?\d+)_',n)):return int(m[1])//93600
 return None
devices={};nodes=defaultdict(set);counts=Counter();parts=[[] for _ in range(10)]
for l in (O/'canonical.spice').read_text().splitlines():
 if not l.startswith('X'):continue
 f=l.split();assert f[0] not in devices
 if '05v0' in f[5]:gs={group(n) for n in f[1:5]}-{None}
 else:
  gs={int(m[1]) for n in f[1:5] if (m:=re.match(r'WL_G(\d+)_',n))}
  if not gs:gs={int(m[1])//128 for n in f[1:5] if (m:=re.match(r'OUT(\d+)$',n))}
  if not gs:gs={int(m[1])//32 for n in f[1:5] if (m:=re.match(r'IDX(\d+)_',n))}
 assert len(gs)==1,(l,gs);g=gs.pop();assert 0<=g<10
 devices[f[0]]=g;counts[g]+=1;parts[g].append(l)
 for n in f[1:5]:nodes[n].add(g)
cross={n:sorted(gs) for n,gs in nodes.items() if len(gs)>1};assert set(cross)==shared,cross
assert all(gs==list(range(10)) for gs in cross.values())
assert len(devices)==111460 and [counts[g] for g in range(10)]==[11146]*10
for i in range(1280):assert nodes[f'OUT{i}']=={i//128}
for g in range(10):
 for r in range(64):assert nodes[f'WL_G{g}_R{r}']=={g}
for g in range(10):
 p=O/f'bank{g}-canonical.spice'
 if p.exists():assert Counter(l for l in p.read_text().splitlines() if l.startswith('X'))==Counter(parts[g])
ref_cover=False
if all((O/f'bank{g}-reference.spice').exists() for g in range(10)):
 expected=Counter(l for l in (O/'reference.spice').read_text().splitlines() if l.startswith('X'));actual=Counter()
 for g in range(10):actual.update(l for l in (O/f'bank{g}-reference.spice').read_text().splitlines() if l.startswith('X'))
 assert expected==actual;ref_cover=True
report={'independent_reference_exact_disjoint_device_cover':ref_cover,'exact_disjoint_device_cover':True,'total_devices':len(devices),'devices_per_bank':[counts[g] for g in range(10)],'cross_bank_nets':cross,'only_intended_cross_bank_nets':True,'all1280_output_ports_owned_by_expected_bank':True,'all640_wordlines_owned_by_expected_bank':True,'partition_files_checked_for_exact_device_identity':[g for g in range(10) if (O/f'bank{g}-canonical.spice').exists()],'global_terminal_fanout_population_matches_reference':json.loads((O/'dimensions-check.json').read_text())['global_control_power_terminal_population_match'],'node_normalization_bijective':True,'bijection_evidence':'connectivity.json and assertions in lvs.py; no merged nodes','scope':'Actual fulltile Magic flat netlist, all111460devices, only10explicit shared global nets; each component retains original connected global terminals.'};(O/'partition-audit.json').write_text(json.dumps(report,indent=2));print(report)
