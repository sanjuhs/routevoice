## Update ~07:35 IST
V2 still in GRT (~90 min). Free disk fell to ~22.49GiB from unrelated/system growth while no large W2 outputs were written. New `stop_dp_tool_on_disk_pressure.py`, session82752, polls1s and stops only leaf OpenROAD below22.35GiB so LibreLane can flush logs before existing22GiBgroup guard; records dp-disk-limit-log-preservation.json. It exits early if V2 controller finishes. Summarizer recognizes this termination evidence. Also transparently compressed two completed gate executables and reran them successfully: full32/10272/0, sliceactivity5/1605/0; evidence/compressed-executable-checks.json. Final check parser now only reports final antenna after completed detailed routing and checks DRC/LVS from actual completed corresponding stages.

# Active W2 work — 14 Oct 2026, ~07:15 IST

Only V2 physical work remains active. Do not finalize with any own job/controller active. All writes only in fabric/. No agents/cloud/commits. User W2 explicitly authorized scoped EDA despite older generic pause. Source readings already done and recorded in SOURCE-READING.md.

## Active jobs

- V2 `rv_fixed_proj320_dp-route200`, exec session7330, supervisor PID79711, OpenROAD PID80683. Started 05:58:54 IST; original 7200s continuation deadline **07:58:54 IST**. Global routing began06:04:40; at07:15 still active maze routing (~100% one CPU, ~6GiB RSS). Last completed02-openroad-stamidpnr-2;03-openroad-globalrouting has no checkpoint. Buffered log still0bytes. Free disk~23.06GiB.
- `continue_dp_with_signoff_caps.py`, session32248, waits for successful GRT. If GRT completes, it interrupts original supervisor so Python flushes logs, then resumes from `OpenROAD.CheckAntennas` in run `rv_fixed_proj320_dp-postgrt-capped` with SAME remaining deadline, updated KLayout caps4, routing4/STA2. It exits if original ends without GRT. Receipt `evidence/dp-signoff-thread-cap-continuation.json` appears on transition/end.
- `stop_dp_tool_at_deadline.py`, session17642, stops only leaf OpenROAD at **07:58:42 IST** to allow LibreLane to flush buffered logs before supervisor timeout. It exits early if the continuation controller finishes. Records `evidence/dp-time-limit-log-preservation.json`; this intentional time-bound termination is not a tool-reported routing violation.

Monitor with `python monitor_active.py <run-tag> --brief`, also check new `postgrt-capped` tag if original ends. Use exec_command session IDs via write_stdin, not functions.wait. Maintain commentary<=60s; waits<=60s. All heavy jobs nice10, total<=8 threads. Helpers are under fabric/ and use repo `.venv/bin/python`.

## Full V1 physical attempts now FINISHED

Initial synthesis265388cells/5674712.735993um² passed635.986s. Original physical budget was6564s, total about2h including synthesis. Original30%/20ns physical stopped3714.54s in slow repair/legalization. 20%/200ns density55 GPL failed GPL-0305 after680.948s; density35 retry also failed after570.743s. Final config `configs/rv_fixed_proj320_rom-util20-density35-noinflate-200ns.json` disables only routability-driven cell inflation, with all route/signoff checks enabled; FP20%, PL35%, clock200ns/IO40ns, typical resizer, final9STA corners, DRT4/STA2/KLayout4.

Final prefix run `rv_fixed_proj320_rom-util20-density35-noinflate-200ns` passed GPL, PDN(0violations), repair, DPL, CTS, STA in1046.477s. Controller resumed `rv_fixed_proj320_rom-route-util20-density35-noinflate-200ns`, passed postCTSrepair and STA, entered GRT. Bounded continuation ended465.641s, exit1, intentional SIGTERM to leaf at original budget deadline. `stop_full_tool_at_deadline.py` preserved buffered log: GRT extra iterations1..5of50, no completed routing. Source `evidence/full-rom-time-limit-log-preservation.json` captures reason; raw supervisor stop_reason null because child termination lets flow exit. Report/JSON normalize this separately, do NOT call it a tool-reported routing violation.

Latest full V1 checkpoint: `runs/rv_fixed_proj320_rom-route-util20-density35-noinflate-200ns/02-openroad-stamidpnr-2/state_out.json`. Typical setup+66.5473ns, hold+.556417ns at200ns. Allocated die28.612630mm²/core28.353067mm². PostCTSinstancearea10.7433mm²/util37.891%. No extracted/routed/signoff.

Full V1 pre-route auxiliary power FINISHED: run `rv_fixed_proj320_rom-pre-route-rtl-activity`, TT5MHz, default189.7365302mW, RTL-VCD305.5831492mW. Annotated79 /unannotated1226425 (~0.00644%): only top-level ports, internal activity propagated/default. NOT gate-annotated or extracted. Full V1 KLayout pre-route PNG saved and visually checked.

