#!/usr/bin/env python3
"""Freeze sibling evidence and construct an explicitly conditional measured-input budget."""
import json,hashlib,datetime,math,re,copy
from pathlib import Path
W=Path(__file__).resolve().parent;R=W.parent.parent
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'); snap=W/'inputs'/('measured-'+stamp);snap.mkdir()
sources=['overnight-20261014/storage-inventory/inventory.json','overnight-20261014/storage-inventory/INVENTORY.md','overnight-20261014/fabric/results.json','overnight-20261014/fabric-k64/results.json','overnight-20261014/taalas-array/results.json','overnight-20261014/taalas-array/RESULTS.md','overnight-20261014/taalas-array/tall-bank/r320/geometry.json','overnight-20261014/taalas-array/tall-bank/r1280/geometry.json','overnight-20261014/taalas-array/tall-bank/timing/results.json','overnight-20261014/taalas-array/tall-bank/INTEGRATION.md','overnight-20261014/taalas-array/tall-bank/verification/results.json','docs/TAALAS-TALL-BANK-BUDGET.md','experiments/chip-integration-20261012-current-learned-fulltables-service-ledger-v2/ledger.json','docs/TAALAS-DIE-SIZE-AND-SYSTEM-COSTS-2026-10-02.md']
hashes={};data={}
for s in sources:
 raw=(R/s).read_bytes(); dest=snap/s;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);hashes[s]=dict(sha256=hashlib.sha256(raw).hexdigest(),snapshot=str(dest.relative_to(W)))
 if s.endswith('.json'):data[s]=json.loads(raw)
(snap/'hashes.json').write_text(json.dumps(hashes,indent=2))
old=json.loads((W/('historical_pre_measured_blocks.json' if (W/'historical_pre_measured_blocks.json').exists() else 'blocks.json')).read_text());cfg=copy.deepcopy(old);cfg.update(scope='Measured-input component floorplan; full macro timing/logic/power and SRAM port mapping remain unqualified',source_hashes=hashes,snapshot_utc=stamp,conservative_only_blocks=[],measurement_evidence={})
inv=data[sources[0]];w2b=data[sources[3]];w5=data[sources[4]];timing=data[sources[8]]
engine=w2b['variants']['array_port'];cell=engine['synthesis']['cell_area_mm2'];foot=engine.get('routed_area_mm2') or cell/.5
cfg['engine_model']=dict(cell_area_mm2=cell,footprint_mm2=foot,footprint_status='MEASURED routed' if engine.get('routed_area_mm2') else 'MEASURED synthesis / ASSUMED 0.5 utilization',clock_hz=25e6,macs_per_projection=409600,cycles=4163,macs_per_second=0.6e9,margin=2,count=math.ceil(2*.6e9/(25e6*409600/4163)),architecture='ASSUMED layer-group row bus shares one engine; two-die version duplicates engine. 25MHz is a target, not achieved timing. Fixed books in engine counted as local cache replica; global all-model books remain separate.')
sel_sc=(w2b['variants']['sc_rom']['synthesis']['cell_area_mm2']-cell)*1e6/409600
cfg['scenarios']={
 'stdcell':dict(selection_um2=sel_sc,periphery_factor=2,status='MEASURED synthesis differential SC-ROM minus ARRAY-PORT; ASSUMED 50% placement utilization. Not isolated routed selection measurement'),
 'custom7':dict(selection_um2=7.04,periphery_factor=1.25,status='ASSUMED historical component comparator +25%'),
 'optimistic3_5':dict(selection_um2=3.5,periphery_factor=1.25,status='ASSUMED optimistic comparator +25%'),
 'measured64':dict(selection_um2=w5['area_um2_per_selection']['full20_partial_readout_assembly_with_gaps'],periphery_factor=1,status='MEASURED partial GDS assembly; missing digital periphery separately allowed'),
 'measured320':dict(selection_um2=data[sources[6]]['assembly_um2_per_selection'],periphery_factor=1,status='MEASURED partial GDS assembly; sampled slice timing only; missing digital periphery separately allowed'),
 'measured1280':dict(selection_um2=data[sources[7]]['assembly_um2_per_selection'],periphery_factor=1,status='MEASURED partial GDS assembly; timing pending; missing digital periphery separately allowed')}
