#!/usr/bin/env python3
"""Proposed placement from exact tensor/operator names; unresolved tensors stay visible."""
import json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'reports/tensor-manifest.json').read_text())
rows=[]
for graph in manifest['graphs']:
    nodes={n['name']:n for n in graph['nodes']}
    for t in graph['tensors']:
        fn=graph['file'];evidence=[]
        if fn.startswith('frontend'):die='die1';evidence=['frontend graph']
        elif fn=='adapter.ort':die='die2';evidence=['adapter after encoder']
        elif fn in ('decoder_kv.ort','cross_kv.ort'):die='die3';evidence=['decoder-side graph']
        else:
            blocks=set(int(b) for b in re.findall(r'blocks\.(\d+)\.',t['name']))
            for c in t['consumers']:
                node=nodes[c['node']]
                for value in node['inputs']:
                    blocks.update(int(b) for b in re.findall(r'blocks\.(\d+)\.',value))
                for value in node['outputs']:
                    m=re.fullmatch(r'linear(?:_(\d+))?',value)
                    if m:blocks.add(int(m.group(1) or 0)//6)
            if blocks and all(0<=b<3 for b in blocks):die='die1'
            elif blocks and all(3<=b<6 for b in blocks):die='die2'
            else:die='unresolved_encoder_shared'
            evidence=['proposed encoder block indices '+str(sorted(blocks))+' from names; scheduling/graph cut must be verified']
        rows.append({'graph':fn,'tensor':t['name'],'bytes':t['bytes'],'dtype':t['dtype'],'shape':t['shape'],'proposed_die':die,'evidence':evidence})
counts=Counter();sizes=Counter()
for r in rows:counts[r['proposed_die']]+=1;sizes[r['proposed_die']]+=r['bytes']
assert sum(sizes.values())==manifest['initializer_bytes']
report={'scope':'Proposed tensor partition; no physical capacity/throughput claim. Raw package bytes include duplicated tensors. Encoder name-based assignment is a candidate and needs verified graph slicing.','initializer_bytes':manifest['initializer_bytes'],'bytes_by_proposed_die':dict(sizes),'tensor_count_by_proposed_die':dict(counts),'tensors':rows,'interface_candidates':{'encoder_boundary_fp32_payload_bps':320*32*50,'encoder_boundary_int8_payload_bps_if_validated':320*8*50,'excludes':'framing, scheduling, retransmission and control overhead'},'cache_examples':{'fp32_self_kv_bytes_per_token':6*2*320*4,'fp32_self_kv_bytes_at_100_tokens':6*2*320*4*100,'fp32_cross_kv_bytes_at_80_steps':6*2*320*4*80,'note':'Examples, not configured bounds or complete SRAM allocation'},'power_watts':None,'silicon_area_mm2':None}
(ROOT/'reports/three-die-partition.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'bytes':dict(sizes),'counts':dict(counts)},indent=2))
