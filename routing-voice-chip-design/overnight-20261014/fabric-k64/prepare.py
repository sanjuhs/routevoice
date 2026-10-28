from pathlib import Path
import os,sys,json,hashlib,shutil,re
os.environ['PYTHONDONTWRITEBYTECODE']='1'
sys.dont_write_bytecode=True
import numpy as np
W=Path(__file__).resolve().parent
R=W.parents[1]
sys.path.insert(0,str(R/'scripts'))
from apply_taalas_routing import read_projection
from compile_taalas_word_k128 import decode_rectangular
from onnxruntime.tools.ort_format_model.ort_flatbuffers_py import fbs
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashbytes=lambda b:hashlib.sha256(b).hexdigest()
candidate=R/'models/candidates/codebook-4bit-optimal-rectangular-k64'
report=json.loads((R/'reports/taalas-serial-word-nibble-k64-1280x320.json').read_text())
manifest=json.loads((candidate/'candidate.json').read_text())
assert sha(candidate/'candidate.json')==report['candidate_manifest_sha256']
weights,zeros,source=read_projection(candidate/'encoder.ort')
original,oz,osource=read_projection(R/'models/artifacts/encoder.ort')
assert source==report['source'] and osource==report['original_source']
record=next(x for x in manifest['changed_tensor_records'] if x['file']=='encoder.ort' and x['tensor']=='val_89_quantized')
recon,indices,books,ranges=decode_rectangular(record,(candidate/'packed'/record['packed_file']).read_bytes(),64)
np.testing.assert_array_equal(recon,weights)
assert hashbytes(original.tobytes())==record['original_sha256']
raw=(candidate/'encoder.ort').read_bytes();g=fbs.InferenceSession.InferenceSession.GetRootAsInferenceSession(raw,0).Model().Graph()
tensors={g.Initializers(i).Name().decode():g.Initializers(i) for i in range(g.InitializersLength())}
scale=np.frombuffer(bytes(tensors['val_89_scale'].RawDataAsNumpy()),dtype='<f4').copy()
bias=np.frombuffer(bytes(tensors['blocks.0.ff.project_out.bias'].RawDataAsNumpy()),dtype='<f4').copy()
np.savez(W/'vectors/model.npz',weights=weights,original_weights=original,zero= zeros,indices=indices,books=np.array(books,dtype=np.uint8),weight_scale=scale,bias=bias)
(W/'evidence/selected-record.json').write_text(json.dumps(record,indent=2))
prev=R/'build/taalas-serial/word-nibble-k64-1280x320';aff=R/'build/taalas-projection-nibble-k64-affine'
assert sha(prev/'taalas_serial_tile.sv')==report['rtl']['sha256']
for name,key in [('inputs.hex','input_sha256'),('expected.hex','expected_sha256')]:
 assert sha(prev/name)==report['simulation'][key]
 shutil.copyfile(prev/name,W/'vectors'/('integer-'+name))
for name in ['inputs.hex','expected.hex','activation-scales.hex','weight-scales.hex','bias.hex']:
 shutil.copyfile(aff/name,W/'vectors'/name)
def readhex(path,bits,signed=False):
 a=np.array([int(x,16) for x in path.read_text().split()],dtype=np.int64)
 if signed:a[a>=1<<(bits-1)]-=1<<bits
 return a
