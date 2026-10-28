from pathlib import Path
import json
root=Path(__file__).resolve().parent
for name in ['rv_fixed_proj320_rom','rv_fixed_proj320_dp','rv_fixed_proj64x320_rom']:
    cfg={'DESIGN_NAME':name,'VERILOG_FILES':[str(root/'rtl'/f'{name}.sv')],
        'CLOCK_PORT':'clk','CLOCK_PERIOD':20.0,'FP_CORE_UTIL':45,'PL_TARGET_DENSITY_PCT':50,
        'DRT_THREADS':8,'STA_THREADS':2,'RUN_MAGIC_DRC':True,'RUN_KLAYOUT_DRC':True,
        'RUN_LVS':True,'RUN_CTS':True,'RUN_DRT':True,'RUN_FILL_INSERTION':True,
        'RUN_MCSTA':True,'RUN_SPEF_EXTRACTION':True,'RUN_ANTENNA_REPAIR':True}
    if name == 'rv_fixed_proj320_dp':
        cfg.update(DEDUPLICATE_CORNERS=True,IO_PIN_H_LAYER='Metal1 Metal3 Metal5',IO_PIN_V_LAYER='Metal2 Metal4',IO_PIN_MIN_DISTANCE=0.56,IO_PIN_MIN_DISTANCE_IN_TRACKS=False,IO_PIN_H_THICKNESS_MULT=1,IO_PIN_V_THICKNESS_MULT=1)
    if name in ['rv_fixed_proj64x320_rom','rv_fixed_proj320_dp']:
        cfg.update(FP_CORE_UTIL=30,PL_TARGET_DENSITY_PCT=55,PL_MAX_DISPLACEMENT_X=1500,PL_MAX_DISPLACEMENT_Y=800)
    (root/'configs'/f'{name}.json').write_text(json.dumps(cfg,indent=2)+'\n')
