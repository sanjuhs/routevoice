#!/usr/bin/env python3
"""Export provenance and every ORT initializer; never invent a model quantizer."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import onnxruntime as ort
from onnxruntime.tools.ort_format_model.ort_flatbuffers_py import fbs

TYPES={1:'FLOAT32',2:'UINT8',3:'INT8',4:'UINT16',5:'INT16',6:'INT32',7:'INT64',9:'BOOL',10:'FLOAT16',11:'FLOAT64',12:'UINT32',13:'UINT64',16:'BFLOAT16'}

def text(b):return (b or b'').decode()

def export(source,output):
    graphs=[];all_bytes=0
    for path in sorted(source.glob('*.ort')):
        raw=path.read_bytes();session=fbs.InferenceSession.InferenceSession.GetRootAsInferenceSession(raw,0);graph=session.Model().Graph()
        nodes=[];consumers={}
        for i in range(graph.NodesLength()):
            node=graph.Nodes(i)
            inputs=[text(node.Inputs(j)) for j in range(node.InputsLength())]
            record={'name':text(node.Name()),'op':text(node.OpType()),'inputs':inputs,'outputs':[text(node.Outputs(j)) for j in range(node.OutputsLength())]}
            nodes.append(record)
            for n in inputs:consumers.setdefault(n,[]).append({'node':record['name'],'op':record['op'],'input_index':inputs.index(n)})
        tensors=[]
        for i in range(graph.InitializersLength()):
            t=graph.Initializers(i);name=text(t.Name());shape=[int(x) for x in t.DimsAsNumpy()];data=bytes(t.RawDataAsNumpy())
            rec={'name':name,'shape':shape,'dtype':TYPES.get(t.DataType(),str(t.DataType())),'elements':math.prod(shape),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'consumers':consumers.get(name,[]),'placement_status':'unassigned','execution_rate_hz':None}
            tensors.append(rec);all_bytes+=len(data)
        runtime=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
        io=lambda v:{'name':v.name,'shape':v.shape,'type':v.type}
        graphs.append({'inputs':[io(v) for v in runtime.get_inputs()],'outputs':[io(v) for v in runtime.get_outputs()],'file':path.name,'file_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'node_count':len(nodes),'operations':dict(Counter(n['op'] for n in nodes)),'tensors':tensors,'nodes':nodes})
    if len(graphs)!=6:raise ValueError(f'Expected pinned six ORT graphs, found {len(graphs)}')
    report={'schema_version':1,'initializer_bytes':all_bytes,'graphs':graphs,'precision_policy':'Preserve original graph; no quantization or die assignment inferred by exporter.'}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=export(a.source,a.output);print(f"Exported {sum(len(g['tensors']) for g in r['graphs'])} initializers; {r['initializer_bytes']} bytes")
