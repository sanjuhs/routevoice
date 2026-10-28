import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from evaluate_reserved_k64_test import cluster_intervals


def test_paired_speaker_resampling_preserves_pair_and_clean_noise_draws():
    rows=[]
    for condition in ['clean','other','white_noise_10db']:
        for speaker in ['a','b','c']:
            for clip in range(2):
                for model in ['original','k64']:
                    rows.append({'condition':condition,'id':speaker+str(clip),'speaker':speaker,'model':model,
                        'edits':ord(speaker)-97+int(model=='k64'),'reference_words':10})
    result=cluster_intervals(rows,1000,2)
    assert result['clean']['seed']==result['white_noise_10db']['seed']
    assert result['clean']['candidate_wer_percentile95']==result['white_noise_10db']['candidate_wer_percentile95']
    for condition in result.values():
        assert all(abs(value-.1)<1e-12 for value in condition['paired_delta_wer_percentile95'])
        assert condition['speaker_count']==3
    assert result==cluster_intervals(rows,1000,2)
