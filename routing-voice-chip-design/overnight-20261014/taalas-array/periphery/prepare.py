from pathlib import Path
import json
P=Path(__file__).resolve().parent
R=P.parents[2]
prefix='gf180mcu_fd_sc_mcu7t5v0__'
lines=['module w5_row_decoder(input wire enable,input wire [5:0] row,output wire [63:0] wordline);','wire [63:0] decoded;']
for i in range(64):
 lines += [f"assign decoded[{i}]=enable && row==6'd{i};", f'{prefix}buf_4 drv_{i}(.I(decoded[{i}]),.Z(wordline[{i}]));']
lines+=['endmodule']
(P/'decoder.v').write_text('\n'.join(lines)+'\n')
base=json.loads((R/'overnight-20261014/fabric-k64/configs/array_port.json').read_text())
base.update(DESIGN_NAME='w5_row_decoder',VERILOG_FILES=[str(P/'decoder.v')],VERILOG_INCLUDE_DIRS=[],CLOCK_PORT=None,CLOCK_NET=None,RUN_CTS=False,FP_SIZING='absolute',DIE_AREA=[0,0,120,120],CORE_AREA=[10,10,110,110],DRT_THREADS=1,STA_THREADS=1,PL_TARGET_DENSITY_PCT=45,RUN_MCSTA=False,RUN_SPEF_EXTRACTION=True,SYNTH_CAP_LOAD=100,RUN_IRDROP_REPORT=False)
(P/'decoder.json').write_text(json.dumps(base,indent=2)+'\n')
