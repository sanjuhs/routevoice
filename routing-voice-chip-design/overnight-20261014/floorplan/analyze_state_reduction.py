#!/usr/bin/env python3
"""Hypothetical state-capacity reduction under the frozen abstract packing policy."""
import json,copy,math
from pathlib import Path
from area_models import configure,block_area
from make_floorplan import tile_blocks,pack
W=Path(__file__).resolve().parent;cfg=json.loads((W/'blocks_final.json').read_text());c=configure(cfg,'sram_bitcell_large_macro','lossless');mem=next(b for b in c['blocks'] if b['name']=='mutable_arrays');base_bits=mem['mutable_bits'];slope=8*(17.8/.70)*1.1/1e6
base_area=sum(block_area(c,b,'final_pitch')['total_mm2'] for b in c['blocks']);core_area=(26-1.4)*(33-1.4)
def trial(removed_bytes):
 q=copy.deepcopy(c);b=next(b for b in q['blocks'] if b['name']=='mutable_arrays');b['memory_area_by_scenario']['sram_bitcell_large_macro']=(base_bits-8*removed_bytes)*(17.8/.70)*1.1/1e6
 t,a=tile_blocks(q,'final_pitch');return pack(t,26000,height=33000),sum(x['area_mm2'] for x in a)
# Scan every whole byte, rather than assuming monotonicity across ceil(tile-count) boundaries.
# Group expensive equivalent geometries by mutable tile count and quantized side length.
cache={};trials=[];threshold=None
for removed in range(math.floor(base_bits/8)+1):
 area=(base_bits-8*removed)*(17.8/.70)*1.1/1e6
 if area<=0:continue
 n=math.ceil(area/c['maximum_tile_area_mm2']);side=math.ceil(math.sqrt(area/n)*1000/5)*5;key=(n,side)
 if key not in cache:cache[key]=trial(removed)[0]
 if removed%1024==0:trials.append(dict(removed_bytes=removed,removed_KiB=removed/1024,placement_pass=cache[key]))
 if cache[key]:threshold=removed;break
assert threshold is not None
inv=json.loads((W.parent/'storage-inventory/inventory.json').read_text());pairs=[]
for module,vars in [('rv_encoder_bank_consumer_edge_v1',['bank0','bank1']),('rv_producer_mutable_storage_v1',['bankA','bankB'])]:
 a=[q for q in inv['all_mutable_arrays'] if q['module_orig']==module and q['var'] in vars];assert len(a)==2
 pairs.append(dict(module=module,arrays=a,combined_bytes=sum(q['total_bytes'] for q in a),one_buffer_bytes=a[0]['total_bytes'],scope='Two equal-size physical buffers, not duplicate contents. Removal/sharing requires lifetime/ownership/throughput proof; not applied to baseline.'))
cases=[]
for removed in [0,threshold,80*1024,160*1024]:
 fit,area=trial(removed);cases.append(dict(removed_bytes=removed,removed_kB_decimal=removed/1000,removed_KiB=removed/1024,placement_pass=fit,block_area_mm2=area))
r=dict(scope='Hypothetical capacity-only guidance; no RTL/state removed and no numerical/throughput equivalence proven',reticle_mm=[26,33],core_mm2=core_area,baseline_blocks_mm2=base_area,area_only_removal_lower_bound_bytes=max(0,math.ceil((base_area-core_area)/slope)),first_fitting_removed_bytes=threshold,first_fitting_removed_kB_decimal=threshold/1000,first_fitting_removed_KiB=threshold/1024,remaining_logical_bytes=base_bits/8-threshold,area_saved_mm2=threshold*slope,mm2_saved_per_KiB=slope*1024,search='Every integer-byte reduction checked through first fit; equivalent geometries cached by tile count and5um side quantization. No monotonic binary-search assumption.',distinct_geometries_checked=len(cache),sampled_trials_1KiB=trials,cases=cases,largest_equal_capacity_buffer_pairs=pairs,not_duplicate_examples=[dict(var=q['var'],bytes=q['total_bytes'],module=q['module_orig']) for q in inv['all_mutable_arrays'][:4]],qualification='Baseline block area is below core area, so no strictly positive state-removal lower bound follows from area alone. Packing/layout improvement may replace reduction. Current deterministic abstract packing threshold is not a physical necessity or global optimum.')
(W/'state_reduction_guidance.json').write_text(json.dumps(r,indent=2)+'\n');print('W3-STATUS: state-reduction geometric threshold',threshold,'B',threshold/1024,'KiB; area-only bound',r['area_only_removal_lower_bound_bytes'],'B; A/B candidates',[(p['module'],p['one_buffer_bytes']) for p in pairs])
