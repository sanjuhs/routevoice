# FPGA capacity screen

The 17 new service ROMs contain **229,130,240 bits** (28,641,280 bytes): a theoretical minimum of 6,216 RAMB36 blocks when all 36,864 bits are usable. Per-array rounding, port duplication and packing increase this. `capacity.json` records both total and per-array lower bounds. The per-array rounded lower bound is 6223 RAMB36 blocks. No ROM BRAM placement is claimed: these are abstract black boxes.

The K64 comparison uses 4-bit indices plus sixteen UINT8 representatives per 64 weights (6 bits/weight), retains metadata, and uses the exact original affine INT8 frontend representation. It needs **139,980,800 bits** for these new services. Adding the five already-onboard tables gives **210,759,680 bits**; small lookups and writable state are additional. This is a representation calculation, separate from W11 full-path qualification.

AMD XMP103 v2.8 lists VU7P with 50.6 Mb BRAM + 180 Mb UltraRAM, VU9P with 75.9 + 270 Mb, and VU13P with 94.5 + 360 Mb. Thus **VU9P/VU13P-class BRAM+UltraRAM capacity** can cover the roughly 300 Mbit major original ROM payload, subject to banking, ports, mutable-state and logic fit. VU7P-class combined memory is a candidate for the roughly 211 Mbit compressed payload, with limited headroom. **BRAM alone is insufficient** on these examples. UltraRAM needs an explicit synchronous interface and image-loading implementation; the current black boxes do not supply those. No device fit or timing closure is established.

Sources checked 21 October 2026: [AMD UltraScale+ product selection guide, pp. 3 and 6](https://docs.amd.com/api/khub/documents/Fz8MLna3N2KIo_xWN_Iv3w/content); [AMD memory architecture comparison](https://docs.amd.com/r/en-US/am007-versal-memory/Block-RAM-and-UltraRAM-Comparison). Device-guide Mb figures are vendor rounded units; exact implementation must use primitive counts/data widths. External DDR/HBM is another FPGA architecture, with a different bandwidth/latency contract.

With independent rectangular banks and one read port per declared array, choosing among the documented RAMB36 modes gives **6,633 blocks** for the 17 native service arrays. This charges depth/width padding but does not implement service adapters or map the RTL. Modes are from [AMD UG573 Block RAM Summary](https://docs.amd.com/r/en-US/ug573-ultrascale-memory-resources/Block-RAM-Summary).

The prior inventory omitted the 1,072 × 64-bit rotary sine/cosine table. Including it and all other identified small tables gives **300,019,892 unique logical ROM bits** in the v2 view and **210,870,452 bits** in the representation comparison, before extra read-port replication.


ECP5 view: the largest family member has 208 18-Kibit blocks (3,833,856 bits) and 156 18×18 multipliers. The new-service payload alone needs at least 12432 such blocks, or 7595 for the comparison encoding. A single ECP5 therefore cannot hold the weights. These are capacity lower bounds without port/banking replication. [Lattice ECP5 family data sheet](https://www.latticesemi.com/-/media/LatticeSemi/Documents/DataSheets/ECP5/FPGA-DS-02012-3-4-ECP5-ECP5G-Family-Data-Sheet.ashx?document_id=50461).
