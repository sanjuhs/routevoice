"""Explicit scenario accounting; geometric screens are not implementation measurements."""
import math,copy

def configure(cfg,memory='sram_open_macro',levers='off',state='baseline'):
 cfg=copy.deepcopy(cfg);cfg.update(memory_scenario=memory,levers=levers,state_profile=state)
 if state=='conservative':cfg['blocks']+=cfg.get('conservative_only_blocks',[])
 for b in cfg['blocks']:
  if levers=='lossless' and b['name'] in ('frontend_FP32','frontend_native_int8_lossless'):
   b['rom_bytes']=2090240
   b['numerical_change']='NONE: source-native affine INT8 with separate FP32 multiply/add rounding'
  if levers=='on':
   if b['name']=='frontend_FP32':b['rom_bytes']=2074560;b['numerical_change']='frontend_int8: requires model-accuracy re-validation'
   if b['name']=='KV_retention_reserve':b['sram_bytes']=math.ceil(b['sram_bytes']/4);b['numerical_change']='kv8: requires model-accuracy re-validation'
 return cfg

def block_area(cfg,b,selection):
 s=cfg['scenarios'][selection];sel=b['selections']*s['selection_um2']*s['periphery_factor']/1e6
 rombytes=b['rom_bytes'];books=0
 if b['name']=='codebooks_and_other_metadata' and cfg.get('levers') in ('on','books','lossless'):
  nb=b.get('book_bytes',7864320)
  books=nb*8*s['selection_um2']/4*s['periphery_factor']/1e6;rombytes-=nb
 rom=rombytes*8*cfg['binary_rom_um2_per_bit']*cfg['binary_rom_periphery_factor']/1e6+books
 mem=cfg['memory_scenarios'][cfg.get('memory_scenario','sram_open_macro')]
 sram=math.ceil(b.get('sram_bytes',0)/mem['bank_bytes'])*mem['bank_area_mm2']*cfg['sram_packing_overhead']
 if 'memory_area_by_scenario' in b:
  key='memory_area_levers_on' if cfg.get('levers')=='on' and 'memory_area_levers_on' in b else 'memory_area_by_scenario'
  sram=b[key][cfg.get('memory_scenario','sram_open_macro')]
 logic=b['logic_area_mm2']
 if cfg.get('levers') in ('on','books','lossless'):logic+=b.get('array_book_extra_logic_mm2',0)
 return dict(selection_mm2=sel,rom_mm2=rom,sram_mm2=sram,logic_mm2=logic,total_mm2=sel+rom+sram+logic)
