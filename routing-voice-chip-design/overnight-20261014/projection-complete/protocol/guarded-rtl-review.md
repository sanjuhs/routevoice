# Guarded RTL and throughput review

**The 180 ns row cadence and 11,843-cycle unstalled projection latency are supported. They are target-clock schedule results, not achieved physical throughput.** Read-only review; no RTL/config changes, native simulation, analog run or cloud action.

The wrapper `rtl/rv_k64_projection_complete.sv:7`–`:43` and W2b engine `../fabric-k64/rtl/engine.sv:107122`, `:107398`, `:107722` give this sequence, with t=0 the accepted activation LOAD:

| Time at a 20 ns target clock | State/action after edge |
|---:|---|
| 0 ns | Capture activation and row; wrapper PRE, engine INDEX |
| 20 ns | GUARD; active-low PC rises, ending precharge |
| 40 ns | EVAL1; selected WL rises |
| 60 ns | EVAL2; evaluation continues |
| 80 ns | Capture array output into frozen-index flops; HOLD |
| 100 ns | RELEASE; WL falls |
| 120 ns | DONE; PC falls; engine may advance on next edge |
| 140 ns | Engine INDEX consumes frozen bits; wrapper returns IDLE |
| 160 ns | Engine ACCUM; next row becomes LOAD-ready |
| 180 ns | Earliest next accepted activation |

Thus consecutive LOADs are nine clocks apart. One whole vector takes `9*1280 + 320 + 3 = 11843` clocks under no stalls, excluding the accepted start edge. This is independently consistent with retained `logs/rtl-simulation.log:1` and `:55`, and the explicit assertion in `tb/complete.sv:67`. The 320 output beats and three affine drain clocks retain W2b's schedule (`../fabric-k64/CONTRACT.md:7`). The derived latency is 236.86 us at 20 ns; no full-bank achieved MHz follows. For sustained successive vectors, account for the next accepted start edge as well: with the current affine active/busy handshake, the earliest new start is the edge after the preceding final output acceptance. The first latency count excludes that new start cycle; using `f/11843` as a demonstrated sustained-vector rate would omit this boundary and physical/stall limits.

Stall semantics are coherent: the physical read phases run to completion even when `step_enable=0`; DONE then holds captured digital data until INDEX can advance. `step_enable` is not a universal input or output pause: the underlying LOAD accepts valid input independently of it, and output transfer uses ready/valid. State the public interface accordingly. Reset gates evaluate immediately but synchronously changes phase to RELEASE, preserving a nominal release interval before PC falls; the 11 retained digital abort checks do not qualify analog abort behavior or arbitrary reset pulses.

## Why this is not 60 ns reuse

W6's retained waveform commands PC-off at 14 ns, WL-on at 18 ns, WL fall over 57.8–58 ns and PC-on over 59.8–60 ns. The present controller changes its registered state only on 20 ns rising edges. It cannot reproduce those phase locations. A simple dual-edge 20 ns clock only adds a 10 ns grid and still cannot reproduce the exact 14/18/58 ns placements. Finer phase generation or a separately characterized revised waveform is necessary.

The current wrapper also serializes macro phases and subsequent INDEX/ACCUM before the next input. Calling the macro's sampled interval 60 ns does not remove that scheduling cost. Achieving a sustained row every 60 ns needs a different controller/data schedule; prefetching the known next index row and overlapping readout with arithmetic is one possible design family, but is neither implemented nor proved here. Prefetch/overlap alone would not make this 120 ns physical sequence run every 60 ns on the same bank. Conversely, a new faster phase generator alone does not prove safe full-bank delivery at that rate. This is an implementation limitation, not an impossibility claim about the architecture.

## Material reporting qualifications

1. **Mapped one-hot decode still has an unqualified phase-handoff gap.** The RTL is binary, but the retained actual synthesis netlist `evidence/complete-mapped.nl.v.gz` is **one-hot**, so the earlier source-only three-bit-transition concern must not be described as the mapped implementation. Uncompressed lines 362576–362615 show eight `dffq_1` phase flops. Following their D/Q cones gives `phase[1]=IDLE`, `[4]=PRE`, `[3]=GUARD`, `[6]=EVAL1`, `[2]=EVAL2`, `[5]=HOLD`, `[0]=RELEASE`, `[7]=DONE`. Actual cell `_03978_` (lines 327030–327035) computes `_01595_ = phase[2] | phase[6] | phase[5]`, the active-evaluation OR. Cell `_05003_` (333672–333677) computes `pc_logic = phase[3] | phase[0] | _01595_`; `precharge_driver` (2251141–2251144) buffers that into PC. The same `_01595_` feeds reset/address-gated WL decode, for example `_03981_` and `_03982_` (327047–327058). Thus an EVAL1→EVAL2 handoff exchanges two separately clocked one-hot bits while the OR should remain high. Unequal clock-to-Q/clock arrival can potentially create an all-zero interval; whether its width propagates through these real gates and unequal PC/WL paths is unmeasured. One-hot recoding removes the binary three-bit decode concern but does not itself prove hazard-free dynamic controls. This is a physical qualification gap, not an observed failure; no new timing/analog simulation was run.
2. **The timing proxy omits essential paths.** `macro/timing-model.json` states that all corners use PC-to-output 44 ns, that independent WL-to-output arcs are absent, and that loads/slew are assumptions. Consequently independent decoder/WL arrival, minimum delay, PC/WL nonoverlap and full-bank PVT behavior are not covered. A single-cycle negative slack on the 44 ns proxy does not by itself refute the multi-cycle digital schedule; positive proxy slack does not establish analog timing closure.
3. **The separate 3/2 multicycle scenario is conditional.** `power/postroute_timing.tcl:38`–`:41` applies setup 3 / hold 2 through macro outputs, corresponding to PC-off at 20 ns and capture at 80 ns. It preserves the original scenario first. This is a reasonable schedule-labelled sensitivity report for the PC-based proxy, not qualified signoff. Confirm all 1,280 actual bank outputs match in the real design; the one-pin API-fixture receipt is not the top's exception coverage. Do not apply a later 3-cycle exception blindly to newly added WL arcs: WL launches at 40 ns and capture at 80 ns, only two clocks apart. The same 44 ns value for rise/fall and min/max cannot characterize physical hold/recovery behavior.
4. **Behavioral success is the claimed functional scope.** `tb/bank_model.sv` returns the real row after a fixed 24 ns delay and checks coarse PC/WL guards. It does not simulate output-load dependence, supply effects or full-bank control fanout. A delayed scheduled assignment is not an analog cancellation model. Existing 54-vector and 11-abort results support exact arithmetic and the stated digital interface; mapped/routed gate evidence must be reported separately. The gate testbench's four abort cases and disabled internal read-count watcher must not inherit the RTL suite's 11-abort or 1,280-read assertion coverage.

No functional mismatch was found by this source review. Keep the final language “180 ns target-derived unstalled row cadence; 11,843 measured RTL clocks excluding accepted start; full-bank physical timing unqualified.”
