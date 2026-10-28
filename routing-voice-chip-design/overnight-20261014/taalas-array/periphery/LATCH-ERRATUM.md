# Corrected latch ownership — independent review

Earlier periphery reports incorrectly interpreted the RTL declaration/write of `index_latch[1279:0]` as evidence of 1,280 physical capture flops. Those versions remain in `pre-review-latch-erratum/`.

The current W2b `rtl/engine.sv` contains only four occurrences of `index_latch`: declaration at line 16, resets at lines 106473 and 106798, and assignment at 107399. There is no consumer. W2b's retained `runs/array_port-v2/06-yosys-synthesis/rv_k64_array_port.nl.v` contains no `index_latch`; it does contain the representative latch bit nets.

At line 874 the live book lookup is `case({codebook_row_domain,frozen_index_bits[0 +: 4]})`; corresponding lookups exist for every lane. `representative_latch_0` is consumed by the partial-product selectors at lines 1197–1198 and captured from `representative_map_0` at line 107400. The real timing path therefore includes the macro read, bank mux and W2b book lookup before representative capture.

Consequences: no raw-index capture area may be credited to those unused declarations. The literal requested output-latch bank remains a separate physical obligation. A transparent latch strip is now being built at the lead's request, with a distinct capture_gate input. Its gate timing/nonoverlap must be qualified; neither direct read_enable gating nor an extra edge-triggered stage is silently compatible with W2b's existing schedule.
