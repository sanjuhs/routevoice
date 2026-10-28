# W5 physical digital periphery

Three isolated GF180 macros are routed and pass selected KLayout DRC, Magic DRC and Netgen LVS with **zero errors**. They are in `handoff-v2/` with GDS, LEF, DEF, transistor SPICE, routed gate netlists, pin-coordinate JSON and metric JSON. This is usable physical periphery evidence; the complete array composition, its phase controller and its timing remain separate.

| Macro | Function | Dimensions | Outline area | Standard-cell area excluding fill |
|---|---|---:|---:|---:|
| `w5_row_decoder` | Enabled 6-to-64 decode with physical drivers | 120 × 120 µm | 14,400 µm² | 4,017.22 µm² |
| `w5_bank_mux128` | 20-to-1 selection of 128 bits | 450 × 450 µm | 202,500 µm² | 81,703.10 µm² |
| `w5_bank_decoder` | Enabled 5-to-20 bank decode | 120 × 120 µm | 14,400 µm² | 1,595.91 µm² |

The final row decoder puts all 64 wordline pins on its east edge and row/enable pins on the west. All three have physical VDD/VSS ports on Metal4/Metal5. The initial arbitrary-pin decoder remains in `runs/decoder-v1/` and `handoff/`; use **`handoff-v2/`** for final integration.

For the parent's proposed 200 separately decoded 64×32 subbanks, 10 mux128 instances and one bank decoder, the isolated outline sum is **4.9194 mm²**, or **12.010254 µm² per projection selection** for this digital periphery alone. The corresponding standard-cell sum is 1.622071 mm². This arithmetic ledger excludes array cells, analog receivers, all inter-macro routing and capture registers; it is not a composed macro or an area minimum. A physically shared decoder with distributed local drivers could have a different cost but was not implemented here.

All three routed gate netlists pass functional tests. Decoder coverage is every row and enable gating. Bank-enable coverage includes all 20 valid and 12 invalid addresses plus disabled operation. Mux coverage includes 8 rounds of all 32 addresses with disable checks and all 2,560 individual bank/bit paths.

KLayout uses the retained official GF180 FEOL, BEOL, connectivity and off-grid rules. Density and antenna are excluded from that check. All three yield zero markers, and all three have zero Magic DRC and Netgen LVS errors. These are open-flow checks, not foundry signoff. See `drc.json`, `functional.json` and `results.json` for exact commands, counts and hashes.

Extracted OpenRCX plus Liberty STA was run at nine combinations of nominal/min/max RC and TT 3.3 V 25°C, SS 3.0 V 125°C, FF 3.6 V −40°C. These are not the analog worker's SS 2.97 V SPICE results. Timing constraints are a 20 ns virtual clock, 4 ns input delay, 4 ns output delay and 0.25 ns uncertainty. Decoder outputs have 100 fF loads; mux outputs have 10 fF. The parent array and inter-macro wire loads are not included.

| Macro | Worst extracted setup slack | Worst slew violations | Worst capacitance violations |
|---|---:|---:|---:|
| Row decoder | −0.806 ns | 11 | 0 |
| Mux128 | −10.582 ns | 303 | 2 |
| Bank decoder | +5.459 ns | 0 | 0 |

Thus the periphery does **not** establish a 20 ns complete read. The slow-corner failures are preserved. Mux post-route timing was run separately in `runs/mux128b-poststa/`; its updated metrics are merged into the final handoff JSON. Earlier flow metrics accumulated pre-route corners and must not be mistaken for extracted results.

W2b owns the 1,280 output capture bits in `engine.sv:index_latch`; count them once within its routed ARRAY-PORT area. Adding macro-local registers would change the boundary. The engine makes **1,280 INDEX row reads during 4,160 integer cycles**. Its bare read-enable port also does not establish precharge/evaluate nonoverlap: immediate precharge on read-enable falling can overlap a still-high decoded wordline. `INTEGRATION-NOTES.md` records this outstanding physical control obligation.

Failures retained: `mux128-v1` failed legalization after inserting 2,566 blanket input buffers plus repair buffers. `mux128b-v1` disables only blanket input buffering, spreads placement to 30% target density, and completes actual routing/verification while preserving timing failures. `decoderb-v1` completes routing/verification and preserves its slow-corner timing failures. No failing result was relabeled as passing.

Commands, from repository root:

```sh
.venv/bin/python overnight-20261014/taalas-array/periphery/prepare.py
.venv/bin/python overnight-20261014/taalas-array/periphery/prepare_mux.py
bash overnight-20261014/taalas-array/periphery/run.sh decoder
bash overnight-20261014/taalas-array/periphery/run.sh mux128
bash overnight-20261014/taalas-array/periphery/run.sh mux128b
bash overnight-20261014/taalas-array/periphery/run.sh decoderb
bash overnight-20261014/taalas-array/periphery/run_sta.sh
bash overnight-20261014/taalas-array/periphery/run.sh bankdec
.venv/bin/python overnight-20261014/taalas-array/periphery/export_v2.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/periphery/test_function.py
nice -n 10 .venv/bin/python overnight-20261014/taalas-array/periphery/check_drc.py
.venv/bin/python overnight-20261014/taalas-array/periphery/collect.py
```

The retained JSON configurations are authoritative for v2 and bank decoder runs; the preparation scripts generate the initial configurations only. Each `run.sh` invokes the LibreLane Nix shell with `nice`, one job/thread and workspace-local temporary/cache paths. Existing run tags are preserved; choose a new tag for fresh reproduction. Source reading and hashes are recorded in `source-reading.json`.
