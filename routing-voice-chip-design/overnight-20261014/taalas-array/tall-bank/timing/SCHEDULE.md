# W2b schedule and physical bank mapping

The existing engine executes LOAD → INDEX → ACCUM for each logical row. `array_read_enable` is asserted only during INDEX when step_enable is high; the INDEX-ending clock edge captures the 1,280 input index bits. Logical row increments at the ACCUM-ending edge. There are 1,280 physical row reads, 4,160 integer cycles and 4,163 cycles through the FP32 drain, not 4,160 row reads.

At the requested 20 ns engine clock, unstalled INDEX requests are 60 ns apart, while INDEX enable-to-capture is approximately 20 ns before setup. Row address is already available during LOAD; exploiting that earlier address for predecode/precharge needs an explicit phase schedule and is not implied by the present read-enable port.

The new 320-row construction is striped: physical bank = logical_row mod 4, local address = floor(logical_row / 4). Thus sequential logical rows can alternate physical banks without reordering activations or accumulation. This requires explicit address conversion and bank output selection in the interface. The previous contiguous image cannot receive this interleaving credit; it remains separately recorded in selection-contiguous.json.

For a hypothetical read initiation every 20 ns, required independent bank count is ceil(measured complete initiation interval / 20 ns). Four striped banks allow at most 80 ns between reuses of a bank in that schedule. This criterion is separate from read latency/capture aperture and output mux/latch timing. The current three-cycle engine instead revisits the same striped bank every 240 ns while still requiring each INDEX value within its capture aperture. A single 1,280-row bank has no such interleaving resource.

A full sampled protocol pass requires precharge, raw and restored data margins, and actual buffered PC/WL phase checks, including recovery before the following read. A threshold crossing after WL command alone is not an initiation interval or a timing-closed engine interface.
