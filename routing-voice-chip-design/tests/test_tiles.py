"""RTL arithmetic, reset, turnover and output-hold checks against Python integers."""
import importlib.util
import json
import random
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('compiler',ROOT/'scripts/compile_tile.py')
compiler=importlib.util.module_from_spec(spec);spec.loader.exec_module(compiler)


def verify(weights, exhaustive=False, bits=8):
    rtl,meta=compiler.compile_matrix('dut',weights,bits,bits)
    n=meta['inputs'];m=meta['outputs'];w=meta['accumulator_bits'];rng=random.Random(180)
    state_valid=0;state_data=0
    body=[]
    stimuli=[]
    if exhaustive: stimuli=[([x],1,1,1) for x in range(-128,128)]
    else:
        stimuli=[([x]*n,1,1,1) for x in [-(1<<(bits-1)),(1<<(bits-1))-1,0,1,-1]]
        stimuli += [([rng.randrange(-(1<<(bits-1)),1<<(bits-1)) for _ in range(n)],int(rng.random()<.8),int(rng.random()<.65),int(rng.random()>.04)) for _ in range(500)]
    stimuli=[([0]*n,0,0,0)]+stimuli
    for cycle,(xs,valid,ready,rst) in enumerate(stimuli):
        accepted=(not state_valid) or ready
        packed=sum((x&((1<<bits)-1))<<(bits*j) for j,x in enumerate(xs))
        body += [f'@(negedge clk); rst_n={rst}; in_valid={valid}; out_ready={ready}; in_data={n*bits}\'h{packed:x};',
                 f'#1; if(in_ready !== 1\'b{int(accepted)}) $fatal(1,"ready cycle {cycle}");']
        if not rst: state_valid=0;state_data=0
        elif accepted:
            state_valid=valid
            if valid:
                ys=[sum(x*v for x,v in zip(xs,row)) for row in weights]
                state_data=sum((y&((1<<w)-1))<<(i*w) for i,y in enumerate(ys))
        body += ['@(posedge clk); #1;',f'if(out_valid !== 1\'b{state_valid} || out_data !== {w*m}\'h{state_data:x}) $fatal(1,"result cycle {cycle}");']
    tb=f'''module tb;
reg clk=0; always #5 clk=~clk;
reg rst_n=0, in_valid=0,out_ready=0;
reg [{n*bits-1}:0] in_data=0;
wire in_ready,out_valid; wire [{m*w-1}:0] out_data;
dut d(.*);
initial begin
@(posedge clk); #1;
{chr(10).join(body)}
$display("PASS {len(stimuli)} cycles"); $finish;
end
endmodule
'''
    with tempfile.TemporaryDirectory() as d:
        d=Path(d);(d/'dut.sv').write_text(rtl);(d/'tb.sv').write_text(tb)
        subprocess.run(['iverilog','-g2012','-s','tb','-o',str(d/'sim'),str(d/'dut.sv'),str(d/'tb.sv')],check=True,capture_output=True,text=True)
        result=subprocess.run(['vvp',str(d/'sim')],check=True,capture_output=True,text=True)
        assert 'PASS' in result.stdout
    return len(stimuli)


class Tiles(unittest.TestCase):
    def test_all_int8_coefficients_and_inputs(self): verify([[w] for w in range(-128,128)],True)
    def test_dot_products_and_backpressure(self):
        rng=random.Random(180);verify([[-128]*8,[127]*8,[0]*8]+[[rng.randrange(-128,128) for _ in range(8)] for _ in range(5)])
    def test_centered_uint8_operands(self):
        verify([[-256]*8,[255]*8,[0]*8,[132,-135,7,0,3,-123,120,255]],bits=9)
    def test_reject_invalid_weights(self):
        for weights in [[],[[]],[[1],[1,2]],[[128]],[[1.5]],[[True]]]:
            with self.assertRaises(ValueError):compiler.compile_matrix('dut',weights)
    def test_exported_model_tiles(self):
        paths=list((ROOT/'models').glob('die*_tile.json'))
        if not paths:self.skipTest('Model tiles not yet exported')
        for p in paths:
            with self.subTest(tile=p.name):verify(json.loads(p.read_text())['weights'],bits=json.loads(p.read_text()).get('input_bits',8))

if __name__=='__main__':unittest.main()
