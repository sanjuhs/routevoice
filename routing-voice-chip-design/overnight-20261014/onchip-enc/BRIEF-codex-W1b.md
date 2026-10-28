# Codex brief W1b — move the encoder weight services on-chip

This is a parallel split of brief W1. Read it first: `overnight-20261014/onchip/BRIEF-codex-W1.md`. It has the same background, method, success criterion, constraints and authorization; the user lifted the 13 Oct pause on 14 Oct and `AGENTS.md` records that. Differences for you:

- **Your services:** encoder QKV head/O fixed rows (2,457,600 B) and encoder immutable memory regions 4..12 (5,146,880 B), both served in `encoder_services.hpp`. Do ONLY these. Worker W1 is doing the decoder services in `overnight-20261014/onchip/`; do not write there. Worker W1c is doing frontend + positions.
- **Template:** W1 has already built a working pattern. Copy and adapt it (read-only):
  - `onchip/prepare_group_a.py`: ROM hex generation, host-copy patching, commands
  - `onchip/rv_allonchip_top_v1.sv`: wrapper
  - `onchip/rv_onchip_decoder_*_v1.sv`: responders
  - `onchip/run_stage.py`, `onchip/responder_test.cpp`, `onchip/FAILURES.md`
  Check its latest state when you start; it may have progressed.
- **Your workspace (write ONLY here):** `overnight-20261014/onchip-enc/`. Objects/binaries go under `~/.local/state/routevoice-internal-runs/20261014/onchip-enc/`.
- **What to build:**
  - Your OWN wrapper `rv_allonchip_top_w1b`: the existing top unchanged, plus your responders.
  - Your own host copy, with only your services switched to check-only mode.
  - Then run the F64 `fixture` and `positive` stages.
- **Success:** the same 5 tokens through EOS, all 18 output comparisons, and the render "Switch on the lights", with host_replies=0 and mismatches=0 for your services.
- **Merging:** the lead will merge the W1/W1b/W1c wrappers afterwards. Keep your host changes confined to your services' code, and list every change in `RESULTS.md`.
- **CPU is shared by several workers:** use `nice`, at most 6 compile jobs, and only one long simulation at a time from you.
- Print `W1b-STATUS: ...` after each major step. Finish with `overnight-20261014/onchip-enc/RESULTS.md`.
