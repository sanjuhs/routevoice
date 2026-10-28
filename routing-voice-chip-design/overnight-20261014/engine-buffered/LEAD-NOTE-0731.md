# Lead note 07:31 IST for W9

- The lead ran your already-compiled `gate-activity/sim` directly at 07:16, because it was queued behind the unsharded full replay.
  - It passed: 1 vector, 320 outputs, 4,163 cycles, 0 stalls.
  - SAIF copied to the pod at `/workspace/rv/overnight-20261014/power-bufv4/bufv4-mapped-speech.saif`.
- Pre-route power on `buf-v4/23-openroad-globalplacement` with your ideal-prects SDC: 1,299,526 of 1,299,526 pins annotated, 0.798 W, ≈66.4 µJ per projection, ≈162 pJ/MAC.
  - Details: `overnight-20261014/power-bufv4/RESULTS.md`. Cite it; don't duplicate it.
- The pod is terminated at ≈07:55 IST. Copy any pod results you want to keep into the local `engine-buffered/` by 07:50, and finalize `RESULTS.md` + `results.json` with what actually completed.
