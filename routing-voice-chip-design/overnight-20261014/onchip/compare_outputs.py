"""Verify all 18 native output hashes, tokens and observed RTL service counts."""
from pathlib import Path
import hashlib
import json
import struct

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
actual = Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip/actual-a'
binding = ROOT/'experiments/voice-e2e-20261012-onboard-numerical-binding-v1/binding-audit.json'
expected = json.loads(binding.read_text())['expected_actual_outputs']
assert len(expected) == 18
positive = sorted((WORK/'logs').glob('*-positive.json'))[-1]
stage = json.loads(positive.read_text())
assert stage['exit_code'] == 0, 'No completed successful positive run'
log = Path(stage['log']).read_text()
for name, count in [('decoder_body',1392000), ('decoder_self',787200)]:
    assert f'ONCHIP service={name} rtl_replies={count} host_replies=0 mismatches=0' in log
assert 'FOUR_STAGE_GREEDY_FRONTEND_LEARNED_HISTORY_PRODUCER_METADATA_KV_TABLES_ONBOARD_EOS_PASS tokens=5' in log
assert {p.name for p in actual.iterdir()} == {r['name'] for r in expected}
records = []
for row in expected:
    p = actual/row['name']
    assert not p.is_symlink()
    data = p.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert len(data) == row['bytes'] and digest == row['sha256'], p
    records.append(dict(path=str(p), bytes=len(data), sha256=digest, passed=True))
tokens = list(struct.unpack('<5I',(actual/'actual-winning-tokens.bin').read_bytes()))
assert tokens == [28176,373,278,26068,2]
result = dict(passed=True, native_output_comparisons=18, tokens=tokens, outputs=records,
              original_binding=str(binding), binding_sha256=hashlib.sha256(binding.read_bytes()).hexdigest())
(WORK/'comparison-result.json').write_text(json.dumps(result,indent=2)+'\n')
print('W1-STATUS: all 18 native output hashes and five tokens through EOS passed')