# Preserve 8-bit word widths and independent array instances; select least-area homogeneous depth bank.
allocation=[]
for a in inv['all_mutable_arrays']:
 depth=math.prod(a['dims']);lanes=math.ceil(a['elem_width']/8);inst=a['instances']
 choice=min(old['sram_macros'],key=lambda m:math.ceil(depth/m['bytes'])*m['area_mm2'])
 count=inst*lanes*math.ceil(depth/choice['bytes']); research=inst*math.ceil(a['bits_per_instance']/32768)
 kv=a['var'] in ('keys','values') and a['module_orig']=='taalas_compact_history_layer_self_o_q1'
 kvbits=a['total_bits']/4 if kv else a['total_bits']; kvlanes=math.ceil((8 if kv else a['elem_width'])/8)
 allocation.append(dict(kv8_eligible=kv,kv8_open_area_mm2=inst*kvlanes*math.ceil(depth/choice['bytes'])*choice['area_mm2'],kv8_research_area_mm2=inst*math.ceil((a['bits_per_instance']/4 if kv else a['bits_per_instance'])/32768)*.9479839488,kv8_dense_area_mm2=kvbits*12/1e6,**a,depth=depth,byte_lanes=lanes,macro=choice['name'],macro_count=count,allocated_bytes=count*choice['bytes'],open_area_mm2=count*choice['area_mm2'],research_banks=research,research_area_mm2=research*.9479839488,dense_area_mm2=a['total_bits']*12/1e6))
assert sum(a['total_bits'] for a in allocation)==inv['totals']['mutable_array_bits']
(W/'memory_allocation.json').write_text(json.dumps(dict(source=hashes[sources[0]],policy='ASSUMED independent single-port depth banking preserving byte lanes; homogeneous best of real 64/128/256/512x8 LEFs per declaration instance. No sharing across arrays. Multidimensional arrays flattened. Ports/simultaneous access not proven. Research banks capacity-rounded per instance; dense effective density assumption.',arrays=allocation),indent=2))
dff=float(re.search(r'cell\s*\(gf180mcu_fd_sc_mcu7t5v0__dffq_1\).*?area\s*:\s*([\d.]+)',next((W/'pdk').glob('*3v30.lib')).read_text(),re.S)[1])
blocks=[]
def add(name,group,sel=0,rom=0,logic=0,power=0,source='',status='',**kw):
 blocks.append(dict(name=name,partition=group,selections=sel,rom_bytes=rom,logic_area_mm2=logic,power_w=power,source=source,area_status=status,power_status='ASSUMED load, not measured recognizer activity',**kw))
add('frontend_FP32','encoder',rom=8298240,logic=12,power=.15,source=sources[0],status='MEASURED coefficient count; ASSUMED binary ROM1.76um2/bit x1.25 and12mm2 frontend logic')
# Each matrix group remains separate. Power falls back to prior explicit assumption: W5 full-row energy null.
for group,count,n in [('encoder',1228800,6),('decoder',1843200,6)]:
 for i in range(n):add(f'{group}_fabric_L{i}',group,sel=count,power=.025,source=sources[4]+' and current model ledger',status='MEASURED selection count x measured partial geometry; transfer/padding across all shapes ASSUMED')
