"""Read-only source/F64 evidence audit; writes only new v3 analysis artifacts.

This is NOT a new RTL simulation or a cycle-level liveness trace.  The live
range proof is in RESULTS-v3.md.  This independently rechecks the retained
F64 evidence and demonstrates why equal-address A/B aliasing loses data.
"""
from pathlib import Path
import ctypes as C
import datetime
import hashlib
import json
import re
import shutil
import struct
import time

START = time.monotonic()
WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
FIXTURE = Path.home()/'.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3'
ACTUAL = Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-all/v2/actual'
pins = {}

def read(path):
    p = Path(path).resolve()
    data = p.read_bytes()
    pins[str(p)] = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    return data

def js(path):
    return json.loads(read(path))

def different(a, b):
    assert len(a) == len(b) == 64*320*4
    words = len(a)//4
    af = struct.unpack('<%dI' % words, a)
    bf = struct.unpack('<%dI' % words, b)
    i = next(i for i in range(words) if af[i] != bf[i])
    return dict(fp32_values=words, unequal_values=sum(x != y for x, y in zip(af, bf)),
                packets_256bit=words//8,
                unequal_packets=sum(a[j:j+32] != b[j:j+32] for j in range(0,len(a),32)),
                first_unequal_scalar=i, a_bits=f'0x{af[i]:08x}', b_bits=f'0x{bf[i]:08x}',
                a_sha256=hashlib.sha256(a).hexdigest(), b_sha256=hashlib.sha256(b).hexdigest())

free = shutil.disk_usage('/').free
assert free >= 22*1024**3, f'Disk floor: {free/1024**3:.3f} GiB'
# Pin and verify every direct v2 compiler input, including its unchanged host.
v2pins = js(WORK/'build-input-pins-v2.json')
for name, expected in v2pins.items():
    assert hashlib.sha256(read(name)).hexdigest() == expected, name
positive_stage = js(WORK/'logs-v2/20261014T031357-positive.json')
assert positive_stage['exit_code'] == 0
log = read(positive_stage['log']).decode()
assert 'common_clocks=312578649' in log
assert 'SOURCE_GENERATIONS generations=30 KV_releases=30' in log
assert 'K_checks=614400 V_checks=614400' in log
assert 'KV_writes=153600' in log
assert 'initialized_reads=199680 initialized_write_ACKs=159360' in log
layers = re.findall(r'^LAYER_ACCEPT layer=(\d+) clocks=(\d+)', log, re.M)
assert [int(a) for a, b in layers] == list(range(6))

binding = js(ROOT/'experiments/voice-e2e-20261012-onboard-numerical-binding-v1/binding-audit.json')
outputs = binding['expected_actual_outputs']
assert len(outputs) == 18
for item in outputs:
    data = read(ACTUAL/item['name'])
    assert len(data) == item['bytes']
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['name']
tokens = list(struct.unpack('<5I',read(ACTUAL/'actual-winning-tokens.bin')))
assert tokens == [28176,373,278,26068,2]
render = js(WORK/'logs-v2/20261014T040706-render.log')
assert render['passed'] and render['text'] == 'Switch on the lights'

# Producer files were dumped from actual RTL-observed writes at complete K/V
# generation publication, in head-major order. Reorder to physical packet order.
def frame_major(data):
    assert len(data) == 81920
    return b''.join(data[(head*64*40+frame*40)*4:(head*64*40+frame*40+40)*4]
                    for frame in range(64) for head in range(8))

producer = []
for layer in range(6):
    a = frame_major(read(ACTUAL/f'actual-layer{layer}-k_cross.bin'))
    b = frame_major(read(ACTUAL/f'actual-layer{layer}-v_cross.bin'))
    producer.append(dict(layer=layer, **different(a,b)))

# Exact encoder references use the same frozen native row library as the
# qualified C++ observer. Check all six normalized-image hashes before using
# them as witnesses. This is reference reconstruction, not a new RTL trace.
fields = iter(read(FIXTURE/'encoder/inputs.txt').decode().split())
gold = []
for layer in range(6):
    weights = next(fields)
    images = {i:next(fields) for i in [7,15,16,17,18,21,20,19,8,9,10,14]}
    domains = [int(next(fields)) for _ in range(8)]
    hashes = [next(fields) for _ in range(4)]
    gold.append((images, domains, hashes))
