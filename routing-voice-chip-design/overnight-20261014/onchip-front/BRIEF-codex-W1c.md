# Codex brief W1c — move the frontend coefficients and position table on-chip

This is a parallel split of brief W1. Read it first: `overnight-20261014/onchip/BRIEF-codex-W1.md`. It has the same background, method, success criterion, constraints and authorization; the user lifted the 13 Oct pause on 14 Oct and `AGENTS.md` records that. Differences for you:

- **Your services:**
  - Frontend immutable scalar regions 0,1,4,5,8: 8,298,240 B, served in `frontend_services.hpp`. These are native FP32 coefficients; keep them bit-exact FP32.
  - Producer fixed positions: 1,310,720 B, served in `producer_services.hpp`. An RTL ROM with passed isolated controls already exists in `experiments/runtime-source-position-immutable-rom-source-20261013-v1/` and the related `experiments/runtime-source-position-*` dirs; reuse it.
  Do ONLY these. W1 is doing the decoder services (`overnight-20261014/onchip/`) and W1b the encoder services (`overnight-20261014/onchip-enc/`); do not write in their folders.
- **Template:** W1 has already built a working pattern. Copy and adapt it (read-only):
  - `onchip/prepare_group_a.py`: ROM hex generation, host-copy patching, commands
  - `onchip/rv_allonchip_top_v1.sv`: wrapper
  - `onchip/rv_onchip_decoder_*_v1.sv`: responders
  - `onchip/run_stage.py`, `onchip/responder_test.cpp`, `onchip/FAILURES.md`
- **Your workspace (write ONLY here):** `overnight-20261014/onchip-front/`. Objects/binaries go under `~/.local/state/routevoice-internal-runs/20261014/onchip-front/`.
- **What to build:**
  - Your OWN wrapper `rv_allonchip_top_w1c`: the existing top unchanged, plus your responders.
  - Your own host copy, with only your services switched to check-only mode.
  - Then run the F64 `fixture` and `positive` stages.
- **Success:** the same 5 tokens through EOS, all 18 output comparisons, and the render "Switch on the lights", with host_replies=0 and mismatches=0 for your services.
- **Merging:** the lead merges afterwards. Keep host changes confined to your services, and list every change in `RESULTS.md`.
- **CPU is shared:** use `nice`, at most 6 compile jobs, and only one long simulation at a time.
- Print `W1c-STATUS: ...` after each major step. Finish with `overnight-20261014/onchip-front/RESULTS.md`.