add('embedding_head_tied_once','decoder',sel=10485760,power=.08,source='current model ledger; '+sources[4],status='MEASURED count; ASSUMED transfer of projection-bank geometry to tied/transposed head access')
add('producer_KV_and_positions','encoder',sel=2539520,power=.04,source='current model ledger',status='MEASURED count; geometry transfer ASSUMED')
# K64 domain has 16 UINT8 representatives per64 weights; all slots reserved, actual used book count may be smaller.
books=31457280//64*16
metadata=sum(a['total_bytes'] for a in inv['all_rom_arrays'] if a['var'].endswith('_meta')) + 61440 + (inv['totals']['rom_case_lut_bytes']-inv['totals']['rom_case_lut_big5_bytes'])
add('codebooks_and_other_metadata','decoder',rom=books+metadata,power=.035,source=sources[0]+'; K64 domain count',status='MEASURED K64 slots and native metadata totals; ASSUMED binary ROM density; engine embedded books retained as conservative cache duplication',book_bytes=books,metadata_bytes=metadata)
# Engine plus unmeasured dynamic/front/control logic: remove projection duplication from old fixed datapath budgets.
add('shared_product_engine','shared',logic=foot,power=.15,source=sources[3],status=cfg['engine_model']['footprint_status'],replicate_per_die=True)
for name,group,area,power in [('encoder_dynamic_attention','encoder',18,.075),('decoder_dynamic_attention','decoder',15,.06),('producer_dynamic','encoder',6,.03),('control_clock_IO_interface','decoder',12,.06)]:
 add(name,group,logic=area,power=power,source='W3 explicit allowance; no full-top mapped logic evidence',status='ASSUMED dynamic-only logic allowance; fixed projection replaced by shared engine')
# October digital periphery terms excluding receiver strips; transfer is an assumption, no duplicate readout area.
peri=25.002+30.369+.269+.944
add('array_decoder_phase_mux_allowance','balanced',logic=peri,power=.02,source='docs/TAALAS-TALL-BANK-BUDGET.md',status='ASSUMED transfer of October placed-footprint estimates; omits receiver strips already in W5 array. Not complete macro bound')
# Exact inventory, initially whole-module grouping then balanced across dies by capacity. Registers counted separately.
memareas={k:sum(x[k] for x in allocation)*1.1 for k in ['open_area_mm2','research_area_mm2','dense_area_mm2']}
add('mutable_arrays','balanced',power=.06,source=sources[0]+'; memory_allocation.json; SRAM LEFs',status='MEASURED inventory/LEF x ASSUMED banking and10% internal placement allowance',memory_area_by_scenario=dict(zip(['sram_open_macro','sram_4k_research','sram_dense_custom'],memareas.values())),mutable_bits=inv['totals']['mutable_array_bits'],memory_area_levers_on={m:sum(a[k] for a in allocation)*1.1 for m,k in zip(['sram_open_macro','sram_4k_research','sram_dense_custom'],['kv8_open_area_mm2','kv8_research_area_mm2','kv8_dense_area_mm2'])})
add('ordinary_registers','balanced',logic=inv['totals']['register_bits']*dff/.5/1e6,power=.02,source=sources[0]+'; gf180mcu7t dffq_1 Liberty area',status='MEASURED bit count/63.6608um2 DFF; ASSUMED50% utilization. Conservative duplication versus engine/control internals not subtracted')
cfg['blocks']=blocks;cfg['inventory_totals']=inv['totals'];cfg['books_bytes']=books;cfg['metadata_bytes']=metadata;cfg['array_timing_snapshot']=timing;cfg['power_basis']='All per-block watts ASSUMED. W5 full320lane energy null and selected group is partial16columns plus128receivers; no full-array scaling claimed. W2b workload power unannotated; default7.32749W is not a qualified load. No sub-watt claim.'
cfg['selected_scenario']='measured320';cfg['memory_allocation_summary']=dict(array_count=len(allocation),instances=sum(a['instances'] for a in allocation),macro_count=sum(a['macro_count'] for a in allocation),allocated_bytes=sum(a['allocated_bytes'] for a in allocation),areas_with_10pct=memareas,dff_cell_um2=dff)
(W/'blocks_measured.json').write_text(json.dumps(cfg,indent=2)+'\n')
(W/'blocks.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('W3-STATUS: measured inputs frozen',stamp,'memory',cfg['memory_allocation_summary'],'engine',cfg['engine_model'])