for _ in range(4):
    next(fields)
rowlib_path, qlib_path = next(fields), next(fields)
assert list(fields) == []
read(rowlib_path)
rowlib = C.CDLL(rowlib_path)
row = rowlib.block
fp = C.POINTER(C.c_float)
row.argtypes = [fp, fp, fp, fp, C.POINTER(C.c_uint32), C.c_int]
row.restype = None
residual_paths = read(FIXTURE/'encoder/residuals.txt').decode().splitlines()
assert len(residual_paths) == 7
encoder = []
zeros = (C.c_float*320)()
for layer, (images, domains, hashes) in enumerate(gold):
    xb, ob, sb = read(images[19]), read(images[10]), read(residual_paths[layer+1])
    x = (C.c_float*(64*320)).from_buffer_copy(xb)
    o = (C.c_float*(64*320)).from_buffer_copy(ob)
    witnesses = {}
    for stage in [0,1]:
        learned = (C.c_float*320).from_buffer_copy(read(images[20 if stage else 21]))
        out = (C.c_float*(64*320))()
        flags = C.c_uint32()
        for frame in range(64):
            offset = frame*320*4
            row(C.cast(C.byref(x,offset),fp), C.cast(C.byref(o,offset),fp) if stage else zeros,
                learned, C.cast(C.byref(out,offset),fp), C.byref(flags), 0 if stage else 1)
        data = bytes(out)
        assert hashlib.sha256(data).hexdigest() == hashes[stage*2]
        witnesses['ff_S_vs_normS' if stage else 'prefix_X_vs_normX'] = different(sb if stage else xb,data)
    encoder.append(dict(layer=layer, **witnesses))

result = dict(
    scope='RTL lifetime analysis correlated with existing, unchanged v2 F64; no new simulation',
    decision='STOP: no safe deletion or equal-address alias of either bank under the existing schedule',
    v2_compiler_inputs_verified=len(v2pins), saved_output_hashes_verified=len(outputs),
    prior_f64_elapsed_seconds=positive_stage['elapsed_seconds'],
    clocks=312578649, tokens=tokens, rendered_text=render['text'],
    encoder_layer_accept_clocks={a:int(b) for a,b in layers},
    producer_generations=30, producer_K_scalar_checks=614400, producer_V_scalar_checks=614400,
    analytical_peak_per_pair=dict(frames=64, words_256bit=5120, fp32_scalars=40960, bytes=163840,
                                  source='RTL barrier proof; not a measured cycle counter'),
    general_peak_per_pair='80*FRAMES words of 256 bits = 2560*FRAMES bytes',
    geometry_examples={str(f):dict(one_bank_bytes=f*1280,pair_bytes=f*2560) for f in [4,64,500,508]},
    overlap_cycle_count=None, overlap_cycle_count_reason='Not instrumented; exact enabling/barrier analysis used as authorized',
    encoder_reference_counterexamples=encoder, producer_actual_counterexamples=producer,
    storage_saved_bytes=0, v3_RTL_created=False, new_F64_run=False,
    disk_free_bytes=free, completed_local=datetime.datetime.now().astimezone().isoformat(),
    analysis_script_seconds=time.monotonic()-START)
# No existing v2 report, log, RTL, host, output, or pin file is written.
read(__file__)
(WORK/'bank-analysis-v3-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
(WORK/'bank-analysis-v3-input-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print(f'V3_ANALYSIS_EVIDENCE_PASS v2_inputs={len(v2pins)} output_hashes=18 layers=6 generations=30')
for name, items in [('encoder',encoder),('producer',producer)]:
    for item in items:
        d = item['ff_S_vs_normS'] if name=='encoder' else item
        print(f"ALIAS_COUNTEREXAMPLE pair={name} layer={item['layer']} unequal_packets={d['unequal_packets']}/2560 first_scalar={d['first_unequal_scalar']} A={d['a_bits']} B={d['b_bits']}")
print('W1-STATUS: evidence audit passed; both pairs need 163840 payload bytes at F64; safe deletion saving=0')
