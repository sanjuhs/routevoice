#!/usr/bin/env python3
import json, math, re, hashlib
from pathlib import Path
W=Path(__file__).resolve().parent; R=W.parent.parent
ledger_path=R/'experiments/chip-integration-20261012-current-learned-fulltables-service-ledger-v2/ledger.json'
j=json.loads(ledger_path.read_text()); source=str(ledger_path.relative_to(R))
lefs=[]
for p in sorted((W/'pdk').glob('*sram*.lef')):
 t=p.read_text(); x,y=map(float,re.search(r'SIZE ([\d.]+) BY ([\d.]+)',t).groups()); n=int(re.search(r'sram(\d+)x8',p.name)[1]); lefs.append(dict(name=p.stem,bytes=n,width_um=x,height_um=y,area_mm2=x*y/1e6,source=str(p.relative_to(W))))
sram=min(lefs,key=lambda x:x['area_mm2']/x['bytes'])
blocks=[]
def add(name,selections=0,rom_bytes=0,logic=0,power=.02,**kw):
 blocks.append(dict(name=name,selections=selections,rom_bytes=rom_bytes,logic_area_mm2=logic,power_w=power,power_status='assumed simultaneous static load; not activity-based recognizer power',source=source,**kw))
add('frontend_FP32',rom_bytes=8298240,logic=12,power=.15,note='All native FP32 bytes from ledger; no INT4 substitution. 12 mm2 logic allowance assumed.')
for l in range(6): add(f'encoder_fabric_L{l}',selections=1228800,power=.025,note='4*320*320 + 2*320*1280 selections per layer; datapath separate')
add('encoder_datapath_attention',logic=30,power=.12,note='Assumed aggregate area for shared products, accumulators, FP32 and dynamic attention')
for l in range(6): add(f'decoder_fabric_L{l}',selections=1843200,power=.025,note='Self 4*320*320 + cross Q/O 2*320*320 + FF 3*320*1280')
add('decoder_datapath',logic=25,power=.1,note='Assumed aggregate arithmetic area, including head datapath')
add('embedding_head_tied_once',selections=10485760,power=.07,note='Tied table counted once, ledger indices 5242880 bytes*2')
add('producer_KV_and_positions',selections=1228800+1310720,rom_bytes=30720,logic=6,power=.045,note='Producer K/V 6*2*320*320; positional 1310720 selections; padded metadata30720 bytes; assumed logic')
add('codebooks_and_other_metadata',rom_bytes=7864320+400000,power=.035,note='7,864,320 B lane-major book payload from docs/TAALAS-BOOK-PAGE-CACHE.md; additional400000 B scalar metadata allowance. Physical compression not credited.')
for v in j['mutable_backends']:
 b=sum(math.ceil(a['bytes']/512)*512 for a in v['arrays']); add(re.sub(r'\W+','_',v['name']),power=.015,sram_bytes=b,logical_bytes=v['bytes'],note='Each declared bank rounded independently to real 512x8 SRAM')
add('frontend_mutable',power=.01,sram_bytes=81920,logical_bytes=81920)
add('book_cache',power=.005,sram_bytes=9216,logical_bytes=9216)
add('KV_retention_reserve',power=.035,sram_bytes=6*2*64*320*4,logical_bytes=6*2*64*320*4,note='Explicit assumed all-layer FP32 K/V retention at F64. Current streaming regeneration may need less; not a ledger measurement.')
add('private_state_reserve',power=.035,sram_bytes=524288,logical_bytes=524288,note='Assumed512KiB additional private state pending full-top Yosys memory inventory; completeness unknown')
add('control_clock_IO_interface',logic=12,power=.05,note='Assumed12mm2 digital control/clock/interface; physical IO cells outside this allowance')
assert sum(b['selections'] for b in blocks)==31457280
out=dict(schema_version=1,scope='F64/history66 conditional complete-block floorplan; internal macro layouts and full memory completeness unproved',vdd=3.3,standard_cell_corner='gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30',sram_macros=lefs,selected_sram=sram,sram_packing_overhead=1.10,binary_rom_um2_per_bit=1.76,binary_rom_status='ASSUMED 7.04/4; not a characterized binary ROM',binary_rom_periphery_factor=1.25,macro_halo_um=30,maximum_tile_area_mm2=9,pad_current_budget_a=.025,pad_current_status='ASSUMED25mA per supply pad; no package/ESD/EM qualification',pad_current_margin=2,scenarios={'stdcell':dict(selection_um2=40,periphery_factor=1.0,status='PLACEHOLDER40um2/selection pending W2/W2b'), 'custom7':dict(selection_um2=7.04,periphery_factor=1.25,status='USER SCENARIO historical partial density plus assumed25% periphery'), 'optimistic3_5':dict(selection_um2=3.5,periphery_factor=1.25,status='OPTIMISTIC ASSUMPTION; no measured macro')},blocks=blocks,ledger_sha256=hashlib.sha256(ledger_path.read_bytes()).hexdigest())
out['conservative_only_blocks']=[b for b in out['blocks'] if b['name'] in ('KV_retention_reserve','private_state_reserve')]
out['blocks']=[b for b in out['blocks'] if b['name'] not in ('KV_retention_reserve','private_state_reserve')]
out['memory_scenarios']={
 'sram_open_macro':dict(bank_bytes=512,bank_area_mm2=sram['area_mm2'],status='MEASURED-LEF; 51.123114453125 um2/bit before group packing',source=sram['source']),
 'sram_4k_research':dict(bank_bytes=4096,bank_area_mm2=.9479839488,status='PROJECT RESEARCH BANK footprint; transfer to current memory ports unproved',source='docs/TAALAS-DIE-SIZE-AND-SYSTEM-COSTS-2026-10-02.md'),
 'sram_dense_custom':dict(bank_bytes=512,bank_area_mm2=512*8*12/1e6,status='ASSUMED effective12um2/bit including about40% periphery; compiled macro required',source='Lead guidance1 2026-10-14')}
out['design_levers']={'frontend_int8':'2,074,560 coefficients; FP32 to INT8, requires model-accuracy re-validation','books_in_array':'book payload encoded using selection density/4 per bit plus same periphery; array port/timing design required; unchanged values','kv8':'Only explicitly identified FP32 KV retention is reduced4x. No KV reserve in baseline; no saving credited until inventory classifies real KV. Requires model-accuracy re-validation.'}
out['baseline_memory_scope']='Only ledger banks, frontend mutable and book cache. Missing private/KV state pending full-top Yosys inventory; NOT complete recognizer capacity.'
(W/'blocks.json').write_text(json.dumps(out,indent=2)+'\n')
print('W3-STATUS: blocks.json written; selections',sum(b['selections'] for b in blocks),'SRAM bytes',sum(b.get('sram_bytes',0) for b in blocks),'SRAM area/512B',sram['area_mm2'])
