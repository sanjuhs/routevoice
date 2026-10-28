# Die size and remaining system costs — 2 October 2026

**The required complete die size and minimum die count are still undetermined.** The current arithmetic supports an incomplete component subtotal, not a whole-chip fit. We retain the existing Moonshine model, four-bit codebook selection and Taalas shared-product/frozen-selection architecture.

## What we can calculate now

The preserved v4 source-capacity screen contains 1,440,000 external bytes and 233,124 conservatively pooled private bytes for an executed reduced encoder component. Translating its 1,673,124 bytes into 409 copies of the particular 4-KiB research bank at 0.9479839488 mm² gives 387.7254350592 mm². This is a hypothetical physical replacement, not a measured implementation of all these arrays, ports or control registers. It is not the full recognizer peak.

| Mutually exclusive selection construction | Partial fixed selection | Hypothetical component state | Incomplete subtotal | Square equivalent |
| --- | ---: | ---: | ---: | ---: |
| Original four-bit frozen selection | 221.42 mm² | 387.73 mm² | 609.15 mm² | 24.68 × 24.68 mm |
| Resolved integer two-nibble alternative | 360.59 mm² | 387.73 mm² | 748.32 mm² | 27.36 × 27.36 mm |

The second row is an alternative exact coefficient representation; it is never added to the first row. These footprints do not establish a memory-density lower bound or an impossibility result for a smaller single-die design. Conventional SRAM weight storage is not the primary architecture in either row. Complete shared-product generation, book/value delivery, peripheral/readout costs, fanout and fixed-selection routing are still needed.

For the original four-bit path, the explicit outline arithmetic is:

| Assumed outline | Aggregate area | Remaining after the 609.15-mm² incomplete subtotal |
| --- | ---: | ---: |
| One 20 × 20 mm die | 400 mm² | −209.15 mm² |
| One 25 × 25 mm die | 625 mm² | 15.85 mm² |
| One 30 × 30 mm die | 900 mm² | 290.85 mm² |
| Two 20 × 20 mm dies | 800 mm² | 190.85 mm² |
| Three 20 × 20 mm dies | 1,200 mm² | 590.85 mm² |

These are study assumptions, not foundry-qualified sizes, recommended tapeout dimensions or realizable partitions. A negative remainder rejects that particular subtotal/outline combination only. A positive remainder does not establish full fit. In particular, 25 × 25 mm leaves very little beyond the incomplete subtotal; it cannot currently be offered as a proven single-die size. A 30-mm study outline gives more arithmetic headroom but still needs foundry acceptance and complete physical costing. Two dies require an actual partition and link; their aggregate area cannot substitute for either die fitting independently.

## Costs and evidence still needed

The [actual composition follow-up](TAALAS-COMPOSED-CAPACITY-SCREENS-2026-10-02.md) now separates the qualified copied six-layer encoder/adapter from the smaller layer0 screen. Under the same hypothetical research-bank replacement and original partial four-bit selection, its incomplete pooled subtotal is **943.78 mm²**; the borrowed candidate is **795.90 mm²**, with saving still uncredited pending lifecycle controls. The resolved fixed alternative gives different, larger subtotals. Neither establishes complete die size, fit or impossibility. The actual full-F500 token/producer's own private inventory is prepared, not executed.

- Compose the actual frontend/VAD, encoder, adapter, decoder and original EOS/segment control. Count maximum simultaneous live arrays and their physical owners. Separate component state cannot be summed or maximized blindly.
- Map every arithmetic/controller instance and every private array to a declared implementation; charge macro ports, bank rounding, alignment, codebook/value access and all fixed-selection peripherals. Avoid adding child areas twice.
- Place and route the complete implementation with clock distribution, supply and IO allowances, timing/PVT and electrical checks. One-, two- and three-die candidates must use the same quality, throughput and total-power contract.
- Measure service and energy at one declared operating point, including memories, shared products, dynamic attention, frontend, links and idle power. Total power below one watt and real-time operation are unproved.

The existing frontend serial schedule demands 429.433 MHz per 80-ms chunk, which has not been physically achieved. Parallelism must be implemented and costed, rather than removing this demand from the ledger. The six-layer borrowed encoder positive passed at 442,043,655 simulation clocks, but its proposed capacity saving remains uncredited pending its fault/reset/lifecycle controls.

The complete F500 decoder/producer positive passed fixed and variable-stall positions across six layers, 3.84 million K/V scalars and 65,536 vocabulary outputs. Whole-mode clocks are 30,078,229. This remains one retained synthetic fixture with an external encoder output and a forced second epoch after EOS; host simulation duration is not ASIC throughput. The literal wrong-V-lane control has also passed: its actual bridge mutation is observed and the unchanged context oracle rejects it, with no successful publication. FullF500 terminal-source refusal and warm retry pass at 48,519,282 clocks; the original post-native observer failure remains preserved alongside a separate same-edge qualification. FullF500 stale/epoch refusal and warm retry pass at34,351,824clocks with zero resets; its independent evidence audit rejects ten contradictions. FullF500 pending-source cold reset and fresh position0 restart pass at25,931,533clocks; its closed-evidence audit rejects thirteen contradictions. Complete-recognizer controls remain open.

The frozen K64 quality pilot passed clean/other/noise point gates (WER 4.488% / 13.631% / 15.765%). Population confidence and live-streaming quality remain separate open requirements. No new recognition, speech download, training or model inference was performed here.

## How we will decide

We will test one die first with a complete state/area/service ledger. If a specific one-die implementation fails, we will preserve that failure and test an explicit two-die partition, then three if necessary. A successful D-die design proves an upper bound of D. Calling D the minimum additionally requires excluding smaller counts within a declared die-size/design contract. At present, neither a successful full-chip upper bound nor a minimum count is proved.

The new bounded ledger independently rederived the saved exact component arithmetic, square equivalents and 1–3 die outline sweep. It does not rerun the historical physical experiments or promote their component scope. Its source, eight input hashes, admission, result and final monitor are retained in `experiments/die-outline-sizing-ledger-20261002-v1`.

Sources: [current envelope and qualifications](TAALAS-CURRENT-DIE-ENVELOPES.md), [compact decoder state](TAALAS-DECODER-TOKEN-COMPACT-PRIVATE-STATE.md), [borrowed encoder result](TAALAS-ENCODER-ADAPTER-BORROWED-ACTUAL-POSITIVE-2026-10-02.md), [full F500 positive](TAALAS-ADAPTER-SESSION-FULL-F500-POSITIVES-2026-10-02.md), [actual wrong-V-lane rejection](TAALAS-ADAPTER-SESSION-FULL-F500-NEGATIVE-2026-10-02.md), [terminal recovery and preserved observer failure](TAALAS-ADAPTER-SESSION-FULL-F500-TERMINAL-RECOVERY-2026-10-02.md), [accepted900-mm² verification contract](TAALAS-900MM2-SINGLE-DIE-VERIFICATION-CONTRACT.md), [foundry outline source review](TAALAS-900MM2-FOUNDRY-OUTLINE-SOURCE-REVIEW-2026-10-02.md), [existing model/quality and proof ledger](DIE-COUNT-PROOF-2026-09-19.md), and `reports/taalas-private-state-screen-v4.json`.
