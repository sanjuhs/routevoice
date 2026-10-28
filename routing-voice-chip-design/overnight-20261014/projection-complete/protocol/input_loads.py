from pathlib import Path
import sys,json,collections
sys.dont_write_bytecode=True
R=Path.cwd();S=R/'overnight-20261014/taalas-pitch/timing';sys.path.insert(0,str(S));import simulate
P=S/'r1280-g02/joined-canonical.spice'; caps=collections.defaultdict(float);gates=collections.defaultdict(list)
for line in P.open():
 f=line.split()
 if line.startswith('C'):
  for node in f[1:3]:
   if node=='PC' or node.startswith('WL'):caps[node]+=simulate.valueff(f[3])
 if line.startswith('X') and (f[2]=='PC' or f[2].startswith('WL')):gates[f[2]].append(' '.join(f[5:]))
out={'source':str(P),'source_sha256':simulate.sha(P),'scope':'Extracted joined128-column crop only. Incident mutual+ground metal C, not effective capacitance nor full-bank pin load. MOS gate capacitance is separately bias dependent and excluded from metal sums.','pin_metal_cap_ff':dict(caps),'gate_counts':{n:len(v) for n,v in gates.items()},'gate_models':{n:dict(collections.Counter(v)) for n,v in gates.items() if n in ['PC','WL0']},'full_bank_structural_gate_counts':{'each_WL':1280,'PC':1280},'full_bank_total_pin_cap_ff':None}
(R/'overnight-20261014/projection-complete/protocol/input_loads.json').write_text(json.dumps(out,indent=2));print(json.dumps({'PC_metal_fF_crop':caps['PC'],'WL_metal_fF_crop_min':min(v for n,v in caps.items() if n.startswith('WL')),'WL_metal_fF_crop_max':max(v for n,v in caps.items() if n.startswith('WL')),'PC_gate_count_crop':len(gates['PC']),'WL0_gate_count_crop':len(gates['WL0']),'gate_models':out['gate_models']},indent=2))
