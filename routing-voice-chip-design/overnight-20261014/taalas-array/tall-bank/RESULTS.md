# W5 tall-bank comparison

**The 320-row layout reduces the measured array/readout assembly from 22.3212 to 12.4401 mm² (44.3%).** Four striped banks replace twenty 64-row banks. The optional single 1,280-row bank measures 10.5022 mm². These are physical GDS bounding rectangles, including unused routing space, not receiver-count area estimates.

The table includes cells, physical precharge/keeper/inverter readouts and actual local joining/control/ground wires. **Global decoder/mux/control, physical WL/PC drivers, output latches and interbank PDN remain excluded.** A complete macro area and achieved ARRAY-PORT clock are not established.

| Rows/bank | Banks | Measured partial macro area, mm² | µm²/selection incl. local readout | Readouts | Worst sampled settling TT / SS, ns | Sampled energy TT / SS, pJ/read | Tested common reuse interval, ns | Conditional banks for 20 ns initiation |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 20 | 22.3211660 | 54.495034 | 25,600 | 2.976 / 4.390 | 77.709 / 62.275 | 20 | 1 |
| 320 | 4 | 12.4400808 | 30.371291 | 5,120 | 5.822 / 8.920 | 51.344 / 41.439 | 40 | 2 |
| 1280 | 1 | 10.5021553 | 25.640028 | 1,280 | 14.676 / 24.351 | 126.934 / 100.366 | 60 | 3 |

**Timing and energy scope:** TT is 3.30 V/25°C; SS is 2.97 V/125°C. Settling is measured after the WL command, and is the worst sample among passing retained protocols, not end-to-end macro latency. The 64-row baseline uses ideal drivers, extracted capacitance without distributed resistance, a 1.44 µm precharge device and 32 fully active lanes. New variants use the retained `pre2std4` 2.88 µm precharge receiver, extracted stock drivers, actual layout capacitance and geometry-derived resistance. Their energy is the sum of finite-window source energies for **16 active bit columns plus 128 readouts**, selected drivers and ideal aggressors. Complete 1,280-bit row energy remains **unknown for every row of this table**. The different test scopes prevent an apples-to-apples energy/speed ratio.

The optional 1,280-row energy pair uses matching compact TT/SS sequences. Its worst SS settling also includes the broader SS-only sequence, which is retained as additional evidence. The compact SS sequence alone already fails six data probes at 20 ns after WL command. No 20 ns latency claim follows from a passing 60 ns protocol. The supplemental 320-row control-load model is a different circuit scope and is reported separately below.

The conditional factor is `ceil(tested passing complete protocol interval / 20 ns)`. It includes the sampled precharge/read/recovery sequence; it is not computed from threshold delay. It is a sufficient factor for that sampled slice protocol, not a proven minimum or full-bank throughput result. Failed shorter protocols remain in the timing report. Four striped 320-row banks revisit each bank every 80 ns under the hypothetical 20 ns request stream, or every 240 ns with current W2b requests 60 ns apart. A single 1,280-row bank provides no interleaving; any larger factor would require full-image replication or a new partition and a new area measurement.

## Retained protocol trials

* 320-row ss, 20 ns interval: **FAIL**; output/raw/precharge/phase failures 116/100/0/0; 448 sampled checks.
* 320-row ss, 40 ns interval: **PASS**; output/raw/precharge/phase failures 0/0/0/0; 448 sampled checks.
* 320-row ss, 60 ns interval: **PASS**; output/raw/precharge/phase failures 0/0/0/0; 448 sampled checks.
* 320-row typical, 20 ns interval: **FAIL**; output/raw/precharge/phase failures 14/8/0/0; 448 sampled checks.
* 320-row typical, 40 ns interval: **PASS**; output/raw/precharge/phase failures 0/0/0/0; 448 sampled checks.
* 320-row typical, 60 ns interval: **PASS**; output/raw/precharge/phase failures 0/0/0/0; 448 sampled checks.
* 1280-row ss, 60 ns interval: **PASS**; output/raw/precharge/phase failures 0/0/0/0; 128 sampled checks.
* 1280-row typical, 60 ns interval: **PASS**; output/raw/precharge/phase failures 0/0/0/0; 128 sampled checks.
* Additional 1,280-row full-pattern sample, ss, 60 ns: **PASS**; maximum sampled settling 24.350631 ns; output/raw/precharge/phase failures 0/0/0/0. This is supplemental evidence; its exact circuit and sampling scope remain in the timing report.
* Supplemental 320-row full-control-load sensitivity, ss, 40 ns: **PASS**; maximum sampled settling 9.075879 ns; output/raw/precharge/phase failures 0/0/0/0. This is supplemental evidence; its exact circuit and sampling scope remain in the timing report.

