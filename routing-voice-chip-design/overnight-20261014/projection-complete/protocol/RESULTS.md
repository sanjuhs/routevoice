# W8 sampled synchronous protocol result

**sampled_SS_120ns_protocol_pass.** Real native SS SPICE completed in504.546s. Capture80ns passes all320combined early/late output sample checks with raw, precharge and phase checks. Failures:{'output': 0, 'raw': 0, 'precharge': 0, 'phase': 0}. Maximum sampled settling after WL command:23.374847ns. These are sampled partial-slice circuit estimates, not full-bank timing closure.

Exact20ns-edge construction: active-low PC rises20ns, WL rises40ns, first capture80ns, retention sample99.5ns, WL falls100ns, PC falls120ns. Each command's0.2ns source edge follows that time. Real row pattern[0,1,1279,1274,546]repeats twice;10fF output loads; SS2.97V125C. The parent180ns minimum row cadence is a separate RTL scheduling statement.

Finite-window source energy over the second repeated sequence:[600,1200]ns:

|Source|pJ per sampled read|
|---|---:|
|Receiver/pr|91.160591081|
|WL source/pw|1.120405139|
|PC source/pp|7.844668545|
|Ideal legal-state aggressor/pa|0.134759016|
|Net sum|100.260423781|

Scope is16active fullheight columns,112ideal legal-state bitline aggressors and128physical receivers, selected stockWL/PCdrivers, extracted MOS/C and geometry-derivedR. Maximum observed endpoint voltage difference:0.000676396453V. Complete internal charge periodicity is not proven. Full1,280-bit row energy remainsnull. Do not multiply these components into a measured full-row energy.

No fastest safe full-bank period is established.120ns is the20ns-clock candidate actually sampled here. A100ns candidate would combine capture/WLoff on the same edge and requires its own hold/protocol proof; it remains unrun. Full-bank sharedWL/PCfanout, controls/decoder, outputlatch/setup/hold, PDN/return/current, simultaneous allcolumn evaluation and analog reset-abort behavior remain unqualified. The20ns command-to-capture probe still fails12bit checks in this run.

Actual128-column-crop input loading is in[input_loads.json](input_loads.json): WLmetal24.69543–26.50314fF plus128NMOS0.36/0.28; PCmetal151.56014fF plus128PMOS2.88/0.28. Full-bank structural gate counts are1280each, but full-bank effective pin capacitance is uncharacterized. The clockless macro should not advertise fabricated clock-to-out/setup arcs. Preliminary WL-to-OUT timing and any electrical load estimates must remain labelledderived/conditional.

Evidence:[result.json](ss-120ns/result.json),[generated deck](ss-120ns/test.cir),[compressed trace](ss-120ns/trace.dat.gz),[watchdog extension](ss-120ns/watchdog-extension.json),[reading receipt](reading.json),[details](README.md). Original480s watchdog extended to720s by parent authorization without native restart. Only the waitingPython launcher was paused; native SPICE continued unchanged.

Postprocessing failure preserved: the original writer could not JSON-serialize a NumPy boolean after native SPICE finished. `analyze_saved.py` reproduces that error in `ss-120ns/postprocess-original-failure.json`, then converts NumPy scalars only at serialization. It reads the unchanged completed trace; no circuit or native simulation was rerun. The summary finalizer's first invocation preceded creation of the corrected JSON and failed with missing `result.json`; the corrected invocation reads the retained analyzer output.
