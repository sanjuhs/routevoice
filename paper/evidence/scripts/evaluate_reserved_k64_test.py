#!/usr/bin/env python3
"""One frozen K64 candidate test; no fitting, reselection or favorable reruns."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import soundfile as sf
import evaluate_stt_isolated as isolated
from audit_native_reproducibility import ROOT, sha, write_new
from stt_metrics import aggregate, noisy

NAME = 'codebook-4bit-optimal-rectangular-k64'
BUILD = ROOT/'build/taalas-k64-reserved-test-v1'
PROTOCOL = ROOT/'reports/taalas-k64-reserved-test-protocol-v1.json'
SCORES = ROOT/'reports/taalas-k64-reserved-test-scores-v1.json'
DECISION = ROOT/'reports/taalas-k64-reserved-test-decision-v1.json'


def cluster_intervals(rows, repetitions=10000, base_seed=20260919):
    results={}
    for condition in ('clean','other','white_noise_10db'):
        rr=[r for r in rows if r['condition']==condition]
        original={r['id']:r for r in rr if r['model']=='original'}
        candidate={r['id']:r for r in rr if r['model']=='k64'}
        assert original.keys()==candidate.keys()
        speakers=sorted({r['speaker'] for r in original.values()})
        grouped=[]
        for speaker in speakers:
            ids=[key for key,r in original.items() if r['speaker']==speaker]
            grouped.append([sum(original[i]['edits'] for i in ids),sum(candidate[i]['edits'] for i in ids),sum(original[i]['reference_words'] for i in ids)])
        table=np.asarray(grouped,dtype=np.int64)
        # Clean and its noisy copies share speaker draws; other has a separate stratum.
        stratum='test-other' if condition=='other' else 'test-clean'
        seed=int.from_bytes(hashlib.sha256(f'taalas-reserved-test-speaker-bootstrap-v1:{base_seed}:{stratum}'.encode()).digest()[:8],'little')
        draws=np.random.default_rng(seed).integers(0,len(speakers),size=(repetitions,len(speakers)))
        totals=table[draws].sum(axis=1)
        reference=totals[:,0]/totals[:,2];current=totals[:,1]/totals[:,2];delta=current-reference
        quantile=lambda values:np.quantile(values,[.025,.975],method='linear').tolist()
        results[condition]={'speakers':speakers,'speaker_count':len(speakers),'resamples':repetitions,'seed':seed,
            'original_wer_percentile95':quantile(reference),'candidate_wer_percentile95':quantile(current),
            'paired_delta_wer_percentile95':quantile(delta),'cluster_sufficient_statistics_original_errors_candidate_errors_words':grouped,
            'scope':'Paired speaker-cluster percentile95% interval for micro-WER; both clips per resampled speaker retained. Marginal intervals, not simultaneous or a replacement acceptance gate.'}
    return results


def freeze():
    validation_path=ROOT/'reports/taalas-isolated-k64-validation-decision-v1.json'
    decision=json.loads(validation_path.read_text());assert decision['candidate_passes_frozen_accuracy_gates']
    assert decision['total_development_candidate_validation_exposures']==13
    previous=ROOT/'reports/taalas-isolated-k64-validation-protocol-v1.json'
    parent=json.loads(previous.read_text());isolated.pinned_check(parent)
    manifest_path=ROOT/'reports/stt-evaluation-manifest.json';manifest=json.loads(manifest_path.read_text())
    requirements_path=ROOT/'reports/stt-requirements.json';requirements=json.loads(requirements_path.read_text())
    limits=requirements['pilot_accuracy_limits']
    assert {c:limits[c+'_max_wer'] for c in ['clean','other','white_noise_10db']}=={'clean':.15,'other':.35,'white_noise_10db':.4}
    assert limits['candidate_max_absolute_wer_increase']==.02 and 'final test once' in limits['selection']
    assert not any('test' in k.lower() and 'limit' in k.lower() for k in requirements)
    clips=[c for c in manifest['clips'] if c['role']=='test'];assert len(clips)==80 and len({c['speaker'] for c in clips})==40
    other_speakers={c['speaker'] for c in manifest['clips'] if c['role']!='test'}
    assert not other_speakers & {c['speaker'] for c in clips}
    BUILD.mkdir();inputs_dir=BUILD/'inputs';inputs_dir.mkdir()
    inputs=[]
    for clip in clips:
        assert sha(ROOT/clip['path'])==clip['sha256']
        signal,sr=sf.read(ROOT/clip['path'],dtype='float32');assert sr==16000 and signal.ndim==1
        condition='clean' if clip['source_split'].endswith('clean') else 'other'
        variants=[(condition,signal)]
        if condition=='clean':variants.append(('white_noise_10db',noisy(signal,clip['id'])))
        for condition,audio in variants:
            index=len(inputs);target=inputs_dir/f'input-{index:03}.npy';np.save(target,audio,allow_pickle=False)
            inputs.append({'input_index':index,'id':clip['id'],'role':'test','speaker':clip['speaker'],
                'condition':condition,'seed':None,'partitions':['test'],'reference':clip['reference'],
                'source_path':clip['path'],'source_sha256':clip['sha256'],'signal_file':str(target),
                'signal_file_sha256':sha(target),'input_float32_sha256':hashlib.sha256(audio.tobytes()).hexdigest()})
    assert len(inputs)==120
    historical_path=ROOT/'reports/stt-baseline-pilot-v1.json'
    historical=json.loads(historical_path.read_text())
    # Read only historical identity fields for this guard; no historical hypotheses/scores guide anything.
    old={(r['id'],r['condition']):r['input_float32_sha256'] for r in historical['rows'] if r['role']=='test'}
    now={(r['id'],r['condition']):r['input_float32_sha256'] for r in inputs};assert old==now
    candidate_path=ROOT/'models/candidates'/NAME/'candidate.json';candidate=json.loads(candidate_path.read_text())
    for f in candidate['model_files']:assert sha(candidate_path.parent/f['file'])==f['sha256']
    exports=[{'file':r['packed_file'],'sha256':r['packed_sha256']} for r in candidate['changed_tensor_records']]
    for r in exports:assert sha(candidate_path.parent/'packed'/r['file'])==r['sha256']
    pinned=[Path(__file__),ROOT/'scripts/isolate_native_worker.py',ROOT/'scripts/evaluate_stt_isolated.py',
        ROOT/'scripts/audit_native_reproducibility.py',ROOT/'scripts/stt_metrics.py',manifest_path,requirements_path,
        validation_path,previous,candidate_path,ROOT/'reports/taalas-isolated-k64-calibration-export-audit-v1.json',historical_path,
        ROOT/'reports/taalas-native-isolation-verification-v1.json',ROOT/'tests/test_reserved_test_intervals.py']
    protocol={'schema_version':1,'status':'Frozen before the first candidate reserved-test inference',
        'candidate':NAME,'candidate_count':1,'candidate_manifest_sha256':sha(candidate_path),'packed_exports':exports,
        'models':parent['models'],'inputs':inputs,'expected_calls':240,'workers':2,'maximum_seconds_per_process':45,
        'native_library_sha256':parent['native_library_sha256'],'BLAS_environment':parent['BLAS_environment'],
        'inference_contract':'One fresh process/native controller per independent clip/condition, original defaults, flags0, no explicit native single-thread override, original model and candidate byte hashes fixed; exact returned PCM/crops must match across models.',
        'gate_limits':limits,'performance_contract':requirements['performance'],
        'test_contract_audit':{'manifest_role':'80reservedtestclips/40project-held-outspeakers,40test-clean+40test-other;40deterministicnoisyclean variants',
            'threshold_location':'reports/stt-requirements.json:pilot_accuracy_limits; the contract provides shared pilot limits and explicitly says final test once for a preselected candidate. The data manifest defines roles/inputs but no separate test-specific threshold override.',
            'callable_gate':'scripts/evaluate_stt_isolated.py:gate, pinned; exact rational comparisons against unchanged clean15%,other35%,noise40%,and +2pp candidate-relative ceiling each condition.',
            'historical_input_hashes_match_all120_test_conditions':True,
            'selection_before_test':'K64passed unchanged corrected development gates; candidate choice and allfiles fixed before test inference.'},
        'uncertainty':{'method':'Paired speaker-cluster percentile bootstrap of micro-WER and candidate-minus-original WER. Resample20speakers with replacement within each clean/other source stratum, keep both utterances and original/candidate pairing; clean/noisy conditions reuse identical speaker draws.',
            'resamples':10000,'base_seed':20260919,'interval_percentiles':[2.5,97.5],'numpy_quantile_method':'linear',
            'scope':'Marginal95% descriptive intervals; not simultaneous coverage, not a gate change, not a p-value or a correction for unknown pretraining overlap and all prior development exploration.'},
        'integrity_gate':'All240processes exit0 with complete result/closemarker, request/model/source hashes match, no cross-model returned PCM/crop mismatch; otherwise report failure without replacing or rerunning inconvenient rows.',
        'post_test_policy':'Exactly one candidate reserved test. No fitting, candidate reselection, gate/noise changes, favorable reruns or test-driven recovery from these results. Preserve failures and all predictions.',
        'history':{'candidate_development_validation_exposures':13,'prior_candidate_test_runs':0,
            'original_historical_test_exists':True,'test_not_claimed_never_evaluated':True},
        'limits':['Bounded human read speech and synthetic white noise; not general-product, road/helmet or continuous-stream proof.',
            'Upstream source-model training overlap unknown. Test speakers are disjoint only within this project.',
            'Aggregate host RTF is recorded from inference compute; fresh-process load time is separate. Live streaming latency, FPGA/ASIC timing and power remain unmeasured.',
            'Four-bit indices intoUINT8representatives retain originalINT8frontend/floating operators. Model quality does not prove die fit or sub-watt operation.'],
        'pinned_files':[{'path':str(p),'sha256':sha(p)} for p in pinned]}
    write_new(PROTOCOL,protocol);print(json.dumps({'protocol_sha256':sha(PROTOCOL),'calls':240,'candidate_frozen':NAME},indent=2))


def run():
    p=json.loads(PROTOCOL.read_text());isolated.pinned_check(p)
    if (BUILD/'test').exists() or SCORES.exists():raise ValueError('Candidate reserved test cannot be repeated')
    isolated.BUILD=BUILD;cases=[];rows=[];start=time.monotonic()
    tasks=[('test',name,item,p) for item in p['inputs'] for name in p['models']]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for status,row in pool.map(isolated.run_case,tasks):
            cases.append(status)
            if row is not None:rows.append(row)
            if len(cases)%16==0:
                print(json.dumps({'completed':len(cases),'expected':240}),flush=True)
                (BUILD/'test'/'progress.json').write_text(json.dumps({'cases':cases,'rows':rows},indent=2)+'\n')
    reference={r['input_index']:r for r in rows if r['model']=='original'}
    failures=[c for c in cases if c.get('exit_code')!=0 or not c['close_complete']]
    mismatches=[r['case_id'] for r in rows if r['input_index'] not in reference or r['segment_pcm_boundary_sha256']!=reference[r['input_index']]['segment_pcm_boundary_sha256']]
    summary={name:aggregate([r for r in rows if r['model']==name]) for name in p['models']}
    report={'schema_version':1,'protocol_sha256':sha(PROTOCOL),'candidate':NAME,'candidate_test_runs':1,
        'integrity_passed':len(rows)==len(cases)==240 and not failures and not mismatches,
        'recorded_calls':len(rows),'process_failures':failures,'PCM_mismatches_vs_original':mismatches,
        'summary':summary,'rows':rows,'cases':cases,'elapsed_seconds':time.monotonic()-start}
    write_new(SCORES,report);print(json.dumps({'integrity_passed':report['integrity_passed'],'summary':summary},indent=2))


def decide():
    p=json.loads(PROTOCOL.read_text());isolated.pinned_check(p);s=json.loads(SCORES.read_text())
    assert s['protocol_sha256']==sha(PROTOCOL)
    gates=isolated.gate(s['summary']['k64'],s['summary']['original'],['clean','other','white_noise_10db'],p['gate_limits'])
    intervals=cluster_intervals(s['rows'],p['uncertainty']['resamples'],p['uncertainty']['base_seed']) if s['integrity_passed'] else None
    report={'schema_version':1,'candidate':NAME,'protocol_sha256':sha(PROTOCOL),'scores_sha256':sha(SCORES),
        'candidate_manifest_sha256':p['candidate_manifest_sha256'],'integrity_passed':s['integrity_passed'],
        'test_accuracy_gates':gates,'passes_frozen_test_accuracy_gates':s['integrity_passed'] and all(g['pass'] for g in gates.values()),
        'paired_uncertainty':intervals,'host_aggregate_RTF':{name:sum(r['compute_seconds'] for r in s['rows'] if r['model']==name)/sum(r['audio_seconds'] for r in s['rows'] if r['model']==name) for name in p['models']},
        'RTF_limit':p['performance_contract']['aggregate_rtf_max'],'live_streaming_latency_checked':False,
        'candidate_development_validation_exposures':13,'candidate_reserved_test_runs':1,
        'original_historical_test_exposure_preserved':True,'no_test_driven_model_changes_or_reselection':True,
        'physical_fit_power_or_product_generalization_proven':False,'limits':p['limits']+[p['uncertainty']['scope']]}
    write_new(DECISION,report);print(json.dumps({'decision_sha256':sha(DECISION),'passes':report['passes_frozen_test_accuracy_gates'],'gates':gates,'uncertainty':intervals},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['freeze','run','decide']);a=parser.parse_args()
    {'freeze':freeze,'run':run,'decide':decide}[a.command]()
