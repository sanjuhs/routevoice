# Proposed goal: one complete GF180 projection

**Status: APPROVED by the user on 14 October 2026 (in chat with Claude); executing in the overnight run — see `../OVERNIGHT-PROGRESS.md` at the repo root and `overnight-20261014/`.**
**Requested:** 13 October 2026. This priority replaces the corpus-first continuation.

## Goal for review

Implement one complete, representative projection from the frozen Moonshine Tiny Streaming English K64 model in GF180, including its actual fixed-weight selection fabric and every circuit required to deliver a correct result. Obtain routed area, extracted timing and activity-based power/energy before expanding to other projections, the full recognizer, more corpus coverage, or FPGA implementation.

The eventual objective remains a complete on-chip speech recognizer. This first experiment determines whether the proposed fabric is physically credible and what it costs. It is not a claim that a complete model fits, meets real-time throughput, or consumes less than 1 W.

## Selected projection for approval

Use the first encoder block's feed-forward output projection: **1,280 inputs by 320 outputs, 409,600 frozen weight positions**. Its graph node is `node_MatMul_86_quant`, weight tensor `val_89_quantized`, and bias `blocks.0.ff.project_out.bias`. The selected K64 evidence records 6,400 local books, four-bit indices, UINT8 representatives, signed nine-bit centered activation inputs, and FP32 scale/bias output processing. This is not a four-bit-activation model.

Reuse the numerical and arithmetic evidence in `reports/taalas-serial-word-nibble-k64-1280x320.json` and `reports/taalas-projection-nibble-k64-affine.json`. The existing arithmetic implementation left physical index storage and metadata delivery outside its measured boundary; this experiment must close those boundaries. Verify the saved tensor/model identities against the frozen candidate before execution. The selected primitive accepts the declared quantized activation interface; any upstream activation quantizer is explicitly outside this projection boundary and remains in the later whole-system budget.

## Time and usage proposal — no execution authorized

- First approval should cover a **60-minute readiness/planning session**, one agent, no background automation and no paid cloud work. Reuse the exact existing projection, inspect macro/tool availability, and produce the resource limits and missing-work list. Stop at the limit rather than silently expanding scope.
- A first bounded physical trial can then have a separately reviewed ceiling of **four hours of machine execution**, with no automatic retry. That is a stop budget, not a promise that a full route or custom macro can finish in four hours.
- Planning estimate only: a complete projection study could take **several working days to a few weeks**, principally depending on whether the custom array and its extracted timing/power views can be reused. Replace this range after the readiness review. Foundry signoff and fabrication are excluded.
- Use one agent by default and concise phase-end reports. New parallel agents, paid resources or recurring monitors require a new explicit request. Machine runtime and Codex usage are different quantities; there is no defensible conversion from EDA hours to a percentage of the account allowance.
- Finishing the experiment means a reproducible, honestly bounded physical result, including an explicit failure if targets cannot be met. A favorable feasibility verdict additionally requires the predeclared throughput/area/power budgets; those numerical budgets must be fixed before running, not selected after seeing the result.

## Pause and resource rules

- Stop current RouteVoice simulations, builds, subagents and queued work safely; preserve existing and partial evidence. Interrupted tests receive no pass credit.
- Keep all RouteVoice automations and the persistent execution goal paused. No background corpus job, monitoring loop, new agent, paid resource or new experiment while awaiting approval.
- During the pause, only minimal shutdown, preservation and requested planning are authorized. Do not turn preservation into a new large audit or build campaign.
- A future go-ahead applies to the reviewed scope; it does not automatically re-enable recurring automations or grant additional cloud spending.
- After approval, start with one bounded execution phase at a time, reuse completed evidence, and define time, storage and compute limits before expensive runs. Stop and report substantive failures rather than running an open-ended retry campaign.
- Keep active computation and inputs internal; use the SSD for verified archives. Preserve the existing storage floors. New cloud spending requires separate explicit authorization.

## First bounded experiment, after approval

1. Confirm the selected first-encoder-block 1280-by-320 projection against the frozen graph. Record its exact operator, model/weight hashes, all indices/codebooks, metadata and arithmetic precision. Do not substitute a smaller tile or a different matrix without explicit review.
2. Freeze its execution schedule and acceptance contract: lanes, banks, interfaces, workload, cycles/throughput requirement, voltage, PVT corners, loads, area accounting and activity traces. Retain the exact frozen numerical contract; do not silently introduce W4A4 or a different quantizer.
3. Implement the complete weight path: fixed selections, representative values, metadata/scales, product generation, distribution/driver circuits, readout, accumulation, buffering, reset and control. No host-supplied weights or uncharacterized ideal memory may stand in for the measured fabric. A testbench may provide inputs and check outputs.
4. Reuse and characterize the actual custom array where applicable: layout, DRC/LVS, extracted parasitics, timing/power models and integration views. Standard-cell mux/ROM synthesis is a labelled comparator, not proof of custom access-cell density. Count all periphery, routing and supply overhead.
5. Run GF180 synthesis, floorplanning, placement, clock/power distribution as applicable, detailed routing, extraction and timing analysis. Use representative frozen-model switching activity for dynamic power and report leakage. Verify the routed implementation against the projection's independent reference, with targeted reset/stall tests.
6. Produce one reviewable physical feasibility report. If a required macro, PDK view, route or timing check cannot close, report the concrete failed boundary and proposed bounded next step instead of claiming a completed physical result.

## Required result

| Evidence | Required reporting |
| --- | --- |
| Identity and correctness | Exact matrix/model/tool/PDK revisions; complete coefficient coverage; numerical output agreement; declared test scope |
| Area | Routed footprint in mm²; separate fabric, arithmetic, state, periphery and routing/utilization costs; exclusions explicit |
| Timing | Extracted-path constraints and slacks across selected corners; supported MHz, cycles per projection and achieved throughput |
| Power and energy | Activity provenance and operating point; dynamic and leakage mW; energy per completed projection; idle and relevant peak limitations |
| Physical verification | DRC/LVS, routing/electrical checks and macro-view coverage; any remaining violations or unsupported signoff checks |
| Reproducibility | Source, constraints, netlist/layout, extraction/activity data and compact result summary with exact archived evidence |

These are pre-silicon implementation estimates, not measured silicon performance. MHz is not a per-parameter metric. Area-per-weight can be a scoped density statistic; power must be tied to activity and throughput.

## Review gate before expansion

Review the complete projection result first. Then construct a whole-model budget that separately counts other matrix shapes, local codebooks, frontend, dynamic attention, writable state, clocks, IO and physical overhead. Do not determine die count by multiplying a single tile's density by 31.5 million parameters alone.

Retain the targets of exact frozen-model behavior, real-time speech recognition and total STT subsystem power below 1 W. One die is preferred; concrete two-/three-die partitions require link, package and all-die energy accounting. Die dimensions and numerical engineering margins must be fixed before a fit decision. External-memory hardware is a separately labelled fallback, not successful completion of the fully on-chip fixed-fabric objective.

Full-model RTL integration, FPGA/DDR emulation, full-corpus replay, test-chip fabrication and product tapeout are subsequent decisions. None is launched by this proposed goal. A full-model test remains necessary later, but is not a prerequisite to measuring this complete projection.

## Resume condition

Wait for the human to read this goal and explicitly approve it. Preserve the old broader goal as incomplete; update the execution objective to this bounded milestone when resuming. Do not mark the project complete or resume from a timer, stale plan, task message or old spending window.

Shutdown evidence is recorded separately in [the pause receipt](../reports/routevoice-user-pause-20261013.md).
