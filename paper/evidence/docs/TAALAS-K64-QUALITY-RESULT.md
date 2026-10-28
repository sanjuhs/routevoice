# K64 passes the frozen pilot accuracy gates

The unchanged-size Moonshine candidate
`codebook-4bit-optimal-rectangular-k64` passes both corrected development
validation and its **single reserved candidate test**. Every one of the
31,457,280 eligible weight positions uses a four-bit local index. The original
INT8 frontend and floating operators remain; this is not W4A4 inference.

This establishes the declared pilot point-estimate accuracy gate. It does not
establish a population-wide accuracy guarantee, single-die fit, sub-watt power,
continuous-stream behavior or FPGA execution. The noisy-test margin is small.

## Fixed candidate, selection and development history

K64 was an already preserved candidate. No new fitting, parameter removal,
precision exemption or bias correction occurred in this comparison. Integer
projections use at most sixteen UINT8 representatives per output and contiguous
64-input group; the tied embedding uses corresponding feature blocks within
each vocabulary row, with an exact output-table transpose alias. Source scales,
zero points and all 386 other source initializers remain unchanged.

An independent export audit decoded all 98 packed records and checked the
expanded runtime weights and tied alias. It counted 491,520 local books,
15,728,640 packed-index bytes and 7,765,892 representative bytes. The ideal
logical payload including unchanged initializers is **25,987,246 bytes**, which
is 3,248,640 bytes (14.29%) larger than K128. This is a logical representation
cost, not physical memory area. Local sixteen-entry books do not imply a global
sixteen-entry product bank; book mapping and shared-product selection require
their actual hardware cost.

The isolated calibration protocol was frozen before inference. It required
unchanged legacy clean/noise eligibility, then a strict improvement over K128's
original-relative held-noise rank: minimize worst delta across 20/10/5 dB, then
mean delta, then representative bytes. K64 qualified on the same input hashes.

| Calibration errors, 268 words per condition | Original | K128 | K64 |
|---|---:|---:|---:|
| Clean | 17 | 19 | 15 |
| Legacy noise 10 dB | 45 | 45 | 44 |
| Held noise 20 dB | 23 | 32 | 25 |
| Held noise 10 dB | 50 | 53 | 58 |
| Held noise 5 dB | 70 | 88 | 74 |

The worst held-noise increase fell from 18 to 8 errors. K64's held 10 dB result
is worse than K128's, but the predeclared worst-then-mean ranking selects K64.
The held noisy variants share the same 16 calibration utterances; they are not
new independent speakers or linguistic samples. Only after saving the hashed
selection decision did K64 receive one development validation.

| Development validation | Original errors / words | K64 errors / words | Increase | Gate |
|---|---:|---:|---:|---|
| Clean | 16/330 (4.85%) | 22/330 (6.67%) | +1.82 pp | Pass |
| Other | 62/325 (19.08%) | 59/325 (18.15%) | −0.92 pp | Pass |
| Noise 10 dB | 58/330 (17.58%) | 64/330 (19.39%) | +1.82 pp | Pass |

The clean/noise development margin is less than one edit: one additional error
would fail retention. This is the **13th candidate development-validation
exposure** across the preserved research history. Earlier failed candidates and
the original reused-controller reports remain intact. The corrected original
development texts and PCM hashes exactly matched the preceding isolated
reference run, checked without substituting results.

## One reserved candidate test

Before any candidate test inference, the exact candidate manifest, eight runtime
files, all 98 packed exports, evaluator, normalization, original model, input
manifest, requirements and calibration/development decisions were frozen by
hash. All 120 test condition input hashes match the historical original test
identities. The numerical test requirements are the shared pilot limits in
`reports/stt-requirements.json`: absolute WER ceilings of 15%, 35% and 40%, plus
at most **2 percentage points increase in each condition**. The manifest defines
test roles but contains no separate threshold override. Gates use exact rational
error-count comparisons.

The test includes 80 utterances from 40 project-held-out speakers: 40 clean and
40 other, two per speaker. The 40 clean utterances also have the unchanged
deterministic 10 dB white-noise condition. K64 and a fresh original reference ran
all 120 conditions once each, using one fresh native process per condition.

