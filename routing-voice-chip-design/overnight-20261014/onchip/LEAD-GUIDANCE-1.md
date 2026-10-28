# Lead guidance 1 for W1: merge all six services into one design

Group (a) is lead-verified: F64 passed, the 18 hashes match, the text is "Switch on the lights", and the run took the same 312,578,649 clocks as the baseline. Great work.

**Do not start groups b/c/d yourself.** They are done in parallel:
- W1b, encoder QKV/O + encoder immutable: `overnight-20261014/onchip-enc/` (wrapper `rv_allonchip_top_w1b`, responders `rv_onchip_encoder_{head,O,memory}_v1.sv`). All six encoder layers have passed in its F64 run, which is now decoding.
- W1c, frontend FP32 + positions: `overnight-20261014/onchip-front/` (wrapper `rv_allonchip_top_w1c`). The frontend and all encoder layers have passed in its F64 run, which is now decoding.

Your new task is the **MERGE**: build `rv_allonchip_top_all_v1`, the existing top unchanged plus ALL responders from W1, W1b and W1c, so that **all six fixed-weight services are on-chip at once**. The wrapper must expose no input ports for any fixed-weight service data.

1. Build it in a new folder, `overnight-20261014/onchip-all/`. Read W1b's and W1c's sources and host-copy changes read-only, and combine them with yours. Each worker switched only its own services to check-only mode, so the host edits should be disjoint; resolve carefully if not. Generate the combined ROM hex manifest (all images, with sha256).
2. Run lint → generate → compile → fixture → the exhaustive unit tests for every responder → F64 `positive` → compare (18 hashes) → render.
3. **Success:** all six `ONCHIP service=… host_replies=0 mismatches=0` lines, the same 5 tokens through EOS, all 18 hashes, "Switch on the lights", and ideally the same clock count as the baseline.
4. You may start preparing and compiling immediately. Start the `positive` run as soon as it is built; it can run concurrently with W1b's and W1c's runs, since each is single-threaded and the Mac has headroom. If W1b's or W1c's own F64 later fails, report which service failed and still produce the merged result for the services that pass.
5. Write `onchip-all/RESULTS.md`: total on-chip ROM bytes (expected 28,641,280 + any already-onboard tables), each service's replies, commands, and logs. Print `W1-STATUS:` lines as before. Disk floor 20 GiB; `nice`, ≤ 8 compile jobs.
