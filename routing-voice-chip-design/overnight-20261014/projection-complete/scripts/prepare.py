from pathlib import Path
import json, hashlib, numpy as np
R=Path.cwd(); W=R/'overnight-20261014/projection-complete'; S=R/'overnight-20261014/fabric-k64'
idxpath=R/'overnight-20261014/taalas-array/indices.npy'
a=np.load(idxpath); assert a.shape==(1280,320) and a.max()<16
(W/'vectors/rows.hex').write_text(''.join(''.join(format(int(x),'x') for x in row[::-1])+'\n' for row in a))
ident=json.loads((S/'evidence/identity.json').read_text()); assert hashlib.sha256(a.astype(np.uint8).tobytes()).hexdigest()==ident['indices_unpacked_sha256']
(W/'evidence/identity.json').write_text(json.dumps(dict(w2b_identity=ident,w6_indices_file_sha256=hashlib.sha256(idxpath.read_bytes()).hexdigest(),real_image_equal=True),indent=2)+'\n')
ports=['input wire PC']+[f'input wire WL{i}' for i in range(1280)]+[f'output wire OUT{i}' for i in range(1280)]
connections=['.PC(pc)']+[f'.WL{i}(wordline[{i}])' for i in range(1280)]+[f'.OUT{i}(array_out[{i}])' for i in range(1280)]
(W/'rtl/rv_k64_projection_complete.sv').write_text('''// W8 proposed guarded protocol, 20ns clock. All arithmetic remains W2b RTL.
// The sampled W6 60ns waveform is NOT claimed reproduced by these full-cycle phases.
module rv_k64_projection_complete(input wire clk,reset,start,step_enable,
input wire signed [8:0] in_data,input wire in_valid,output wire in_ready,
input wire [31:0] activation_scale,output wire busy,out_valid,input wire out_ready,
output wire [31:0] out_data,output wire [8:0] out_column,output wire [4:0] exceptions);
localparam IDLE=3'd0, PRE=3'd1, GUARD=3'd2, EVAL1=3'd3, EVAL2=3'd4, HOLD=3'd5, RELEASE=3'd6, DONE=3'd7;
reg [2:0] phase;
reg [10:0] read_row;
reg [1279:0] frozen_index_bits;
wire [1279:0] array_out;
wire [10:0] array_row;
wire array_read_enable;
wire engine_in_ready;
wire engine_in_valid = in_valid && phase==IDLE;
assign in_ready = engine_in_ready && phase==IDLE;
wire engine_step = step_enable && (phase==IDLE || phase==DONE);
wire pc;
wire pc_logic = (phase==GUARD || phase==EVAL1 || phase==EVAL2 || phase==HOLD || phase==RELEASE);
wire evaluate = (phase==EVAL1 || phase==EVAL2 || phase==HOLD) && !reset;
wire [1279:0] wordline;
(* keep *) gf180mcu_fd_sc_mcu7t5v0__buf_20 precharge_driver(.I(pc_logic),.Z(pc));
genvar r;
generate for(r=0;r<1280;r=r+1)begin: decoder
 wire selected = evaluate && read_row==r;
 (* keep *) gf180mcu_fd_sc_mcu7t5v0__buf_20 wordline_driver(.I(selected),.Z(wordline[r]));
end endgenerate
rv_k64_array_port engine(.clk(clk),.reset(reset),.start(start),.step_enable(engine_step),
.in_data(in_data),.in_valid(engine_in_valid),.in_ready(engine_in_ready),.activation_scale(activation_scale),
.busy(busy),.out_valid(out_valid),.out_ready(out_ready),.out_data(out_data),
.out_column(out_column),.exceptions(exceptions),.array_row(array_row),
.array_read_enable(array_read_enable),.frozen_index_bits(frozen_index_bits));
always @(posedge clk)begin
 if(reset)begin phase<=RELEASE;read_row<=0;frozen_index_bits<=0;end
 else case(phase)
 IDLE: if(in_valid&&in_ready)begin read_row<=array_row;phase<=PRE;end
 PRE: phase<=GUARD;
 GUARD: phase<=EVAL1;
 EVAL1: phase<=EVAL2;
 EVAL2: begin frozen_index_bits<=array_out;phase<=HOLD;end
 HOLD: phase<=RELEASE;
 RELEASE: phase<=DONE;
 DONE: if(engine_in_ready || !busy || array_read_enable)phase<=IDLE;
 default: phase<=IDLE;
 endcase
end
PITCH_BANK_R1280 bank(
'''+',\n'.join(connections)+');\nendmodule\n')
# Behavioral bank retains real frozen image; fixed delay is from sampled SS result rounded up.
# No functional connection to engine row: decode is checked from actual physical WL pins.
(W/'tb/bank_model.sv').write_text('''`timescale 1ns/1ps
module PITCH_BANK_R1280(
'''+',\n'.join(ports)+''');
wire [1279:0] wl = {'''+','.join(f'WL{i}' for i in reversed(range(1280)))+'''};
reg [1279:0] rows[0:1279];
reg [1279:0] result=0;
integer n,selected,count;
time last_pc_rise=0,last_wl_fall=0,last_wl_rise=0;
initial $readmemh("'''+str(W/'vectors/rows.hex')+'''",rows);
assign {'''+','.join(f'OUT{i}' for i in reversed(range(1280)))+'''}=result;
always @(posedge PC) last_pc_rise=$time;
always @(negedge PC)begin
 if(wl!==1280'b0)$fatal(1,"precharge/wordline overlap");
 if(last_wl_fall && $time-last_wl_fall<2)$fatal(1,"WL-off guard too short");
 result<=0;
end
always @(wl)begin
 count=0;selected=0;
 for(n=0;n<1280;n=n+1)if(wl[n])begin count=count+1;selected=n;end
 if(count>1)$fatal(1,"multiple selected wordlines");
 if(count==1)begin
  if(!PC)$fatal(1,"WL during precharge");
  if($time-last_pc_rise<4)$fatal(1,"PC-off guard too short");
  if(last_wl_rise && $time-last_wl_rise<60)$fatal(1,"reuse shorter than sampled protocol");
  last_wl_rise=$time;
  result<=#24 rows[selected];
 end else last_wl_fall=$time;
end
endmodule
''')
tb=(S/'tb/array_port.sv').read_text().replace('rv_k64_array_port dut(.*);','rv_k64_projection_complete dut(.*);\nassign array_read_enable=dut.array_read_enable;')
tb=tb.replace('taalas_index_fabric fabric(.row(array_row),.read_enable(array_read_enable),.frozen_index_bits(frozen_index_bits));','')
tb=tb.replace('dut.projection','dut.engine.projection').replace('dut.metadata_column','dut.engine.metadata_column')
tb=tb.replace('elapsed!=4163','elapsed!=11843').replace('expected4163cycles','expected11843cycles').replace('unstalled_cycles=4163','unstalled_cycles=11843')
tb=tb.replace(' for(v=0;v<54;v=v+1)begin', " // Abort at every physical controller phase; reset drains WL before PC falls.\n for(s=1;s<=7;s=s+1)begin\n  @(negedge clk);start=1;step_enable=1;tick;\n  @(negedge clk);start=0;in_valid=1;in_data=9'sd255;\n  while(dut.phase!=s)begin tick;@(negedge clk);end\n  clear_reset;\n end\n for(v=0;v<54;v=v+1)begin").replace('aborts=4','aborts=11')
tb=tb.replace('module tb;', 'module tb;\ninitial begin #40000000; $fatal(1,\"whole-suite watchdog\"); end')
(W/'tb/complete.sv').write_text(tb)
config=json.loads((S/'configs/array_port.json').read_text())
cells=S/'pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog'
files=[str(cells/'primitives.v'),str(cells/'gf180mcu_fd_sc_mcu7t5v0.v')]+config['VERILOG_FILES']+[str(W/'rtl/rv_k64_projection_complete.sv'),str(W/'tb/bank_model.sv'),str(W/'tb/complete.sv')]
(W/'configs/sim-files.f').write_text('\n'.join(files)+'\n')
(W/'evidence/source-reading.md').write_text('Read repository skill, complete source-notes, atlas, architecture-and-numerics, implementation-workflow, root ../plan.md and approved physical proposal. Relevant primary P1 Fig4/readable-cell/shared-products/serial control and claims, P2 stored-address/connectivity alternatives and claims, P3 mask connections/serial transport/read cycle read from retained primary texts in experiments/common-v9-start-handoff-source-20261004-v1/reading-basis-v2. The 13 October pause is superseded by the explicit W8 user instruction. W6 uses four access devices per four-bit immutable selection, with shared products downstream.\n')
print('real W6 indices match W2b identity; generated wrapper and delayed behavioral model')