acts=readhex(W/'vectors/inputs.hex',9,True).reshape(-1,1280)
dots=acts@(weights.astype(np.int64)-zeros)
np.testing.assert_array_equal(dots[1:].ravel(),readhex(W/'vectors/integer-expected.hex',32,True))
asbits=readhex(W/'vectors/activation-scales.hex',32).astype(np.uint32);asc=asbits.view(np.float32)
floatref=np.add(np.multiply(dots.astype(np.float32),np.multiply(asc[:,None],scale[None,:],dtype=np.float32),dtype=np.float32),bias[None,:],dtype=np.float32)
np.testing.assert_array_equal(floatref.view(np.uint32).ravel(),readhex(W/'vectors/expected.hex',32))
np.save(W/'vectors/numpy-integer-reference.npy',dots);np.save(W/'vectors/numpy-fp32-reference.npy',floatref)
# Independent reference reads executable candidate tensor bytes, not generated lookup RTL.
# Pre-codebook original differs by design; record delta rather than falsely claiming equality.
origdots=acts@(original.astype(np.int64)-oz)
identity={'source':source,'original_source':osource,'candidate_manifest_sha256':sha(candidate/'candidate.json'),'packed_sha256':report['packed_sha256'],'book_bytes_sha256':hashbytes(np.array(books,np.uint8).tobytes()),'indices_unpacked_sha256':hashbytes(indices.tobytes()),'coefficient_count':int(weights.size),'books':6400,'representatives':102400,'reconstruction_equal':True,'numpy_integer_comparisons':int(dots[1:].size),'numpy_float_comparisons':int(floatref.size),'original_uncoded_different_coefficients':int(np.count_nonzero(original!=weights)),'original_uncoded_different_integer_outputs':int(np.count_nonzero(origdots!=dots)),'candidate_vs_original_scope':'Exactness target is executable frozen K64 tensor. Pre-codebook original preserved and hashed; not numerically identical.'}
(W/'evidence/identity.json').write_text(json.dumps(identity,indent=2))
text=(prev/'taalas_serial_tile.sv').read_text()
engine=text[:text.index('// Simulation-only mask image.')]
(W/'rtl/engine.sv').write_text(engine)
fabric=text[text.index('module taalas_index_fabric'):text.index('module taalas_serial_tile')]
(W/'rtl/index_fabric.sv').write_text('// Standard-cell comparator: all constant rows synthesized, no memory macro.\n'+fabric)
for name in ['taalas_projection_affine.sv','taalas_fp32_affine.sv']:
 shutil.copyfile(R/'rtl'/name,W/'rtl'/name)
shutil.copytree(R/'third_party/hardfloat/HardFloat-1/source',W/'hf',dirs_exist_ok=True)
meta=['module fixed_metadata(input wire [8:0] column,output reg [31:0] weight_scale,bias);','always @* begin weight_scale=0;bias=0;case(column)']
for j in range(320):meta.append(f"9'd{j}:begin weight_scale=32'h{scale.view(np.uint32)[j]:08x};bias=32'h{bias.view(np.uint32)[j]:08x};end")
meta+=['endcase end endmodule'];(W/'rtl/metadata.sv').write_text('\n'.join(meta))
ports='''input wire clk,reset,start,step_enable,
input wire signed [8:0] in_data,input wire in_valid,output wire in_ready,
input wire [31:0] activation_scale,output wire busy,out_valid,input wire out_ready,
output wire [31:0] out_data,output wire [8:0] out_column,output wire [4:0] exceptions'''
body='''wire [8:0] metadata_column;wire [31:0] weight_scale,bias;
fixed_metadata metadata(.column(metadata_column),.weight_scale(weight_scale),.bias(bias));
taalas_projection_affine projection(.*);
'''
(W/'rtl/rv_k64_array_port.sv').write_text('module rv_k64_array_port('+ports+',\noutput wire [10:0] array_row,output wire array_read_enable,input wire [1279:0] frozen_index_bits);\n'+body+'endmodule\n')
(W/'rtl/rv_k64_sc_rom.sv').write_text('module rv_k64_sc_rom('+ports+');\nwire [10:0] array_row;wire array_read_enable;wire [1279:0] frozen_index_bits;\n'+body+'taalas_index_fabric fabric(.row(array_row),.read_enable(array_read_enable),.frozen_index_bits(frozen_index_bits));\nendmodule\n')
# Reuse rigorous saved checker with fixed metadata removed from host and a separate array model only for ARRAY-PORT.
tb=(aff/'tb.sv').read_text().replace(str(aff),str(W/'vectors')).replace('always #5','always #10')
tb=tb.replace('reg [31:0] scale_mem[0:319],bias_mem[0:319],as_mem[0:53];','reg [31:0] as_mem[0:53];')
tb=re.sub(r'wire \[31:0\] weight_scale=.*?;\n','',tb)
tb=re.sub(r'\$readmemh\("[^"]*weight-scales.hex",scale_mem\);\$readmemh\("[^"]*bias.hex",bias_mem\);','',tb)
tb=tb.replace('dut.engine','dut.projection.engine')
# Check integer result on every visible beat as well as FP32; an independent numpy oracle.
tb=tb.replace('integer v,r,c,elapsed', 'reg [31:0] int_expected[0:17279];\ninteger integer_checks=0;\ninteger v,r,c,elapsed')
(W/'vectors/integer-all.hex').write_text(''.join(f'{int(x)&0xffffffff:08x}\n' for x in dots.ravel()))
tb=tb.replace('initial begin\n',f'initial begin\n $readmemh("{W}/vectors/integer-all.hex",int_expected);\n')
tb=tb.replace('if(out_valid)begin','if(dut.projection.integer_valid)begin\n if(dut.projection.integer_result!==int_expected[v*320+dut.metadata_column])$fatal(1,"integer numpy mismatch");\n if(dut.projection.integer_ready)integer_checks=integer_checks+1;\n end\n if(out_valid)begin')
tb=tb.replace('total=total+elapsed;', 'total=total+elapsed; $display("vector=%0d cycles=%0d reads=%0d",v,elapsed,reads);')
tb=tb.replace('$display("PASS vectors=', 'if(integer_checks!=17280)$fatal(1,"integer count");\n $display("PASS vectors=')
for variant in ['array_port','sc_rom']:
 t=tb.replace('taalas_projection_affine dut(.*);',f'rv_k64_{variant} dut(.*);')
 if variant=='sc_rom':
  t=t.replace('taalas_index_fabric fabric(.row(array_row),.read_enable(array_read_enable),.frozen_index_bits(frozen_index_bits));','assign array_row=dut.array_row;assign array_read_enable=dut.array_read_enable;')
 # real speech trace only, after abort checks; retains synthesis hierarchy signal names.
 t=t.replace('for(v=0;v<54;v=v+1)begin',f'$dumpfile("{W}/evidence/{variant}-speech.vcd");$dumpvars(0,dut);\n for(v=0;v<54;v=v+1)begin')
 t=t.replace('total=total+elapsed;', 'if(v==0)$dumpoff;\n total=total+elapsed;')
 trace=t.replace('s<=4','s<=0').replace('v<54','v<1').replace('integer_checks!=17280','integer_checks!=320').replace('PASS vectors=54 outputs=17280','PASS trace vectors=1 outputs=320').replace('aborts=4','aborts=0')
 (W/'tb'/f'trace_{variant}.sv').write_text(trace)
 full='\n'.join(line for line in t.splitlines() if '$dump' not in line)+'\n'
 (W/'tb'/f'{variant}.sv').write_text(full)
