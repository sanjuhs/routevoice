from pathlib import Path
import subprocess,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2]
lib=R/'pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog';T='/nix/store/yczxlrrywxp7q2aavm4b3zrj3lpmq18a-devshell-dir/bin/'
(P/'latch_tb.v').write_text('''`timescale 1ns/1ps
module tb;
reg capture_gate=0;reg[127:0] index_in=0;wire[127:0] index_out;
reg[127:0] held;integer i,r,k;integer checks=0;
w5_latch128 dut(.*);
task check_value(input[127:0] expected);begin #1;if(index_out!==expected)$fatal(1,"latch mismatch gate=%b",capture_gate);checks=checks+1;end endtask
initial begin
// Startup has no reset; obtain defined data through actual transparency.
index_in=128'h0123456789abcdef0011223344556677;capture_gate=1;check_value(index_in);
// Change data twice during the SAME open gate: edge-triggered substitution fails.
index_in=~index_in;check_value(index_in);index_in=0;check_value(index_in);
for(i=0;i<128;i=i+1)begin
index_in=128'b1<<i;check_value(index_in);index_in=~index_in;check_value(index_in);
held=index_in;capture_gate=0;#1;index_in=0;check_value(held);index_in=~128'b0;check_value(held);
capture_gate=1;check_value(index_in);
end
for(r=0;r<128;r=r+1)begin
for(k=0;k<4;k=k+1)index_in[k*32+:32]=$random;check_value(index_in);
held=index_in;capture_gate=0;#1;
for(i=0;i<4;i=i+1)begin for(k=0;k<4;k=k+1)index_in[k*32+:32]=$random;check_value(held);end
capture_gate=1;check_value(index_in);
end
$display("PASS latch transparent/hold checks=%0d all128bits,128randomcaptures,no reset assumption",checks);$finish;end
endmodule
''')
net=P/'runs/latch128b-v1/final/nl/w5_latch128.nl.v';tb=P/'latch_tb.v';exe=P/'latch.sim'
cmd=[T+'iverilog','-g2012','-DFUNCTIONAL','-s','tb','-o',str(exe),str(tb),str(net),str(lib/'gf180mcu_fd_sc_mcu7t5v0.v'),str(lib/'primitives.v')]
c=subprocess.run(cmd,capture_output=True,text=True);(P/'latch-compile.log').write_text(c.stdout+c.stderr);c.check_returncode()
c=subprocess.run([T+'vvp',str(exe)],capture_output=True,text=True);(P/'latch-functional.log').write_text(c.stdout+c.stderr);c.check_returncode();print(c.stdout)
(P/'latch-functional.json').write_text(json.dumps(dict(command=cmd,stdout=c.stdout,scope='Routed gate-netlist zero-delay functional behavior; not analog pulse/setup/hold qualification',netlist_sha256=hashlib.sha256(net.read_bytes()).hexdigest(),testbench_sha256=hashlib.sha256(tb.read_bytes()).hexdigest()),indent=2)+'\n')
