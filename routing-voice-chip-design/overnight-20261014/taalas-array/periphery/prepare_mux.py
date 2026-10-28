from pathlib import Path
import json
P=Path(__file__).resolve().parent
lines=['module w5_bank_mux128(input wire enable,input wire [4:0] bank,input wire [2559:0] bank_data,output reg [127:0] index_bits);','always @* begin','index_bits=0;','if(enable) case(bank)']
lines += [f"5'd{i}: index_bits=bank_data[{128*i} +: 128];" for i in range(20)]
lines += ['endcase','end','endmodule']
(P/'mux128.v').write_text('\n'.join(lines)+'\n')
c=json.loads((P/'decoder.json').read_text())
c.update(DESIGN_NAME='w5_bank_mux128',VERILOG_FILES=[str(P/'mux128.v')],DIE_AREA=[0,0,450,450],CORE_AREA=[10,10,440,440],IO_PIN_H_THICKNESS_MULT=1,IO_PIN_V_THICKNESS_MULT=1,IO_PIN_MIN_DISTANCE=0.56,SYNTH_CAP_LOAD=10)
(P/'mux128.json').write_text(json.dumps(c,indent=2)+'\n')