| Reserved test | Original errors / words | K64 errors / words | Increase | Gate |
|---|---:|---:|---:|---|
| Clean | 37/869 (4.26%) | 39/869 (4.49%) | +0.23 pp | Pass |
| Other | 100/785 (12.74%) | 107/785 (13.63%) | +0.89 pp | Pass |
| Noise 10 dB | 121/869 (13.92%) | 137/869 (15.77%) | +1.84 pp | Pass |

The noisy gate allows at most 138 candidate errors: one more would still pass,
two more would fail. No fitting, model reselection, favorable reruns, noise
changes or test-driven recovery followed this result. The reserved candidate
test count is now **one**. The original model had a historical test evaluation;
the test was reserved for candidates, not literally never evaluated.

## Integrity, uncertainty and limits

All 240 processes exited successfully, with complete results and close markers;
there were no missing/replaced rows or cross-model PCM/crop differences. The
test took 41.27 seconds with two local workers. Aggregate host inference RTF was
0.02311 for original and 0.02320 for K64, below the frozen limit of 1. Process
startup/load time is separate; live streaming latency and ASIC throughput/power
were not measured. Earlier native teardown failures remain preserved.

The fresh-process contract corrects a demonstrated native VAD call-order effect:
identical API audio previously could yield a 32 ms crop difference after another
utterance. Three independent repetitions established stable isolated execution
before the corrected scoring began. This independent-utterance reset policy is
not a proposed reset of every chunk in a continuous audio stream.

Uncertainty was predeclared before test inference: 10,000 paired speaker-cluster
bootstrap draws, retaining both clips for each resampled speaker and keeping
original/candidate pairs together. Clean and noisy copies use the same speaker
draws; clean/other source strata are resampled separately. The intervals below
are marginal 95% percentile intervals for micro-WER differences.

| Condition | Candidate-minus-original WER interval |
|---|---:|
| Clean | −0.83 to +1.48 pp |
| Other | −1.51 to +3.19 pp |
| Noise 10 dB | −0.77 to +4.48 pp |

These intervals are descriptive, not simultaneous confidence bounds or a new
gate. Other/noisy upper endpoints exceed +2 pp, so the pilot pass does **not**
prove population-wide retention within that limit. Only 20 speakers contribute
to each source stratum. Synthetic white noise does not cover real road/helmet
noise; upstream model training overlap is unknown. Project speaker separation
does not establish separation from upstream pretraining.

The source skill, complete supplied notes and relevant primary P2 disclosure
were read. Local representative books and fixed pointers follow that permitted
architecture direction. Our scalar quantization, grouping and evaluation are
engineering choices, not claims that a patent guarantees speech quality or
reveals a commercial chip's exact implementation.

## Frozen evidence

The final machine-readable ledger is
`reports/taalas-k64-quality-summary-v1.json`, SHA256
`5489f74b2c11a06acf4ecebb4f8bfc8e02916c0d3aa60dbc639b518edd62948b`.
It contains exact runtime file hashes, export counts, decisions, test edit
margins and post-test independent score recount/integrity checks.

| Artifact | SHA256 |
|---|---|
| K64 candidate manifest | `a9ac4a4c9f51b65ebadf5b26b7c7fe0d3100d047ec4ad863f1b9d147b78870cc` |
| Calibration protocol | `c56e57879b3ce93a9021083da1a52d82ddea0c7f556921746bd43ae853b0fd01` |
| Export audit | `49d34f71b5533c96843af24272cdef5854ab6ec3f688a31fcc7b1043c071efb1` |
| Calibration decision | `d1618aa85b3d8c89501ed24c7b3490ed13b1f3055672ee38d0494f4d631d4281` |
| Development decision | `d56298677705577cdd8521449ccfa0126bafdbdbd43bfa2e92d6b7ea2317eceb` |
| Reserved test protocol | `5ca9f77789f76bab38a08c347309baae8add20021f883112b3909362c2372bb0` |
| Reserved test scores | `245c1af107e41411cd2ffb0bb200a041d1e1a2b3b8d6d669f361596eaa8d16fb` |
| Reserved test decision | `8ca29f9f55ab19108dea5bb06009d521c9beda0666face6f2bfddfb0ca370b56` |

Per-process requests, result files, returned original PCM and native logs remain
under `build/taalas-k64-reserved-test-v1/`. The evaluator has a no-repeat guard.
The paired-bootstrap fixture passed, and an independent read-only review found
no material resampling/gate-integrity issue. The final recount additionally
checks unique model/input pairs, exact shared reference words and speaker IDs.