## Other completed results

All THREE RTL and GF180 zero-delay mapped checks: each32vectors/20random/10272comparisons/0failures. Full mapped build needed disk-stop then resume; both receipts retained. Zero-delay/two-state no SDF. Original-byte NumPy oracle; reconstruction asserts all102400values and16entries/book. 320-row start-to-done321cycles; slice65; full641with320clockedreads. Full5MHz target64.2us, unqualified; initial50MHz6.42us unqualified. Power workloads643cycles/fullvector,387/slice.

Synthesis: fullV1 265388cells/5.674712736mm²/55.417116562um²perweight; V2 222596/5.276646144mm²/51.5297475 perlogicalweight; slice190460/4.229742093mm²/206.530375625. No area subtraction as storage cost; V2 excludes array/periphery,42,240array-inputbits on block boundary.

V2 current200ns CTS: cellarea11.8037mm²/util44.7516%; die26.613756mm²/core26.376030mm²; TTsetup+53.5032/hold+.548467ns. Pre-route power default245.1654822mW, RTL-VCD394.8503733mW;42319annotated/1076008unannotated (~3.784%); only ports direct, internal propagated/default. Earlier30%/20ns CTS missed setup -101.387ns. Earlier IO-spacing and multicorner repair failures documented.

Slice200ns: TTsetup+90.3294/hold+.597714ns; cellarea6.23801mm²/util44.285%; die14.267764mm²/core14.085907mm². GRT stopped on22GiBguard after5890.26s, no route. Earlier45%floorplan DPL0036/840unlegalized. Prepower default150.6443769mW; gate-cell-VCD106.0931012mW,739686annotated/103648unannotated87.71%, zero-delaymappednetlist trace5vectors/1605checks. Failed dot-scope0annotation and RTL79pinattempt116.4083853mW retained.

All three `*-PRE-ROUTE-NOT-SIGNOFF.png` exist, actually rendered and viewed. No final routed PNG yet.

## Reporting and finalization

Pipeline: collect_checkpoint_metrics.py -> summarize.py -> write_run_commands.py -> write_results_report.py. Report remains WIP. Generator has `--final` only for wording; manually ensure own jobs ended first. Update V2 narrative/outcome after final result. Full-V1 narrative and images updated. JSON keeps unavailable routed metrics null. Expected9extractedcorners required before `achieved_mhz` set. Separate latestpre-routeTT timing table uses1000/(period-setupslack), explicitly unqualified. Power quantities separately marked pre-route/target clock with annotation coverage. Full-ROM and DP intentional leaf time-limit records normalize attempt termination reason. Do not fabricate DRC/LVS/antenna zeros.

If V2 routes, finish all checks (already enabled), extract final9corners/defaultTTpower, annotate VCD via `run_activity.py` WITHOUT --pre-route (requiresSPEF), finalPNG and visually inspect. Watch disk during final fresh allcornerSDFexports; can compress finished individualcornerfiles preservingbytes, do not disable corners/signoff.

`run_flow.sh` now exports `_OPENLANE_MAX_CORES=W2_NUM_THREADS`; --jobs only limits Pythonpool, so KLayout explicit4caps added. Active original DP has already-loaded old config without explicitKLayout caps; continuation controller handles this before signoff. All routing4/STA2 limits already held.

`hash_deliverables.py` hashes119+replayinputfiles and checks7previously recorded numerical sources unchanged; old manifest preserved `input-hashes.prior.json`. Run again final. `audit_checkpoint_paths.py` at07:00:199states,64archived/unavailable paths (sameolderarchives), run again final. Python AST/configJSON/report-consistency check passed after latest reporting edits except last few simpledocchanges; repeat final once.

Disk preservation: clone_duplicates.py then compress_completed_files.py on completed stages. `--activity-inputs` additionally transparently compresses completed tmpVCDinputs; just compressed4 and recovered~0.24GiB. All hashverified identical paths/bytes. Twoolderverifiedtararchives and APFSclone/compression receipts retained. Avoid deleting evidence. Successful gate executables kept; rebuildableC++/objects removed with hashmanifest. Twoold power runs were externally moved toSSD by another actor; W2 restoredlogs read-only; no externalwrites.

At final, verify no own EDA/controllers remain, refresh reports/commandledger/hashes/pathaudit. Report numerical success and physical incompleteness honestly if no signoff. Tell lead fullV1 is ready for longer/larger-resource rerun, no cloud launched. Final response concise with RESULTS.md/results.json links, keyverification and synthesisnumbers, explicit missing routed signoff.
