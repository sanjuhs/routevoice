from pathlib import Path
W=Path(__file__).resolve().parent
for v in ['array_port','sc_rom']:
 s=(W/'tb'/f'gate_{v}.sv').read_text()
 a=s.index(' // Reset with zero');b=s.index(' for(v=0;v<54;v=v+1)begin',a)
 s=s[:a]+s[b:]
 s=s.replace('for(v=0;v<54;v=v+1)begin','for(v=0;v<1;v=v+1)begin')
 s=s.replace('PASS gate vectors=54 outputs=17280','PASS gate_activity vectors=1 outputs=320').replace('aborts=4','aborts=0')
 s=s.replace('initial begin\n',f'initial begin\n $dumpfile("{W}/evidence/{v}-mapped-speech.saif");$dumpvars(0,dut);\n',1)
 (W/'tb'/f'activity_{v}.sv').write_text(s)
