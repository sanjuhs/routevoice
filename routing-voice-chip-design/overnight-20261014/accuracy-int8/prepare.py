"""W7 immutable source audit, deterministic weight-only variants, frozen protocol."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort
from onnxruntime.tools.ort_format_model.ort_flatbuffers_py import fbs
import soundfile as sf

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from stt_metrics import noisy

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b): return hashlib.sha256(b).hexdigest()
def write(p, obj):
    with p.open('x') as f: json.dump(obj, f, indent=2); f.write('\n')
def options():
    o = ort.SessionOptions(); o.intra_op_num_threads = 1; o.inter_op_num_threads = 1
    o.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
    return o

def main():
    assert shutil.disk_usage(WORK).free >= 22 * 2**30 + 300 * 2**20
    source = ROOT / 'models/candidates/codebook-4bit-optimal-rectangular-k64'
    manifest = json.loads((source / 'candidate.json').read_text())
    for r in manifest['model_files']: assert sha(source / r['file']) == r['sha256']
    for r in manifest['changed_tensor_records']:
        assert sha(source / 'packed' / r['packed_file']) == r['packed_sha256']
    ledger_path = ROOT / 'experiments/chip-integration-20261012-current-learned-fulltables-service-ledger-v2/ledger.json'
    ledger = json.loads(ledger_path.read_text())
    images = [r for r in ledger['current_images'] if r['service'].startswith('frontend immutable')]
    session = ort.InferenceSession(str(source / 'frontend.weights.ort'), options(), providers=['CPUExecutionProvider'])
    outputs = dict(zip([o.name for o in session.get_outputs()], session.run(None, {})))
    spec = [
        ('linear_weights.bin', 'onnx::MatMul_128_add_tensor_add_tensor', 1),
        ('conv1_weights.bin', '/weight/weight.0/Mul_output_0_add_tensor', 0),
        ('conv2_weights.bin', '/weight/weight.0_1/Mul_output_0_add_tensor', 0),
    ]
    raw = bytearray((source / 'frontend.model.ort').read_bytes())
    graph = fbs.InferenceSession.InferenceSession.GetRootAsInferenceSession(raw, 0).Model().Graph()
    tensors = {graph.Initializers(i).Name().decode(): graph.Initializers(i) for i in range(graph.InitializersLength())}
    inventory = []
    for role, name, axis in spec + [('conv1_bias.bin', 'conv1.conv.bias', None), ('conv2_bias.bin', 'conv2.conv.bias', None)]:
        w = outputs[name] if axis is not None else tensors[name].RawDataAsNumpy().view('<f4').reshape(tensors[name].DimsAsNumpy())
        image = next(r for r in images if r['role'] == role)
        assert digest(w.tobytes()) == sha(image['path']) == image['sha256']
        assert w.nbytes == image['bytes']
        inventory.append({'rom_role': role, 'tensor_name': name, 'shape': list(w.shape), 'dtype': 'float32',
                          'elements': w.size, 'sha256': digest(w.tobytes()), 'rom_path': image['path'],
                          'per_output_channel_axis': axis, 'quantized_in_W7': axis is not None})
    assert sum(r['elements'] for r in inventory) == 2074560
    weight_raw = bytearray((source / 'frontend.weights.ort').read_bytes())
    wg = fbs.InferenceSession.InferenceSession.GetRootAsInferenceSession(weight_raw, 0).Model().Graph()
    existing = []
    for i in range(wg.InitializersLength()):
        t = wg.Initializers(i)
        existing.append({'name': t.Name().decode(), 'shape': list(map(int,t.DimsAsNumpy())),
                         'onnx_dtype': t.DataType(), 'bytes': t.RawDataLength(), 'sha256': digest(t.RawDataAsNumpy().tobytes())})
    write(WORK / 'frontend-inventory.json', {'ledger_sha256': sha(ledger_path), 'tensors': inventory,
          'total_fp32_rom_bytes': sum(r['elements']*4 for r in inventory), 'source_loader_initializers': existing,
          'finding': 'Source loader already uses INT8 codes times FP32 scales plus FP32 offsets; Conv2 broadcasts along input channels. W7 requantizes expanded ROM values symmetrically along output channels or per tensor. Biases remain FP32.'})
    print('W7-STATUS: Step 1 complete; all five ROM image hashes match K64', flush=True)
    models = {'fp32_baseline': {'directory': str(source), 'files': [{'path': str(source/r['file']), 'sha256': r['sha256']} for r in manifest['model_files']]}}
    variants = {}
    for mode in ['int8_per_channel', 'int8_per_tensor']:
        directory = WORK / mode; directory.mkdir(); packed = directory / 'packed'; packed.mkdir()
        for r in manifest['model_files']:
            if r['file'] != 'frontend.weights.ort': shutil.copyfile(source/r['file'], directory/r['file'])
        reconstructed = {}; records = []
        for role, name, axis in spec:
            w = outputs[name]
            axes = tuple(i for i in range(w.ndim) if i != axis) if mode == 'int8_per_channel' else tuple(range(w.ndim))
            maximum = np.max(np.abs(w), axis=axes, keepdims=True)
            scales = (maximum / np.float32(127)).astype('<f4')
            scales[maximum == 0] = np.float32(1)
            q = np.clip(np.rint(w / scales), -127, 127).astype('int8')
            dq = (q.astype(np.float32) * scales).astype('<f4')
            qpath = packed / role.replace('.bin', '.int8.bin'); spath = packed / role.replace('.bin', '.scale.fp32.bin')
            qpath.write_bytes(q.tobytes()); spath.write_bytes(scales.tobytes())
            decoded = np.frombuffer(qpath.read_bytes(), dtype='int8').reshape(w.shape).astype(np.float32) * np.frombuffer(spath.read_bytes(), dtype='<f4').reshape(scales.shape)
            assert decoded.tobytes() == dq.tobytes()
            reconstructed[name] = dq
            records.append({'name': name, 'shape': list(w.shape), 'axis': axis if mode == 'int8_per_channel' else None,
                            'scale_shape': list(scales.shape), 'int8_file': str(qpath), 'int8_sha256': sha(qpath), 'int8_bytes': q.nbytes,
                            'scale_file': str(spath), 'scale_sha256': sha(spath), 'scale_bytes': scales.nbytes,
                            'dequantized_sha256': digest(dq.tobytes()), 'source_sha256': digest(w.tobytes()),
                            'rmse': float(np.sqrt(np.mean((dq.astype('float64')-w)**2))), 'max_abs_error': float(np.max(np.abs(dq-w)))})
        # Only the coefficient loader is reserialized. All numerical frontend operators and remaining model files are copied byte-for-byte.
        graph = helper.make_graph([], 'W7_dequantized_frontend_weights', [],
            [helper.make_tensor_value_info(n, onnx.TensorProto.FLOAT, list(w.shape)) for n,w in reconstructed.items()],
            [numpy_helper.from_array(w, n) for n,w in reconstructed.items()])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 17)], ir_version=9)
        onnx.checker.check_model(model)
        onnx_path = directory / 'dequantized-weights.onnx'; onnx.save(model, onnx_path)
        o = options(); o.optimized_model_filepath = str(directory / 'frontend.weights.ort'); o.add_session_config_entry('session.save_model_format', 'ORT')
        ss = ort.InferenceSession(str(onnx_path), o, providers=['CPUExecutionProvider'])
        ss = ort.InferenceSession(str(directory / 'frontend.weights.ort'), options(), providers=['CPUExecutionProvider'])
        for n,w in zip(ss.get_outputs(),ss.run(None,{})): assert w.tobytes() == reconstructed[n.name].tobytes()
        files = []
        for r in manifest['model_files']:
            h = sha(directory/r['file'])
            if r['file'] != 'frontend.weights.ort': assert h == r['sha256']
            files.append({'path': str(directory/r['file']), 'sha256': h})
        models[mode] = {'directory': str(directory), 'files': files}
        variants[mode] = {'tensors': records, 'int8_weight_bytes': sum(r['int8_bytes'] for r in records),
                          'fp32_scale_bytes': sum(r['scale_bytes'] for r in records), 'unchanged_fp32_bias_bytes': 3840,
                          'total_frontend_coefficient_storage_bytes': sum(r['int8_bytes']+r['scale_bytes'] for r in records)+3840,
                          'all_other_runtime_files_bit_identical': True}
    write(WORK / 'variants.json', variants)
    print('W7-STATUS: Step 2 complete; both variants exported and independently decoded', flush=True)
    old = json.loads((ROOT / 'reports/taalas-isolated-k64-validation-protocol-v1.json').read_text())
    manifest_path = ROOT / 'reports/stt-evaluation-manifest.json'
    clips = [c for c in json.loads(manifest_path.read_text())['clips'] if c['role'] == 'validation']
    assert len(clips) == 32
    old_inputs = {(i['id'],i['condition']):i for i in old['inputs']}
    inputs = []; idir = WORK/'inputs'; idir.mkdir()
    for c in clips:
        assert sha(ROOT/c['path']) == c['sha256']
        audio,sr = sf.read(ROOT/c['path'], dtype='float32'); assert sr == 16000 and audio.ndim == 1
        condition = 'clean' if c['source_split'].endswith('clean') else 'other'
        signals = [(condition, audio)]
        if condition == 'clean': signals.append(('white_noise_10db', noisy(audio, c['id'])))
        for condition,signal in signals:
            i = old_inputs[c['id'],condition]; path = idir / f'input-{i["input_index"]:03}.npy'; np.save(path, signal, allow_pickle=False)
            assert digest(signal.tobytes()) == i['input_float32_sha256'] and sha(path) == i['signal_file_sha256']
            inputs.append({**i, 'signal_file': str(path)})
    assert len(inputs) == 48 and all(i['role']=='validation' for i in inputs)
    # A one-line local worker adaptation enforces the authorized CPU cap using the native library's audited switch.
    worker_source = (ROOT / 'scripts/isolate_native_worker.py').read_text()
    old_assert = "assert os.environ.get('MOONSHINE_ORT_SINGLE_THREAD') is None"
    assert worker_source.count(old_assert) == 1
    worker_path = WORK / 'isolate_native_worker_singlethread.py'
    worker_path.write_text(worker_source.replace(old_assert, "assert os.environ.get('MOONSHINE_ORT_SINGLE_THREAD') == '1'"))
    pins = [Path(__file__), WORK/'run.py', worker_path, ROOT/'scripts/isolate_native_worker.py', ROOT/'scripts/evaluate_stt_isolated.py', ROOT/'scripts/stt_metrics.py',
            manifest_path, ROOT/'reports/stt-requirements.json', source/'candidate.json', WORK/'variants.json', WORK/'frontend-inventory.json',
            ROOT/'reports/taalas-isolated-k64-validation-protocol-v1.json']
    protocol = {'stage': 'validation', 'status': 'Frozen before any W7 recognition inference', 'models': models, 'inputs': inputs,
                'expected_calls': 144, 'workers': 1, 'maximum_seconds_per_process': 120,
                'BLAS_environment': {'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','VECLIB_MAXIMUM_THREADS':'1','MKL_NUM_THREADS':'1','MOONSHINE_ORT_SINGLE_THREAD':'1','PYTHONDONTWRITEBYTECODE':'1'},
                'native_library_sha256': old['native_library_sha256'], 'gate_limits': old['gate_limits'],
                'quantization': 'absmax/127 FP32 scale, nearest-even rounding, clipping [-127,127], zero offset, zero-range scale=1; weights only; no calibration or fitting',
                'reference_for_W7_gate': 'Same-session unmodified K64 fp32_baseline. Historical original-relative gates reported separately; no stacking +2pp silently.',
                'execution_change': 'Same isolated native worker with only environment assertion changed to native single-thread=1; one sequential worker; scorer, noise, inference API and flags unchanged. Coefficient loader alone reserialized for variants.',
                'reserved_test_used': False, 'subset': False, 'new_variant_validation_exposures': 2,
                'source_reading': 'Read skill, complete supplied notes, accuracy reference, earlier evaluations, and relevant local primary patent excerpts. Root plan.md absent; no new architecture or physical feasibility claims.',
                'disk_floor_bytes': 22*2**30, 'pinned_files': [{'path':str(p),'sha256':sha(p)} for p in pins]}
    write(WORK / 'protocol.json', protocol)
    print('W7-STATUS: Validation protocol frozen; 48 inputs x 3 models = 144 fresh processes; no test inputs', flush=True)

if __name__ == '__main__': main()