hf=['HardFloat_primitives.v','HardFloat_rawFN.v','isSigNaNRecFN.v','fNToRecFN.v','recFNToFN.v','iNToRecFN.v','mulRecFN.v','addRecFN.v','ARM-VFPv2/HardFloat_specialize.v']
common=[W/'hf'/n for n in hf]+[W/'rtl'/n for n in ['engine.sv','taalas_fp32_affine.sv','taalas_projection_affine.sv','metadata.sv']]
for variant in ['array_port','sc_rom']:
 files=common+[W/'rtl'/f'rv_k64_{variant}.sv']+([W/'rtl/index_fabric.sv'] if variant=='sc_rom' else [])
 cfg={'DESIGN_NAME':f'rv_k64_{variant}','VERILOG_FILES':list(map(str,files)),'VERILOG_INCLUDE_DIRS':[str(W/'hf'),str(W/'hf/ARM-VFPv2')],'CLOCK_PORT':'clk','CLOCK_PERIOD':20.0,'FP_CORE_UTIL':40,'PL_TARGET_DENSITY_PCT':45,'DRT_THREADS':3,'STA_THREADS':2,'RUN_MAGIC_DRC':True,'RUN_KLAYOUT_DRC':True,'RUN_LVS':True,'RUN_CTS':True,'RUN_DRT':True,'RUN_FILL_INSERTION':True,'RUN_MCSTA':True,'RUN_SPEF_EXTRACTION':True,'RUN_ANTENNA_REPAIR':True}
 (W/'configs'/f'{variant}.json').write_text(json.dumps(cfg,indent=2))
(W/'evidence/source-hashes.json').write_text(json.dumps({str(p.relative_to(W)):sha(p) for p in W.rglob('*') if p.is_file() and p.suffix in ['.sv','.v','.vi','.hex','.npz']},indent=2))
print('W2b-STATUS: identity PASS; 409600 coefficients, 6400 books, 16960 integer and 17280 FP32 numpy comparisons; RTL/configs generated')