Numerical timestep failures are preserved separately in the timing report and are not scored as electrical passes or electrical failures. No final timing case timed out. The shortest tested passing interval is not a proof of the minimum possible interval. See each retained deck for the exact precharge guard and capture sample times.

## Physical verification

| Rows/bank | Assembly dimensions, µm | Selected full-assembly DRC markers | Independent bit readback | Full-bank LVS |
|---:|---:|---:|---|---|
| 64 | 4669.70 × 4780.00 | 0 | all 1,638,400 bits match | pass; 87,040 devices, tile0 |
| 320 | 4669.70 × 2664.00 | 0 | all 1,638,400 bits match | pass; 414,720 devices, bank3 |
| 1280 | 4669.70 × 2249.00 | 0 | all 1,638,400 bits match | not run |

The 320-row full-bank reference independently decodes the original packed K64 tensor and checks it against W2b RTL. Monolithic Netgen passes with no property errors, supported by exact device-graph/W/L comparison, ten passing partitions and a shared-net audit. A doubled-width negative control is rejected. DRC uses the reused official GF180 FEOL/BEOL/connectivity/off-grid rules; density and antenna are excluded. No foundry signoff claim is made. The optional 1,280-row variant has no full-bank LVS claim.

The final required 320-row timing group is bank3/group2, containing the worst ranked column among all 1,280 columns of the extracted bank3 by an explicit-capacitance/geometry-resistance proxy. That proxy and sampled sequences do not prove a global worst case over all four banks. The earlier group3 timing runs remain separately recorded. The optional 1,280-row sample is independently extracted from its actual programmed layout; its ranking and scope are in the timing report. Its compact authoritative sequence alternates far rows 1,278/1,279 twice, exercising one/zero on the selected worst-ranked bit. This reduced coverage is not equivalent to the required 320-row near/far/activity sequence.

## Integration and evidence

Physical 320-row placement is striped: `logical_row = bank + 4*local_row`. Use `bank = row[1:0]`, `local_row = row[10:2]`; keep W2b representative/codebook selection tied to the original logical row. Each bank has ten 32-lane subbanks, common long WL/PC rails, and one set of 1,280 readouts. Stock drivers in the timing harness are not placed in these GDS banks.

W2b requests 1,280 rows in 4,160 integer cycles (4,163 with FP32 drain), normally one request every three cycles. Its INDEX capture aperture is still one cycle, and its real representative register follows a combinational lookup. Bank interleaving does not remove this latency/setup requirement. Complete-row control loading, output selection, capture phases and the logical row tag require physical and protocol closure. Hard-macro placement beside W2b remains skipped; there is no complete qualified hard macro to place.

The unchanged retained cell-only specimen remains **4.8684604443 µm²/selection**. Taller layouts retain the wide horizontal readout strip and joining geometry, so much of each rectangle is unused width. Their areas are measured implementations, not optimal lower bounds.

* [320-row GDS](r320/assembly.gds), [geometry](r320/geometry.json), [DRC](r320/assembly-drc.json).
* [1,280-row GDS](r1280/assembly.gds), [geometry](r1280/geometry.json), [DRC](r1280/assembly-drc.json).
* [Independent verification](verification/RESULTS.md), [machine evidence](verification/results.json).
* [Timing and preserved failures](timing/RESULTS.md), [machine evidence](timing/results.json).
* [Integration contract](INTEGRATION.md), [exact commands](COMMANDS.md), [comparison JSON](results.json).
