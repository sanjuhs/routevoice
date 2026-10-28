"""Count actual mapped cell input pins; clock and constants reported separately."""
import collections
import hashlib
import gzip
import json
import sys
import re
from pathlib import Path

p = Path(sys.argv[1])
d = json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
m = d['modules']['rv_k64_array_port']
loads = collections.Counter()
drivers = collections.defaultdict(list)
names = collections.defaultdict(list)
tie_bits = set()
for name, net in m['netnames'].items():
    for i, bit in enumerate(net['bits']):
        names[bit].append(name + (f'[{i}]' if len(net['bits']) > 1 else ''))
for name, cell in m['cells'].items():
    for pin, bits in cell['connections'].items():
        direction = cell['port_directions'][pin]
        for bit in bits:
            if direction in ('input', 'inout'):
                loads[bit] += 1
            if direction in ('output', 'inout'):
                drivers[bit].append(f'{name}/{pin}')
                if '__tieh' in cell['type'] or '__tiel' in cell['type']:
                    tie_bits.add(bit)
clock_bits = set(m['ports']['clk']['bits'])
signal = [(bit,n) for bit,n in loads.items() if isinstance(bit,int) and bit not in clock_bits]
signal.sort(key=lambda x:x[1],reverse=True)
result = {
    'netlist_json':str(p), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
    'method':'Mapped cell input-pin loads; excludes clock and constant nodes from max signal fanout.',
    'max_signal_fanout':signal[0][1],
    'max_nonclock_nontie_fanout':max(n for b,n in signal if b not in tie_bits),
    'max_tie_cell_fanout':max((loads[b] for b in tie_bits),default=0),
    'signal_nets_over_16':sum(n>16 for _,n in signal),
    'clock_loads':sum(loads[b] for b in clock_bits),
    'cells':len(m['cells']),
    'buffers':sum('buf_' in c['type'] for c in m['cells'].values()),
    'top_signal_nets':[{'bit':b,'loads':n,'names':names[b][:8],'drivers':drivers[b][:8]} for b,n in signal[:40]],
}
dup={}
for name,net in m['netnames'].items():
    match=re.search(r'w9_row_g(\d+)(?:\[(\d+)\])?$',name)
    if match:
        group=int(match.group(1));bits=dup.setdefault(group,{})
        if match.group(2) is not None:bits[int(match.group(2))]=net['bits'][0]
        else:bits.update(enumerate(net['bits']))
result['duplicated_row_nets']=dup
result['duplicated_row_bit6_distinct']=len({bits[6] for bits in dup.values() if 6 in bits})
result['duplicated_row_decode_fanout']={group:{i:loads[b] for i,b in bits.items() if i>=6} for group,bits in dup.items()}
print(json.dumps(result,indent=2))
