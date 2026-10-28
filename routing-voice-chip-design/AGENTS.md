# Active Routing Voice architectural instructions

**21 October 2026: resumed by the user, target release Friday 23 October.** The user asked Claude to finish the end-to-end work using parallel Codex workers. Briefs are in `overnight-20261014/finish-1023/`:
- W10: route the local-partials engine to signoff and measure routed power (pod);
- W11: Taalas index+codebook storage through the full recognizer, with F64 bit-exact;
- W12: full-recognizer synthesizability, chip and FPGA.

The RunPod remainder of the original $30 is authorized (guard cap $28 total, stop Fri 23 Oct 18:00 IST).

**16 October 2026: physical goal PAUSED by the user.** Stop all P&R/EDA runs; resume only when the user says so. Proven so far:
- The fanout-16 1280×320 engine closes timing at 150 ns in all corners post-CTS.
- Local per-group partial products (`overnight-20261014/engine-buffered/rtl/engine_local.sv`) pass the 54-vector RTL bench identically, and cut global-route overflow by 92% (3.37M → 260k).

The full route (`d4-full`) did not converge, and the global-route question is still open: full GRT reached 767k overflow vs 260k for the 3-iteration diagnostic.

Next, if resumed: D4 at ≈30–35% density with post-GPL repair on, and a short diagnostic before any full route.

Archive: `/Volumes/Extreme Pro Dev/routevoice-checkpoints/overnight-20261014/lead-route-150ns/` (see `PAUSED-2026-10-14.md` and `CONGESTION-DIAG-2026-10-15.md` there).

**14 October 2026 — pause lifted by the user (in chat with Claude):** The user approved `docs/ROUTEVOICE-PROPOSED-PHYSICAL-GOAL-2026-10-13.md` and authorized an autonomous overnight run led by Claude with Codex workers and subagents. Its scope: (1) the proposed complete GF180 projection with the actual weight fabric, routed area, timing and power; (2) moving all host-served fixed-weight services on-chip in the full-recognizer RTL; (3) a whole-chip floorplan with power distribution; (4) a full-top synthesizability check. Compilation, EDA, simulations, parallel workers and RunPod CPU pods are authorized for this run, with **$30 of new RunPod spending** (separate from earlier spend) under a hard guard. Briefs and progress: `overnight-20261014/` and root `OVERNIGHT-PROGRESS.md`. The older 13 October pause text is superseded; the record of it is in `reports/routevoice-user-pause-20261013.md`.

The user's 1 October storage instruction is explicit: run computation and keep active experiment inputs/output on the Mac's internal filesystem. Use the external SSD for backups, saved checkpoints and offloading old artifacts. A path under the SSD-linked `build` directory is archival storage, not an active EDA working directory. The reviewed internal working set at `/Users/sanju/.local/state/routevoice-internal-runs/20260928/chip` is available for the retained encoder experiments; preserve its frozen inputs.

The user's selected direction is the existing Moonshine Tiny Streaming English model with four-bit codebook selections, specialized into Taalas-inspired shared products and frozen physical connections. Target one 180 nm die and sub-watt STT; these are objectives to test, not established results. Use native local tools by default; RunPod CPU pods are authorized for the 14 October run within its $30 cap.

Before architecture, feasibility or routing work, read `skills/taalas-fixed-weight-routing/SKILL.md`, its complete `references/source-notes.md`, the relevant primary patent texts, and the current root `plan.md`. The installed personal copy is `/Users/sanju/.codex/skills/taalas-fixed-weight-routing/SKILL.md`. Every subagent participating in this work must receive and follow the same reading requirement. Include it explicitly in delegation prompts and request a source-reading confirmation.

Study the actual patent mechanism: shared coefficient products, fixed selection identity, row/read control, serial or parallel digital transport and accumulation. The one-access-transistor readable-cell embodiment is explicit patent content; its full physical cost needs characterization. SRAM-sized weight storage is a comparator, not the primary architecture and not grounds for rejecting the routing design.

Index width, representative precision, activation precision and accumulator width are separate. Preserve source zero points/scales and derive valid shared corrections. Four-bit numerical activations are not required to investigate four-bit pointers. Keep dynamic attention and writable state in the full design.

Preserve original model artifacts, supplied research text and dated failures. Do not require a smaller replacement model before testing the existing model's topology. Do not report parameter-count ratios as measured area/power reductions, or a small tile as a complete recognizer.

Keep the repository skill and installed personal skill synchronized when revising this project-specific workflow. The skill adds no authority for unrelated external actions or cloud spending.
