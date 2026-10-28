"""Minimal sequential wrapper around the frozen project's isolated case/scorer/gate."""
import inspect
import json
import os
from pathlib import Path
import shutil
import sys
import time

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import evaluate_stt_isolated as isolated
from stt_metrics import aggregate
from audit_native_reproducibility import sha, write_new

def main():
    p = json.loads((WORK/'protocol.json').read_text()); isolated.pinned_check(p)
    assert not (WORK/'validation').exists() and not (WORK/'scores.json').exists()
    os.environ['PYTHONPATH'] = str(ROOT/'scripts')
    # Preserve the project's case runner exactly apart from output location, local single-thread worker and its environment.
    source = inspect.getsource(isolated.run_case)
    source = source.replace("str(ROOT / 'scripts/isolate_native_worker.py')", "str(WORK / 'isolate_native_worker_singlethread.py')")
    source = source.replace("env.pop('MOONSHINE_ORT_SINGLE_THREAD', None)", "env['MOONSHINE_ORT_SINGLE_THREAD'] = '1'")
    namespace = {**isolated.__dict__, 'BUILD': WORK, 'WORK': WORK}
    exec(compile(source, str(WORK/'case-runner-effective.py'), 'exec'), namespace)
    (WORK/'case-runner-effective.py').write_text(source)
    statuses = []; rows = []; resource_checks = []; begin = time.monotonic()
    for item in p['inputs']:
        for name in p['models']:
            free = shutil.disk_usage(WORK).free
            resource_checks.append({'before_case':f'{name}-input-{item["input_index"]:03}', 'free_disk_bytes':free, 'time':time.time()})
            if free < p['disk_floor_bytes']:
                write_new(WORK/'resource-stop.json', {'reason':'disk below 22 GiB floor', 'checks':resource_checks})
                raise RuntimeError('Disk free-space guard; preserve partial cases')
            status,row = namespace['run_case'](('validation',name,item,p)); statuses.append(status)
            if row is not None: rows.append(row)
            print(f'W7-PROGRESS: {len(statuses)}/{p["expected_calls"]} {status["case_id"]} exit={status.get("exit_code")} close={status["close_complete"]}', flush=True)
            (WORK/'progress.json').write_text(json.dumps({'cases':statuses,'rows':rows},indent=2)+'\n')
    isolated.pinned_check(p)
    reference = {r['input_index']:r for r in rows if r['model']=='fp32_baseline'}
    failures = [s for s in statuses if s.get('exit_code') != 0 or not s['close_complete']]
    mismatches = [r['case_id'] for r in rows if r['input_index'] not in reference or r['segment_pcm_boundary_sha256'] != reference[r['input_index']]['segment_pcm_boundary_sha256']]
    summary = {name:aggregate([r for r in rows if r['model']==name]) for name in p['models']}
    integrity = len(rows) == len(statuses) == p['expected_calls'] and not failures and not mismatches
    scores = {'protocol_sha256':sha(WORK/'protocol.json'), 'integrity_passed':integrity, 'rows':rows, 'cases':statuses,
              'process_failures':failures, 'PCM_mismatches':mismatches, 'summary':summary,
              'elapsed_seconds':time.monotonic()-begin,'resource_checks':resource_checks}
    write_new(WORK/'scores.json',scores)
    print('W7-STATUS: Step 3 complete; full validation evaluated; integrity='+str(integrity),flush=True)
    if not integrity:
        write_new(WORK/'results.json', {'status':'inconclusive: integrity failure','scores_sha256':sha(WORK/'scores.json'),'summary':summary})
        (WORK/'RESULTS.md').write_text('# W7 INT8 frontend\n\nInconclusive: evaluation integrity failed. All cases preserved in scores.json.\n')
        return
    conditions = ['clean','other','white_noise_10db']
    gates = {name:isolated.gate(summary[name],summary['fp32_baseline'],conditions,p['gate_limits']) for name in p['models'] if name!='fp32_baseline'}
    historical = json.loads((ROOT/'reports/taalas-isolated-k64-validation-scores-v1.json').read_text())
    historical_summary = historical['summary']
    if 'validation' in historical_summary['original']: historical_summary = {n:s['validation'] for n,s in historical_summary.items()}
    original_gates = {name:isolated.gate(summary[name],historical_summary['original'],conditions,p['gate_limits']) for name in p['models']}
    old_k64 = { (r['id'],r['condition']):r for r in historical['rows'] if r['model']=='k64'}
    baseline_differences = []
    for r in reference.values():
        old = old_k64[r['id'],r['condition']]
        if r['normalized_tokens'] != old['normalized_tokens']:
            baseline_differences.append({'id':r['id'],'condition':r['condition'],'current':r['hypothesis'],'historical':old['hypothesis']})
    variants = json.loads((WORK/'variants.json').read_text())
    result = {'status':'complete', 'integrity_passed':True, 'full_frozen_validation':True,'reserved_test_used':False,
              'utterances_per_condition':16,'distinct_utterances':32,'conditions_per_model':48,'inference_calls':144,
              'summary':summary,'gates_vs_same_session_k64':gates,
              'passes_W7_point_gates':{n:all(g['pass'] for g in gs.values()) for n,gs in gates.items()},
              'historical_original_relative_gates_not_same_session':original_gates,
              'same_session_k64_vs_historical_k64_transcript_differences':baseline_differences,
              'gate_limits':p['gate_limits'],'storage':variants,'biases_quantized':False,
              'limitations':['Small previously exposed development validation; no population accuracy guarantee.',
                  'Only weight storage quantization tested; inference dequantizes to FP32 and retains all activation/operator semantics.',
                  '960 biases stay FP32 and scale storage is charged. Source loader already has exact INT8+scale+offset representation.',
                  'No RTL dequantizer, physical fit, timing or power claim; no new reserved-test inference.',
                  'Native single-thread enforced in every arm; earlier K64 validation used native defaults. Historical comparisons are separately labeled.'],
              'provenance':{'protocol_sha256':sha(WORK/'protocol.json'),'scores_sha256':sha(WORK/'scores.json'),
                            'inventory_sha256':sha(WORK/'frontend-inventory.json'),'minimum_observed_free_disk_GiB':min(c['free_disk_bytes'] for c in resource_checks)/2**30,
                            'elapsed_seconds':scores['elapsed_seconds']}}
    write_new(WORK/'results.json',result)
    lines = ['# W7: INT8 frontend validation', '',
             'Full frozen development validation: 32 distinct utterances from 16 speakers; 16 clean, 16 other, and the same 16 clean clips with frozen 10 dB noise. 144 fresh native processes completed. Reserved test was not used.', '',
             '| Condition | Utterances / words | K64 FP32 ROM baseline | INT8 per-output-channel | Δ pp | INT8 per-tensor | Δ pp |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for c in conditions:
        a,b,d = [summary[n][c] for n in p['models']]
        fmt=lambda r:f'{100*r["wer"]:.4f}% ({r["edits"]}/{r["reference_words"]})'
        lines.append(f'| {c} | {a["clips"]} / {a["reference_words"]} | {fmt(a)} | {fmt(b)} | {gates["int8_per_channel"][c]["delta_percentage_points"]:+.4f} | {fmt(d)} | {gates["int8_per_tensor"][c]["delta_percentage_points"]:+.4f} |')
    lines += ['', 'Frozen limits: clean WER ≤15%, other ≤35%, noise ≤40%, and degradation ≤2 percentage points in **each** condition. W7 compares each INT8 arm against the unmodified K64 run in this same session.', '']
    for n,passed in result['passes_W7_point_gates'].items(): lines.append(f'- **{n}: {"PASS" if passed else "FAIL"}** W7 point gates. Historical original-relative gates: '+('PASS' if all(g['pass'] for g in original_gates[n].values()) else 'FAIL')+' (historical reference, not a same-session original run).')
    lines += ['', f'The same-session baseline has {len(baseline_differences)} normalized transcript differences from the earlier isolated K64 validation; details are preserved in results.json.', '',
              '## What was stored and changed', '',
              'All five frontend ROM hashes match K64. The 2,074,560 FP32 ROM coefficients comprise 2,073,600 weights plus 960 biases. Only the three weight tensors were requantized; biases retain their exact FP32 bytes. Tensor names, shapes, hashes and ROM mapping are in frontend-inventory.json.', '',
              'Symmetric quantization uses FP32 absmax/127 scales, nearest-even rounding and clipping to [-127,127], with zero offset. Output axes are linear axis 1, Conv1 axis 0 and Conv2 axis 0. Per-tensor uses one scale for each of the three tensors. Saved INT8 blobs plus FP32 scales independently decode to the exact inference weights. No fitting or calibration was used.', '',
              '| Storage | Original ROM bytes | New INT8 weights + scales + FP32 biases |', '|---|---:|---:|']
    for n,v in variants.items(): lines.append(f'| {n} | 8,298,240 | {v["total_frontend_coefficient_storage_bytes"]:,} = {v["int8_weight_bytes"]:,} + {v["fp32_scale_bytes"]:,} + 3,840 |')
    lines += ['', 'The source model already stores these weights as INT8 codes with FP32 multiplicative scales and additive offsets; Conv2 scales are along input channels. The chip fixture stores their expanded FP32 values. Preserving that source representation is a separate possible exact-storage design; W7 measures the specifically requested symmetric re-quantization.', '',
              '## Execution and proof scope', '',
              'The wrapper reuses evaluate_stt_isolated.run_case, stt_metrics and the exact rational gate. Its only runner adaptations redirect outputs to this workspace and launch a local copy of isolate_native_worker.py with its single-thread environment assertion changed. All original scripts are untouched. OMP/BLAS/native ORT are set to one thread, one child at a time, under nice. The full saved worker and effective runner are provided.', '',
              'Only frontend.weights.ort is replaced for each variant, with a loader returning the saved dequantized constants under the identical output names/shapes. Its graph serialization changes; every other runtime file, including frontend.model.ort, encoder, decoder, affine metadata, tokenizer and streaming configuration, is byte-identical to K64. CPU ORT output equality is checked. Same-session baseline uses unmodified K64 files. Input hashes and saved NPY hashes match all 48 frozen validation inputs; returned PCM crops match across arms.', '',
              'All predictions, close markers, failures if any, input/model hashes and timings are preserved. No candidate was tuned or chosen using this run. These are additional development-validation exposures, not a fresh held-out test. Small read-speech/synthetic-noise point gates do not prove population retention, one-die fit, sub-watt power, timing, or an implemented INT8 hardware dequantizer.', '',
              'Root plan.md was absent. The skill, supplied notes, accuracy workflow, relevant local patent excerpts and named evaluator/requirement reports were consulted; no new circuit assumptions are made.', '',
              'Reproduction: `env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 nice -n 10 .venv/bin/python overnight-20261014/accuracy-int8/prepare.py`, then the same command with `run.py`. Scripts intentionally refuse to overwrite this completed run; use a separate authorized workspace for a future repetition.', '']
    (WORK/'RESULTS.md').write_text('\n'.join(lines))
    print('W7-STATUS: Step 4 complete; '+json.dumps(result['passes_W7_point_gates']),flush=True)
    print(json.dumps(summary,indent=2),flush=True)

if __name__ == '__main__': main()
