# Tall-bank physical variant

This follow-up changes immutable index placement and receiver replication. The tensor, index precision, UINT8 representative tables, activation precision and arithmetic remain unchanged. The actual layouts reuse the retained tall-array generator and `receiver-pre2` generator. The stronger precharge PMOS is 2.88 µm wide; keeper and inverter dimensions retain the qualified choices. Physical row/precharge drivers, global decoder/mux/control and output latches are excluded from these array/readout GDS footprints.

## Row addressing

For the 320-row variant, physical bank `b` stores logical rows `b + 4*r`, for `r=0..319`. Thus `bank = array_row[1:0]` and `local_row = array_row[10:2]`. Four consecutive logical reads use different banks. This is deliberate interleaving, not four contiguous 320-row slices. Independent GDS readback reconstructs the original logical 1280×320 image before comparing all indices.

W2b's K64 codebook domain must continue using the **logical** row. A new physical bank number is not a replacement for `floor(logical_row/64)`. Output bit order remains `frozen_index_bits[4*lane+bit]`. The optional 1,280-row variant has one bank and identity row mapping.

Each physical bank contains ten adjacent 32-lane subbanks and exactly 1,280 analog receiver channels. Wordline and PC rails are physically common across the ten subbanks in this construction. VDD/VSS and the array's local ground straps are connected within a bank; global interbank PDN and chip power delivery are excluded. The saved 32-lane timing subbank does not by itself include the long common bank rails or the other nine subbanks' loads.

## Throughput and latency are separate

For a **validated per-bank reuse interval** `T`, the arithmetic lower bound for regularly interleaved requests every 20 ns is `ceil(T / 20 ns)` independent banks. Threshold-crossing delay after wordline assertion is not that reuse interval: precharge, nonoverlap, data capture and recovery must also fit. An observed passing period is a sampled sufficient period, not a proved minimum unless the search brackets it.

Four striped banks revisit a given physical bank every 80 ns. This mapping can support a sampled protocol of at most 80 ns only if the actual full-bank electrical behavior, output selection, phases and schedule are also verified. The sample-slice factor in the comparison is conditional evidence, not a complete-macro throughput claim. If more than four independently reusable banks are required, this physical four-bank layout alone does not supply them.

A one-bank 1,280-row image has no interleaving capacity. Meeting a multi-bank factor would require additional full-image copies or a new repartitioned layout. Those areas and timing must be measured separately; the one-bank area must not be presented as supplying multiple independently readable banks.

W2b currently requests one INDEX row every three engine cycles (60 ns at its 20 ns target), but captures after the single INDEX interval. A 60 ns bank protocol therefore does not automatically satisfy its approximately 20 ns enable-to-capture window. Earlier precharge/predecode, stable-row lookahead, additional stalls or an explicit read-completion handshake may be needed. Interleaving improves initiation rate; it does not remove latency. Any pipeline also needs the matching logical-row/codebook tag to accompany its delayed index output. No such controller or W2b modification is included in this variant.

## Area comparison scope

The 64-row baseline uses the retained `timing/full-readout/` partial assembly: twenty banks, 25,600 receivers and 22.321166 mm². The new 320-row layout uses four banks and 5,120 stronger receivers. Its measured GDS rectangle includes the actual fanout and all unused space within the bounding box. It retains the previous horizontal 128-channel receiver strip and its routing, so the receiver strip fixes a much wider subbank pitch than the base array itself. Taller banks reduce repetition but do not reclaim that blank width. No receiver-count ratio is used as an area reduction measurement.

The 64-row analog result used ideal drivers and no distributed wire resistance, whereas the new circuit work reuses stock-driver `pre2std4` choices and geometry-derived resistance. The baseline receiver also has a 1.44 µm precharge PMOS. These method and circuit differences must stay visible beside the area-versus-speed table. Complete 1,280-bit row energy is unknown when only a selected column group is simulated; sampled source energy must retain its actual active-column/readout coverage.
