from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent;R=P.parents[2]
lib=R/'pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/verilog'
T='/nix/store/yczxlrrywxp7q2aavm4b3zrj3lpmq18a-devshell-dir/bin/'
(P/'decoder_tb.v').write_text('''module tb;
reg enable=0;reg[5:0] row=0;wire[63:0] wordline;integer i;
w5_row_decoder dut(.*);
initial begin
for(i=0;i<64;i=i+1)begin row=i;enable=1;#1;if(wordline!==(64'b1<<i))$fatal(1,"row %d",i);enable=0;#1;if(wordline!==0)$fatal(1,"disabled row %d",i);end
$display("PASS 64 rows,64 disabled checks");$finish;end
endmodule
''')
(P/'mux128_tb.v').write_text('''module tb;
reg enable=0;reg[4:0] bank=0;reg[2559:0] bank_data=0;wire[127:0] index_bits;
integer b,k,r,i;reg[127:0] expected;
w5_bank_mux128 dut(.*);
initial begin
for(r=0;r<8;r=r+1)begin
for(i=0;i<80;i=i+1)bank_data[i*32+:32]=$random;
for(b=0;b<32;b=b+1)begin bank=b;enable=1;#1;expected=b<20?bank_data[b*128+:128]:128'b0;if(index_bits!==expected)$fatal(1,"bank %d round %d",b,r);enable=0;#1;if(index_bits!==0)$fatal(1,"disabled %d",b);end
end
for(b=0;b<20;b=b+1)for(k=0;k<128;k=k+1)begin bank_data=0;bank_data[b*128+k]=1;bank=b;enable=1;#1;if(index_bits!==(128'b1<<k))$fatal(1,"onehot %d %d",b,k);end
$display("PASS 8x32 bank values+disable and2560 onehot bank-bit paths");$finish;end
endmodule
''')
(P/'bankdec_tb.v').write_text('''module tb;
reg enable=0;reg[4:0] bank=0;wire[19:0] bank_enable;integer b;
w5_bank_decoder dut(.*);
initial begin
for(b=0;b<32;b=b+1)begin bank=b;enable=1;#1;if(bank_enable!==(b<20?(20'b1<<b):20'b0))$fatal(1,"bank %d",b);enable=0;#1;if(bank_enable!==0)$fatal(1,"disabled bank %d",b);end
$display("PASS 32 bank addresses+32 disabled checks");$finish;end
endmodule
''')
res={}
for tag,top in [('decoderb-v1','w5_row_decoder'),('mux128b-v1','w5_bank_mux128'),('bankdec-v1','w5_bank_decoder')]:
 stem='bankdec' if 'bankdec' in tag else ('decoder' if 'decoder' in tag else 'mux128');final=P/'runs'/tag/'final/nl'/f'{top}.nl.v'
 if not final.exists():continue
 command=[T+'iverilog','-g2012','-DFUNCTIONAL','-s','tb','-o',str(P/(stem+'.sim')),str(P/(stem+'_tb.v')),str(final),str(lib/'gf180mcu_fd_sc_mcu7t5v0.v'),str(lib/'primitives.v')]
 c=subprocess.run(command,capture_output=True,text=True);(P/(stem+'-compile.log')).write_text(c.stdout+c.stderr);c.check_returncode()
 c=subprocess.run([T+'vvp',str(P/(stem+'.sim'))],capture_output=True,text=True);c.check_returncode();res[top]={'stdout':c.stdout,'netlist':str(final),'command':command}
 print(top,c.stdout.strip())
(P/'functional.json').write_text(json.dumps(res,indent=2)+'\n')
