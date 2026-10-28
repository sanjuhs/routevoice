# W14 supplemental GF180 physical checks

No READY or complete signoff claim. Built-in KLayout.DRC was skipped because its runset was unset; these checks execute the installed GF180 variant-D deck on frozen copies of exact final primary GDS.

| Run | Top | Main markers | Density markers | Antenna markers | Overall |
|---|---|---:|---:|---:|---|
| io_token_sequencer_resume | `rv_greedy_token_sequencer_v2` | 0 | 5 | 0 | failed |
| io_token_sequencer_retry | `rv_greedy_token_sequencer_v2` | 0 | 5 | 0 | failed |
| quantizer_value_signoff | `taalas_dql_value` | 0 | 5 | 0 | failed |

## io_token_sequencer_resume

Receipt: `runs/io_token_sequencer_resume/results.json`. GDS SHA-256: `3b1869b13aa9386ec3b3011c429d005c8e21b4a32886e4255de99d526e8b1418`.
- main: 651 categories, 0 violation items. Rules: {}.
- density: 5 categories, 5 violation items. Rules: {"'M2.4'": 1, "'M3.4'": 1, "'M4.4'": 1, "'M5.4'": 1, "'MT.3'": 1}.
- antenna: 11 categories, 0 violation items. Rules: {}.

## io_token_sequencer_retry

Receipt: `runs/io_token_sequencer_retry/results.json`. GDS SHA-256: `25de1c403a2e047c5e2477277f3ba3ac3b545d3985b8c52c51f0f3d08a74b9bf`.
- main: 651 categories, 0 violation items. Rules: {}.
- density: 5 categories, 5 violation items. Rules: {"'M2.4'": 1, "'M3.4'": 1, "'M4.4'": 1, "'M5.4'": 1, "'MT.3'": 1}.
- antenna: 11 categories, 0 violation items. Rules: {}.

## quantizer_value_signoff

Receipt: `runs/quantizer_value_signoff/results.json`. GDS SHA-256: `3ffd9f0b2633063c1ace7cfe3a654b486c644cd08371f69991e0bae70f4600a4`.
- main: 651 categories, 0 violation items. Rules: {}.
- density: 5 categories, 5 violation items. Rules: {"'M2.4'": 1, "'M3.4'": 1, "'M4.4'": 1, "'M5.4'": 1, "'MT.3'": 1}.
- antenna: 11 categories, 0 violation items. Rules: {}.

## Method and reproduction

No GDS modifications or density waivers. Density failures are actionable fill obligations, retained in each native report. Main, density and antenna must all pass; a skipped check receives no credit. Native runner exit, exact input/copy hashes, all PDK rule-deck hashes and dependency/wrapper hashes are recorded. Source hashes are checked again after each run.

The reusable wrapper accepts a W14 run path and top, plus optional unique `--label`; it refuses overwrite. One native KLayout worker and one thread execute at a time. Dependencies, snapshots, generated decks, caches, config and temporary files remain here. No Nix shell or build. The initial disk guard requires ≥22 GiB free.

Parser controls in `parser-tests/results.json` validate zero and nonzero item counts, and reject missing, malformed, wrong-root, wrong-top, category-free, items-free and uncategorized-item reports. These controls test result ingestion, not physical rule qualification.

```sh
/nix/store/yczxlrrywxp7q2aavm4b3zrj3lpmq18a-devshell-dir/bin/python3 overnight-20261014/finish-1023/w14-blocks/physical-audit/run_supplemental_drc.py overnight-20261014/finish-1023/w14-blocks/runs/<run> <top>
python3 overnight-20261014/finish-1023/w14-blocks/physical-audit/collect.py
```
