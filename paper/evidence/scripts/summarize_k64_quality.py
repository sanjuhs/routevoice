#!/usr/bin/env python3
"""Recount immutable K64 results and preserve their final evidence ledger."""
import json
from fractions import Fraction
from pathlib import Path

import evaluate_stt_isolated as isolated
from audit_native_reproducibility import ROOT, sha, write_new
from stt_metrics import aggregate, edits


def main():
    protocol_path = ROOT/'reports/taalas-k64-reserved-test-protocol-v1.json'
    score_path = ROOT/'reports/taalas-k64-reserved-test-scores-v1.json'
    decision_path = ROOT/'reports/taalas-k64-reserved-test-decision-v1.json'
    protocol = json.loads(protocol_path.read_text())
    scores = json.loads(score_path.read_text())
    decision = json.loads(decision_path.read_text())
    isolated.pinned_check(protocol)
    assert scores['protocol_sha256'] == sha(protocol_path)
    assert decision['scores_sha256'] == sha(score_path)
    assert scores['integrity_passed'] and decision['passes_frozen_test_accuracy_gates']
    directory = Path(protocol['models']['k64']['directory'])
    assert sha(directory/'candidate.json') == protocol['candidate_manifest_sha256']
    for item in protocol['packed_exports']:
        assert sha(directory/'packed'/item['file']) == item['sha256']
    inputs = {r['input_index']: r for r in protocol['inputs']}
    cases = {r['case_id']: r for r in scores['cases']}
    assert len(cases) == len(scores['rows']) == 240
    assert len({(r['model'], r['input_index']) for r in scores['rows']}) == 240
    for row in scores['rows']:
        item = inputs[row['input_index']]
        assert row['input_float32_sha256'] == item['input_float32_sha256']
        assert row['reference'] == item['reference'] and row['speaker'] == item['speaker']
        result = edits(row['reference'], row['hypothesis'])
        assert row['edits'] == result['edits'] and row['reference_words'] == result['reference_words']
        assert cases[row['case_id']]['exit_code'] == 0 and cases[row['case_id']]['close_complete']
    for model in protocol['models']:
        assert aggregate([r for r in scores['rows'] if r['model'] == model]) == scores['summary'][model]
    margins = {}
    for condition, gate in decision['test_accuracy_gates'].items():
        n = gate['reference_words']
        # Largest integer error count meeting both exact-rational acceptance gates.
        cap = min(Fraction(str(gate['absolute_ceiling']))*n,
                  gate['reference_edits']+Fraction(str(gate['retention_limit']))*n)
        maximum = cap.numerator//cap.denominator
        margins[condition] = {'maximum_passing_candidate_edits': maximum,
                              'additional_edits_allowed': maximum-gate['candidate_edits'],
                              'one_edit_percentage_points': 100/n}
    calibration = ROOT/'reports/taalas-isolated-k64-calibration-decision-v1.json'
    validation = ROOT/'reports/taalas-isolated-k64-validation-decision-v1.json'
    export = ROOT/'reports/taalas-isolated-k64-calibration-export-audit-v1.json'
    artifacts = [protocol_path, score_path, decision_path, calibration, validation, export,
                 ROOT/'scripts/evaluate_reserved_k64_test.py',
                 ROOT/'tests/test_reserved_test_intervals.py', Path(__file__)]
    report = {'schema_version': 1, 'candidate': protocol['candidate'],
        'candidate_manifest_sha256': protocol['candidate_manifest_sha256'],
        'model_files': protocol['models']['k64']['files'],
        'export': json.loads(export.read_text()),
        'calibration_selection': json.loads(calibration.read_text()),
        'development_validation': json.loads(validation.read_text()),
        'reserved_test': decision, 'test_edit_margins': margins,
        'post_test_audit': {'pinned_files_and_model_hashes_unchanged': True,
            'packed_export_hashes_rechecked': len(protocol['packed_exports']),
            'all_reference_and_hypothesis_scores_independently_recounted': True,
            'unique_model_input_pairs': 240, 'missing_or_replaced_rows': 0,
            'process_failures': 0, 'cross_model_PCM_or_crop_differences': 0},
        'elapsed_test_seconds': scores['elapsed_seconds'],
        'candidate_development_exposures': 13, 'candidate_reserved_test_runs': 1,
        'historical_original_test_exposure_preserved': True,
        'candidate_fit_or_reselection_after_test': False,
        'conclusion': 'The frozen K64 candidate passes the declared small-pilot development and reserved-test point-estimate gates. Paired intervals do not establish population-wide <=2pp retention for other/noisy speech. This is not an ASIC fit, power, continuous-stream or product validation.',
        'artifacts': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in artifacts]}
    target = ROOT/'reports/taalas-k64-quality-summary-v1.json'
    write_new(target, report)
    print(json.dumps({'summary_sha256': sha(target), 'test_margins': margins,
                      'elapsed_test_seconds': scores['elapsed_seconds']}, indent=2))


if __name__ == '__main__':
    main()
