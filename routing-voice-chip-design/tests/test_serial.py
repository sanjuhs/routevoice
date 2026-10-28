"""Cycle-accurate checks for sign-plane handling, reset during work and stalls."""
import importlib.util,json,random,subprocess,tempfile,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from compile_serial import compile_serial

def verify(weights):
    rtl,meta=compile_serial('dut',weights);n=meta['inputs'];m=meta['outputs'];w=meta['accumulator_bits'];bits=9
    rng=random.Random(180);state={'busy':0,'valid':0,'data':0,'left':0,'result':0};body=[];accepted=completed=0
    for c in range(1500):
        rst=int(c>0 and rng.random()>.01);valid=int(rng.random()<.85);ready=int(rng.random()<.65)
        xs=[rng.randrange(-256,256) for _ in range(n)]
        if c%17==0:xs=[-256]*n
        if c%19==0:xs=[255]*n
        packed=sum((x&511)<<(9*j) for j,x in enumerate(xs));inready=int(not state['busy'] and (not state['valid'] or ready))
        body += [f'@(negedge clk); rst_n={rst}; in_valid={valid}; out_ready={ready}; in_data={n*9}\'h{packed:x};',f'#1; if(in_ready !== 1\'b{inready}) $fatal(1,"ready {c}");']
        if not rst:state={'busy':0,'valid':0,'data':0,'left':0,'result':0}
        else:
            if state['valid'] and ready:state['valid']=0
            if state['busy']:
                state['left']-=1
                if state['left']==0:state.update(busy=0,valid=1,data=state['result']);completed+=1
            elif valid and inready:
                ys=[sum(x*v for x,v in zip(xs,row)) for row in weights]
                state.update(busy=1,left=bits,result=sum((y&((1<<w)-1))<<(j*w) for j,y in enumerate(ys)));accepted+=1
        body += ['@(posedge clk); #1;',f'if(out_valid !== 1\'b{state["valid"]} || out_data !== {m*w}\'h{state["data"]:x}) $fatal(1,"output {c}");']
    assert accepted>100 and completed>90
    tb=f'''module tb;
reg clk=0; always #5 clk=~clk;
reg rst_n=0,in_valid=0,out_ready=0; reg [{n*9-1}:0] in_data=0;
wire in_ready,out_valid;wire [{m*w-1}:0] out_data;
dut d(.*);
initial begin @(posedge clk); #1;
{chr(10).join(body)}
$display("PASS");$finish;end
endmodule
'''
    with tempfile.TemporaryDirectory() as d:
        p=Path(d);(p/'dut.sv').write_text(rtl);(p/'tb.sv').write_text(tb)
        subprocess.run(['iverilog','-g2012','-s','tb','-o',str(p/'sim'),str(p/'dut.sv'),str(p/'tb.sv')],capture_output=True,check=True)
        r=subprocess.run(['vvp',str(p/'sim')],capture_output=True,check=True,text=True);assert 'PASS' in r.stdout

class Serial(unittest.TestCase):
    def test_signed_extremes(self):verify([[-256]*8,[255]*8,[0]*8])
    def test_real_slices(self):
        for p in (ROOT/'models').glob('die*_tile.json'):
            with self.subTest(p.name):verify(json.loads(p.read_text())['weights'])
