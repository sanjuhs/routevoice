"""Derive engine_local_pipe2.sv from engine_local.sv (lead, 23 Oct 2026).
Splits the 320:1 output select: each 32-lane group registers its lane for the NEXT column (look-ahead),
and the zero-point correction is registered the same way. One PREP state after the last ACCUM fills the
registers for column 0, so each vector takes one more cycle; throughput in OUTPUT stays one column/cycle."""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)
rep("localparam IDLE=3'd0, LOAD=3'd1, INDEX=3'd2, ACCUM=3'd3, OUTPUT=3'd4;",
    "localparam IDLE=3'd0, LOAD=3'd1, INDEX=3'd2, ACCUM=3'd3, OUTPUT=3'd4, PREP=3'd5;")
rep("wire signed [31:0] correction=activation_sum*$signed({24'b0,zero_point});",
    "wire signed [31:0] correction=activation_sum*$signed({24'b0,zero_point});\n"
    "// look-ahead column: the column OUTPUT will present after this clock edge\n"
    "wire [8:0] look_column=(state==OUTPUT&&out_ready)?column+1'b1:column;\n"
    "reg signed [26:0] group_lane [0:9];\n"
    "reg signed [31:0] correction_q;\n"
    "reg signed [26:0] selected_accum;\n"
    "always @* begin selected_accum=group_lane[0]; case(column[8:5])\n"
    + "".join(f"  4'd{g}: selected_accum=group_lane[{g}];\n" for g in range(10)) +
    " default: selected_accum=group_lane[0]; endcase end\n"
    "always @(posedge clk) begin : output_lookahead\n"
    " integer g;\n"
    " if(reset) begin for(g=0;g<10;g=g+1) group_lane[g]<=0; correction_q<=0; end\n"
    " else if(state==PREP||state==OUTPUT) begin\n"
    "  for(g=0;g<10;g=g+1) group_lane[g]<=accum[g*32+look_column[4:0]];\n"
    "  correction_q<=correction;\n"
    " end\n"
    "end")
rep("assign out_data=$signed(accum[column])-correction;",
    "assign out_data=$signed(selected_accum)-correction_q;")
# zero_point ROM is indexed by the look-ahead column so correction_q matches the presented column
rep(" zero_point=0;\n case(column)", " zero_point=0;\n case(look_column)")
rep("if(row==11'd1279) begin column<=0;state<=OUTPUT;end",
    "if(row==11'd1279) begin column<=0;state<=PREP;end")
rep(" OUTPUT: if(out_ready) begin", " PREP: state<=OUTPUT;\n OUTPUT: if(out_ready) begin")
open(dst, "w").write(s)
