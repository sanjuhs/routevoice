# W12 per-hierarchy synthesizability

**Status: complete_with_failures** — updated 2026-10-21T14:03:44.570228+00:00.

Hierarchical composition with each distinct logic module synthesized independently against exact child-port stubs; no flattening and no DFF enable/reset merging. Area and resource sums include every reachable instance with multiplicity, exclude ROM-service interiors, and do not include cross-boundary optimization.

The 30,545 reachable elaborated modules reduce to 4,457 distinct logic units plus 17 distinct ROM macro types under the exact structural comparison documented in `per-module/manifest.json`. The direct compute child is itself almost the full recognizer, so it is recursively partitioned. Its reported totals include all descendant instances.

Top wrapper connectivity check: **pass**. Every synthesized parent retains its child instances and uses their exact elaborated port and parameter declarations as black boxes. Each child implementation is checked separately; no hierarchy boundary is silently omitted.

| Phase | Result | Unit status counts | Selected-attempt work (s) | Maximum child RSS (GiB) |
|---|---|---|---:|---:|
| generic | fail | {'pass': 4445, 'fail': 12} | 4684.6 | 4.211 |
| gf180 | fail | {'pass': 4445, 'blocked_by_generic': 12} | 6164.6 | 1.362 |
| fpga | fail | {'pass': 4451, 'fail': 6} | 10025.5 | 4.229 |

## First-level children

| Child | Generic | GF180 | ECP5 |
|---|---|---|---|
| \positions | ROM black box | excluded | storage charged separately |
| \original | fail | fail | fail |
| \frontend_rom | ROM black box | excluded | storage charged separately |
| \encoder_memory | ROM black box | excluded | storage charged separately |
| \encoder_head | ROM black box | excluded | storage charged separately |
| \encoder_O | ROM black box | excluded | storage charged separately |
| \decoder_self | ROM black box | excluded | storage charged separately |
| \decoder_body | ROM black box | excluded | storage charged separately |

Per-child counts, FFs, memory bits, cell types and completeness flags are in `results.json`. Detailed per-unit metrics, diagnostics and source-location annotations are in `per-module/results.json`. Failed unit identifiers link these two records. Native tool diagnostics are preserved with their log line; source locations are not presented as unsupported-construct locations unless the tool actually identifies them.

## Chip view

Generic totals from passing units: **20,486,077 cells**, **1,366,062 FFs**. Complete: **False**. The pre-target frontend inferred 311 memories / **8,169,778 bits**, excluding ROM macros. Generic mapping implements retained memory state in logic, so post-map memory bits can be zero.

GF180 TT 25°C 3.3 V standard-cell area from passing units: **430.744394 mm²**. Complete: **False**. A complete area/63 mm² ratio is None. Incomplete sums are not full-recognizer area estimates.

The floorplan assumes 63 mm² for frontend/dynamic/control logic (12 + 18 + 15 + 6 + 12), with separate shared projection, periphery, register and SRAM budgets. These RTL sums include instantiated arithmetic and generic writable state, while ROM services are excluded. They cannot replace the different shared-engine/SRAM architecture without reconciliation. See `AREA-COMPARISON.md`.

## FPGA view

ECP5 sums from passing units: **15,618,541 LUT4**, **745,985 FF**, **1,216 DSP**, **117 18-Kibit BRAM**. Complete: **False**. These are ECP5 counts; no Xilinx logic-fit claim is made.

The 28.641280 MB new-service weight payload requires **229,130,240 bits**; the 4-bit-index/codebook comparison (with original affine INT8 frontend and retained metadata) requires **139,980,800 bits**. Native capacity is at least **6,216 RAMB36**, or **6,633** under independent rectangular single-port banking. All identified ROMs total **300,019,892 bits**, or **210,870,452** in the comparison encoding.

The largest ECP5 has 208 18-Kibit BRAM blocks (3,833,856 bits), so neither weight encoding fits in one ECP5; this target provides a primitive-count view only. [Lattice ECP5 data sheet](https://www.latticesemi.com/-/media/LatticeSemi/Documents/DataSheets/ECP5/FPGA-DS-02012-3-4-ECP5-ECP5G-Family-Data-Sheet.ashx?document_id=50461). The existing capacity screen identifies VU9P/VU13P-class combined BRAM+UltraRAM for the original payload and VU7P-class combined memory for the comparison payload; BRAM alone is insufficient on those devices. These remain memory-capacity candidates only, with ports, mutable state, loading, timing and a separately mapped Xilinx logic fit unresolved. [AMD resource table](https://docs.amd.com/api/khub/documents/Fz8MLna3N2KIo_xWN_Iv3w/content). See `FPGA-CAPACITY.md`.

## Preserved failures and measurement

The monolithic flattened generic attempt was OOM-killed (−9 / 247). The initial FPGA attempt segfaulted (−11 / 245) during OPT_DFF; the OOM counter did not increase. Its fault instruction resolves to Yosys CellTypes::setup_type, without RTL source-line diagnosis. The subsequent generic attempts stalled in OPT_MEM_PRIORITY and OPT_DFF. Their logs, metrics and core evidence remain in the W12 directory and `attempts/`. The lead retired the stalled generic jobs at 12:03 and 15:58 IST on 21 October, respectively (`LEAD-ACTIONS.md`); their native exits were −15. Legacy controllers remain held while per-module work runs.

After a successful attention-core probe, subsequent stages skip optional post-techmap OPT_MERGE as well: the original pass aborted with std::bad_alloc under the 6 GB address-space cap. The affected completed units are retried with original artifacts archived under their attempts directory. A subsequent ECP5 allocation failure at AUTONAME led to omitting that optional naming-only pass too. Failed in-flight older profiles remain recorded and may need a retry. These changes preserve the mapped logic. The probe completed generic synthesis and check-assert in 112.836 s at 1,704,852 KiB peak RSS. Each per-unit stage records native exit, wall time, peak child RSS, CPU and script hash. Sums of unique-unit wall times are work totals, not elapsed parallel wall time. Peak RSS is not the sum of simultaneous processes. The runner enforces a 6 GB address-space cap per process, two workers sharing the W12 four-CPU allowance, memory and disk gates, and a one-hour per-stage timeout. A guard failure is reported explicitly, not hidden as an unsupported construct.

See `ROM-INVENTORY.md` for every ROM-service and extracted lookup boundary, including original file:line declarations for readmemh arrays. Original sources and baseline model artifacts remain unchanged. The source and ROM boundary manifests, compressed raw checkpoint and earlier diagnostics remain authoritative. Per-module synthesis does not rerun F64 equivalence. All outputs remain inside W12.
