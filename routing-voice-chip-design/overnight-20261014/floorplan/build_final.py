#!/usr/bin/env python3
"""Final lossless-frontend + measured-bitcell scenario, with immutable input receipts."""
import json,hashlib,datetime,math,copy
from pathlib import Path
W=Path(__file__).resolve().parent;R=W.parent.parent
cfg=json.loads((W/'pre_lossless_blocks_credible.json').read_text());stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');snap=W/'inputs'/('final-'+stamp);snap.mkdir();paths=['overnight-20261014/accuracy-int8/RESULTS.md','overnight-20261014/accuracy-int8/existing-affine-int8-exact/manifest.json','overnight-20261014/taalas-pitch/results.json','overnight-20261014/taalas-pitch/RESULTS.md','overnight-20261014/storage-inventory/inventory.json','overnight-20261014/fabric-k64/results.json','overnight-20261014/floorplan/sram_bitcell_measurement.json'];hashes={};data={}
for s in paths:
 raw=(R/s).read_bytes();dest=snap/s;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);hashes[s]=dict(sha256=hashlib.sha256(raw).hexdigest(),snapshot=str(dest.relative_to(W)))
 if s.endswith('.json'):data[s]=json.loads(raw)
aff=data[paths[1]];files=[f for r in aff['records'] for f in r['files']]+aff['unchanged_bias_files'];payload_audit=[]
for f in files:
 p=Path(f['path']);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==f['sha256'] and p.stat().st_size==f['bytes'];payload_audit.append(dict(path=str(p),sha256=h,bytes=p.stat().st_size,verified=True))
assert sum(f['bytes'] for f in files)==2090240 and all(r['matches_all_ROM_bits'] for r in aff['records'])
(W/'lossless_payload_audit.json').write_text(json.dumps(dict(manifest_sha256=hashes[paths[1]]['sha256'],files=payload_audit,total_bytes=sum(f['bytes'] for f in files),bit_exact_claim_source='lead-verified source manifest; W3 independently checked all payload sizes/hashes',decode_contract=aff['decode_contract']),indent=2)+'\n')
pitch=data[paths[2]];density=pitch['area']['um2_per_selection_including_analog_readout'];engine=data[paths[5]]['variants']['array_port'];ef=engine.get('routed_area_mm2') or engine['synthesis']['cell_area_mm2']/.5
assert math.isclose(ef,cfg['engine_model']['footprint_mm2']), 'W2b engine footprint changed; update engine and all physical cases'
inv=data[paths[4]];assert inv['totals']['mutable_array_bits']==8501818
cfg.update(scope='Final conditional lossless-frontend floorplan; native affine decode unimplemented and physical macro integration/power unqualified',scenarios=dict(final_pitch=dict(selection_um2=density,periphery_factor=1,status='MEASURED W6 GDS footprint incl analog readout; scope/status in final_array_verification')),selected_scenario='final_pitch',final_snapshot_utc=stamp,final_source_hashes=hashes,final_array_verification={str(k):{q:z for q,z in v.items() if q!='geometry'} for k,v in pitch['layouts'].items()},final_array_timing=pitch['timing'],final_array_missing=pitch['missing'],frontend_native_int8_lossless=dict(bytes=2090240,int8_bytes=2073600,scale_offset_bytes=12800,bias_bytes=3840,coefficients=2074560,numerical_change=False,decode_contract=aff['decode_contract'],fp32_multiply_add_resources=1,resource_area_source='Reused within existing12mm2 ASSUMED frontend logic allowance; one FMA-class resource executes separate rounded multiply then add, not one fused operation',hardware_status='not implemented/timed; two dependent rounded operations per decoded weight'),levers_definition=dict(lossless='frontend_native_int8_lossless + books_in_array; original mutable state; no numerical change; noKV8/dedup'))
cfg['source_hashes'].update(hashes)
effective=17.8/.70
cfg['memory_scenarios']['sram_bitcell_large_macro']=dict(bank_bytes=1,bank_area_mm2=8*effective/1e6,um2_per_bit=effective,measured_bit_pitch_um2=17.8,array_efficiency=.70,status='bit cell MEASURED;70% array efficiency ASSUMED; no implemented large macro; additional10% bank-group placement retained',source='sram_bitcell_measurement.json')
cfg['memory_scenarios']['sram_dense_custom']['status']='ASSUMED12um2/bit effective; requires a smaller foundry bit cell than the open GF180 one; no compiled macro'
for b in cfg['blocks']:
 if b['name']=='frontend_FP32':
  b['name']='frontend_native_int8_lossless';b['rom_bytes']=2090240;b['source']=paths[1];b['area_status']='MEASURED payload2090240B; ASSUMED binary ROM1.76um2/bit x1.25;12mm2 frontend logic retains one separately-rounded FP32 multiply-add resource'
 if b['selections']:b['source']=paths[2]+'; frozen selection counts'
 if b['name']=='mutable_arrays':
  b['memory_area_by_scenario']['sram_bitcell_large_macro']=b['mutable_bits']*effective/1e6*1.1
  b['memory_area_levers_on']=copy.deepcopy(b['memory_area_by_scenario'])
cfg['power_basis']='Unchanged assumed1.08W whole, no measured new decode power. Decode resource included within assumed frontend0.15W. Full-row W6 energy and W2b annotated workload power unavailable.'
(W/'blocks_final.json').write_text(json.dumps(cfg,indent=2)+'\n');(snap/'hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('W3-STATUS: final inputs hashed',stamp,'lossless payload2090240B; SRAM effective',effective,'um2/bit; W6',density)
