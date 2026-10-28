#!/usr/bin/env python3
"""Export exact centered UINT8 weight slices from three named model operators."""
import hashlib,json
from pathlib import Path
import numpy as np
from onnxruntime.tools.ort_format_model.ort_flatbuffers_py import fbs
from compile_tile import compile_matrix
ROOT=Path(__file__).resolve().parents[1]
SELECTIONS=[('die1_tile','encoder.ort','blocks.0.ff.project_out.bias'),('die2_tile','encoder.ort','blocks.3.ff.project_out.bias'),('die3_tile','decoder_kv.ort','cross_attn_blocks.0.ff.project_out.bias')]
for name,filename,bias in SELECTIONS:
    raw=(ROOT/'models/artifacts'/filename).read_bytes()
    graph=fbs.InferenceSession.InferenceSession.GetRootAsInferenceSession(raw,0).Model().Graph()
    tensors={t.Name().decode():t for t in [graph.Initializers(i) for i in range(graph.InitializersLength())]}
    found=[]
    for i in range(graph.NodesLength()):
        node=graph.Nodes(i);ins=[node.Inputs(j).decode() for j in range(node.InputsLength())]
        if node.OpType()==b'DynamicQuantizeMatMul' and bias in ins:found.append((node,ins))
    if len(found)!=1:raise RuntimeError('Selection must resolve to one exact operator')
    node,ins=found[0];t=tensors[ins[1]];zp=tensors[ins[3]];scale=tensors[ins[2]]
    if t.DataType()!=2 or zp.DataType()!=2:raise RuntimeError('Expected UINT8 matrix and zero point')
    shape=[int(v) for v in t.DimsAsNumpy()];zero=np.asarray(zp.RawDataAsNumpy(),dtype=np.uint8).astype(np.int64)
    if len(zero) not in (1,shape[1]):raise RuntimeError('Unsupported weight zero-point axis')
    matrix=np.asarray(t.RawDataAsNumpy(),dtype=np.uint8).reshape(shape).astype(np.int64)-zero
    # ONNX B has [K,N]; compiler expects [output,input].
    weights=matrix[:8,:8].T.tolist()
    obj={'name':name,'input_bits':9,'weight_bits':9,'weights':weights,'provenance':{'file':filename,'file_sha256':hashlib.sha256(raw).hexdigest(),'node':node.Name().decode(),'operator':node.OpType().decode(),'tensor':ins[1],'tensor_shape_K_N':shape,'tensor_sha256':hashlib.sha256(bytes(t.RawDataAsNumpy())).hexdigest(),'weight_zero_points':zero.tolist(),'zero_point_shape':[int(v) for v in zp.DimsAsNumpy()],'scale_name':ins[2],'scale_sha256':hashlib.sha256(bytes(scale.RawDataAsNumpy())).hexdigest(),'slice_K':[0,8],'slice_N':[0,8],'orientation':'transpose B[K,N] to W[output,input]'},'boundary':'Exact 8x8 partial integer dot only. Inputs are centered quantized activations (A_uint8 - A_zero_point). Dynamic activation quantization, scale, bias, remaining K terms and full layer/model execution are not implemented.'}
    (ROOT/'models'/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    rtl,meta=compile_matrix(name,weights,9,9);(ROOT/'rtl'/f'{name}.sv').write_text(rtl)
    (ROOT/'reports'/f'{name}-compile.json').write_text(json.dumps(meta,indent=2)+'\n')
    config={'DESIGN_NAME':name,'VERILOG_FILES':[f'dir::../rtl/{name}.sv'],'CLOCK_PORT':'clk','CLOCK_PERIOD':100.0,'FP_CORE_UTIL':30,'MAX_FANOUT_CONSTRAINT':4,'PL_TARGET_DENSITY_PCT':45}
    (ROOT/'physical'/f'{name[:4]}.json').write_text(json.dumps(config,indent=2)+'\n')
    print(name,ins[1],shape,'selected_zero_points',zero[:8].tolist(),'slice range',min(map(min,weights)),max(map(max,weights)))
