# W8 rate and energy evidence review

**Neither complete W6 row-read energy nor a general streaming invocation rate for the selected projection is established by the inspected receipts.** Keep both fields null in measured results. This bounded read-only review ran no model, simulator, EDA or cloud job.

## Complete row-read energy

The exact W6 bank is `PITCH_BANK_R1280`, 1,280 input rows by 320 four-bit selections, with 1,280 output bit columns. Its original TT/SS energy numbers (123.606923 / 98.516840 pJ per sampled read) come from **16 real full-height active columns, 112 ideal legal-state bit-line aggressors and 128 physical receivers**. They exclude the complete shared control loads, simultaneous full-bank current and nonideal supplies. See `overnight-20261014/taalas-pitch/RESULTS.md:33`, `:42` and `:46`; machine receipt `overnight-20261014/taalas-pitch/timing/results.json:458` explicitly sets `whole_bank_energy_pj_per_row` to null, and each case has `full_row_energy_pj: null` (`:198`, `:379`).

The W8 120 ns run does not widen that electrical scope. `projection-complete/protocol/results.json` fields `source_energy_sum_pj_per_sampled_read=100.26042378127435`, `full_row_energy_pj=null` and `full_bank_energy_projection_pJ=null` remain appropriate. Its `ss-120ns/result.json` binds the actual waveform, source hashes and finite-window measurements.

W5 provides no transferable complete-row energy either. `overnight-20261014/taalas-array/RESULTS.md:11` lists 126.934 / 100.366 pJ for its different 1,280-row geometry, but `:13` explicitly says the energy is partial and complete 1,280-bit row energy is unknown for **every** table row. The earlier 64-row experiment is a different electrical model and region: `overnight-20261014/taalas-array/timing/RESULTS.md:3` and its exclusions prohibit treating its 32-lane energy as full-macro energy. `timing/full-readout/RESULTS.md:13` has an unconnected 20-tile assembly with timing/energy unimplemented; `timing/decoded-tile/RESULTS.md:16` makes no decoded-tile timing/energy claim.

Therefore neither multiplying a partial slice energy by ten/eighty nor multiplying the timing-candidate receiver MOS meter by 1,280 yields measured full-row energy. The column meter omits explicit VDD coupling current and shared controls and is already included in receiver source energy. No defensible numeric complete-array energy per projection can be added to gate-level logic power yet.

## Audio rate and selected projection demand

The frozen input contract is 16,000 mono samples/s (`reports/stt-requirements.json:6`). A retained full frontend chunk consumes 1,280 PCM samples and emits four 320-wide feature rows (`reports/taalas-recognizer-boundary-evidence-v1.json:6`, first entry's `source_audio.shape`, `features.shape`, `feature_rows`; summarized in `docs/TAALAS-REAL-TIME-WORKLOAD-BOUNDARIES-2026-10-03.md:7`). Thus **80 ms/chunk and 50 new feature rows/s** are source-backed arithmetic for nonoverlapping, full chunks with retained history.

More recent actual native frontend evidence supersedes the old document's missing-real-PCM fixture status for its specific fixture: `scripts/voice_e2e_20261011_frontend_stream.py:42` iterates 125 chunks; `:43` slices consecutive, nonoverlapping `pcm[i*1280:(i+1)*1280]`; `:56` carries the actual returned state; `:59` checks the concatenated shape `[1,500,320]`. The executed receipt `reports/voice-e2e-20261011-frontend-stream-v1.json:2` says passed, `:35945` gives 500 feature frames, and `:35980` records 125 native calls. This supports that particular frontend chronology, not a general encoder service calendar.

The associated `experiments/voice-e2e-20261011-real-f500-v2/protocol.json:8`–`:12` declares 125,440 original PCM samples plus 34,560 synthetic silence samples, 160,000 lab samples total, and bypassed VAD. Hence 500 / 10 = **50 feature rows per lab input second** counts supplied synthetic silence. It is not a measurement of steady streaming work per new external speech second. The original crop is 7.84 s; the extra 2.16 s is declared lab padding. Do not silently count this padding as new external audio, nor promote the fixture to an accepted streaming recurrence.

The selected W8 matrix is first encoder block FF output, `node_MatMul_86_quant` / `val_89_quantized` / `blocks.0.ff.project_out.bias` (`reports/taalas-serial-word-nibble-k64-1280x320.json:11`, `:16`, `:19`; `overnight-20261014/fabric-k64/CONTRACT.md:3`). W8's unit invocation is one 1,280-input vector yielding 320 outputs, not one frontend chunk or a whole multi-frame encoder call. Under a **conditional single completed-utterance encoder pass with each feature evaluated once**, the selected matrix performs one vector projection per frame: 50 vector projections/s averaged over nonoverlapping supplied audio. This is a labelled workload assumption, not the actual general streaming rate.

The completed-utterance and streaming distinctions are explicit in `docs/TAALAS-REAL-TIME-WORKLOAD-BOUNDARIES-2026-10-03.md:11`, `:29`–`:33`: the number of frontend frames does not determine encoder invocation frequency. Growing-prefix re-encoding, overlapping VAD windows, lookbehind replay and retries can increase work per new external audio second. The bounded review found no current accepted recurrence establishing their combined rate for this exact physical projection. Other encoder layers use different fixed matrices; their invocations are not executions of this first-layer frozen bank. Whole-recognizer work must count them separately, along with dynamic attention and decoder work.

## Formulas that remain valid

Let `T_new` be seconds of new, non-replayed external input audio and `F_k` the actual number of feature-vector evaluations of this selected matrix in encoder invocation k, including re-evaluated frames. Then:

- `R_selected = sum_k(F_k) / T_new` vector projections/s. **Measured general streaming value: unknown.**
- Each unbatched successful W8 vector reads 1,280 index rows, not 4,160/4,163 engine clocks (`overnight-20261014/taalas-array/timing/RESULTS.md:18`; `fabric-k64/CONTRACT.md:7`). Therefore `R_rowreads = 1280 * R_selected`, plus any explicitly counted abort/retry reads.
- Conditional no-replay, one-pass example only: `R_selected=50/s`, `R_rowreads=64,000/s`.
- `E_array_projection = sum_(i=0..1279) E_fullrow(i, activity, PVT, phase)`. Only if a defensible representative full-row average is established may this be written `1280 * E_fullrow_average`.
- With consistently separated dynamic energy and leakage, `P_total = P_logic_leak + P_array_leak + R_selected * (E_logic_dynamic_projection + E_array_dynamic_projection) + P_other_idle_clocking`. Include both fixed and activity-dependent clock/control costs in their actual owners. Do not double-count standard-cell decoders/drivers/latches already included in gate-level logic power.
- If using finite-window **total** active energy (which includes leakage), use `P_total = R_selected * E_active_total_projection + (1 - duty) * P_idle`, with `duty = R_selected * active_duration` for one nonoverlapped engine and a feasible duty no greater than one. Do not add the same active-window leakage again.

All numeric full-array/complete-projection power remains unknown until complete row energy, matched activity/PVT ownership and the actual invocation calendar are supplied. No measured real-time or sub-watt claim follows from the conditional 50/s example.
