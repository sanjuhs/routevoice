"""Post-run provenance/scoring audit and exact export of the EXISTING affine frontend encoding.

This does not fit a candidate, rerun inference or change any W7 scores/gates.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from onnxruntime.tools.ort_format_model.ort_flatbuffers_py import fbs

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from stt_metrics import edits, words

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b): return hashlib.sha256(b).hexdigest()
def write(p,obj):
    with p.open('x') as f: json.dump(obj,f,indent=2); f.write('\n')

def main():
    protocol = json.loads((WORK/'protocol.json').read_text())
    scores = json.loads((WORK/'scores.json').read_text())
    result = json.loads((WORK/'results.json').read_text())
    assert scores['protocol_sha256'] == sha(WORK/'protocol.json')
    for rec in protocol['pinned_files']:
        assert sha(rec['path']) == rec['sha256']
    for model in protocol['models'].values():
        for rec in model['files']: assert sha(rec['path']) == rec['sha256']
    expected = {(name,i['input_index']) for name in protocol['models'] for i in protocol['inputs']}
    assert len(expected) == 144
    actual = [(r['model'],r['input_index']) for r in scores['rows']]
    assert len(set(actual)) == len(actual) == 144 and set(actual) == expected
    inputs = {i['input_index']:i for i in protocol['inputs']}
    for row in scores['rows']:
        inp = inputs[row['input_index']]
        assert row['role'] == inp['role'] == 'validation'
        assert row['reference'] == inp['reference']
        assert row['input_float32_sha256'] == inp['input_float32_sha256']
        metric = edits(row['reference'],row['hypothesis'])
        assert all(row[k] == v for k,v in metric.items())
        saved = WORK/'validation'/row['case_id']/'result.json'
        status = next(s for s in scores['cases'] if s['case_id'] == row['case_id'])
        assert status['result_sha256'] == sha(saved) and status['exit_code'] == 0 and status['close_complete']
    # Verify gate outcomes by integer cross-products, independently of the project's Fraction-based gate.
    for name,gs in result['gates_vs_same_session_k64'].items():
        for condition,g in gs.items():
            rr = [r for r in scores['rows'] if r['model']==name and r['condition']==condition]
            br = [r for r in scores['rows'] if r['model']=='fp32_baseline' and r['condition']==condition]
            ce,cw = sum(r['edits'] for r in rr),sum(r['reference_words'] for r in rr)
            be,bw = sum(r['edits'] for r in br),sum(r['reference_words'] for r in br)
            ceiling = {'clean':15,'other':35,'white_noise_10db':40}[condition]
            passed = ce*100 <= ceiling*cw and (ce*bw-be*cw)*100 <= 2*cw*bw
            assert g['pass'] == passed and ce == g['candidate_edits'] and be == g['reference_edits']
    source = Path(protocol['models']['fp32_baseline']['directory'])
    raw = bytearray((source/'frontend.weights.ort').read_bytes())
    graph = fbs.InferenceSession.InferenceSession.GetRootAsInferenceSession(raw,0).Model().Graph()
    tensors = {graph.Initializers(i).Name().decode():graph.Initializers(i) for i in range(graph.InitializersLength())}
    def array(name,dtype):
        t=tensors[name]; return np.frombuffer(t.RawDataAsNumpy().tobytes(),dtype=dtype).reshape(t.DimsAsNumpy())
    inventory = json.loads((WORK/'frontend-inventory.json').read_text())
    export = WORK/'existing-affine-int8-exact'; export.mkdir()
    spec = [('linear_weights','onnx::MatMul_128_add_tensor',1),
            ('conv1_weights','/weight/weight.0/Mul_output_0',0),
            ('conv2_weights','/weight/weight.0_1/Mul_output_0',1)]
    records=[]
    for role,prefix,axis in spec:
        q=array(prefix+'_quantized','int8'); scale=array(prefix+'_scale','<f4'); offset=array(prefix+'_zero_point','<f4')
        # The field is named zero_point by the source but is an additive FP32 offset after multiplication.
        product=(q.astype(np.float32)*scale).astype(np.float32)
        decoded=(product+offset).astype('<f4')
        item=next(r for r in inventory['tensors'] if r['rom_role']==role+'.bin')
        assert decoded.tobytes() == Path(item['rom_path']).read_bytes()
        files=[]
        for suffix,a in [('int8',q),('scale.fp32',scale),('offset.fp32',offset)]:
            path=export/f'{role}.{suffix}.bin';path.write_bytes(a.tobytes())
            files.append({'path':str(path),'shape':list(a.shape),'dtype':str(a.dtype),'bytes':a.nbytes,'sha256':sha(path)})
        records.append({'role':role,'source_initializer_prefix':prefix,'broadcast_channel_axis':axis,
                        'reconstructed_fp32_sha256':digest(decoded.tobytes()),'matches_all_ROM_bits':True,
                        'files':files,'coefficients':q.size})
    bias_files=[]
    for r in inventory['tensors']:
        if r['quantized_in_W7']: continue
        path=export/r['rom_role'];path.write_bytes(Path(r['rom_path']).read_bytes())
        assert sha(path)==r['sha256']
        bias_files.append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)})
    total=sum(f['bytes'] for r in records for f in r['files'])+sum(f['bytes'] for f in bias_files)
    assert total == 2090240
    exact={'status':'Existing source encoding exported and bit-exact against all 2,074,560 fixture coefficients',
           'not_a_new_candidate_or_inference_run':True,'records':records,'unchanged_bias_files':bias_files,
           'int8_bytes':2073600,'fp32_scale_and_offset_bytes':12800,'fp32_bias_bytes':3840,
           'total_payload_bytes':total,'original_expanded_ROM_bytes':8298240,
           'decode_contract':'Round INT8 cast to FP32 times FP32 scale to FP32; then add FP32 offset with a second FP32 rounding. Do not silently fuse, drop offsets or change Conv2 input-channel axis.',
           'hardware_status':'Decoder/storage implementation, access area, timing and power unverified. This is an exact numerical storage alternative, not a symmetric per-output-channel pass.'}
    write(export/'manifest.json',exact)
    audit={'all_144_cases_unique_complete_and_recomputed':True,'model_and_protocol_pins_unchanged':True,
           'all_point_gates_independently_confirmed':True,'per_tensor_zero_normalized_word_utterances':
               sum(not words(r['hypothesis']) for r in scores['rows'] if r['model']=='int8_per_tensor'),
           'existing_exact_encoding_manifest_sha256':sha(export/'manifest.json'),'audit_script_sha256':sha(__file__),
           'scores_sha256':sha(WORK/'scores.json')}
    write(WORK/'audit.json',audit)
    result['final_audit']=audit
    result['existing_source_affine_int8_exact_storage']=exact
    (WORK/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    with (WORK/'RESULTS.md').open('a') as f:
        f.write('\n## Exact existing INT8 representation: separate finding\n\n')
        f.write('The independent post-run audit exported the source INT8 arrays and their original FP32 scales and additive offsets, then reconstructed **all 2,074,560 ROM coefficients bit-for-bit**, including the retained biases. This is the existing K64 encoding, not a newly fitted candidate or a favorable rerun. Payload is **2,090,240 bytes**: 2,073,600 INT8 bytes + 12,800 scale/offset bytes + 3,840 bias bytes. Files and hashes are in `existing-affine-int8-exact/manifest.json`.\n\n')
        f.write('Thus the requested symmetric INT8 schemes fail, while an exact compact source representation already exists at almost the same storage size. Using it on-chip requires original channel axes (Conv2 input-channel axis 1), additive offsets, and separate FP32 multiply/add rounding. That hardware path has not been implemented or timed here, so this is numerical evidence for a storage option, not proof of one-die fit.\n\n')
        f.write('The final audit recomputed all 144 scores, checked unique complete case coverage and unchanged model/protocol pins, and independently confirmed all gates with integer comparisons. All 48 per-tensor hypotheses contain zero normalized words; 100% WER is an observed failure, with successful native process exits, not a missing-result placeholder. Audit: `audit.json`.\n')
    print('W7-STATUS: Final audit passed; requested symmetric variants FAIL; existing affine INT8 export reconstructs every ROM bit in 2,090,240 payload bytes',flush=True)

if __name__=='__main__':main()
