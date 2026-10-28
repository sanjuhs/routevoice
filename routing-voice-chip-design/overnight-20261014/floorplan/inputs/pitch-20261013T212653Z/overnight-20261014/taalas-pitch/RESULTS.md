# W6 pitch-matched readout — work in progress

The new **1,280-row ×320-output** bank keeps the native array bit-line pitch and uses **eight staggered rows of physical pre2/keeper/inverter receivers**. Its measured rectangle is **1004×2258.81um =2.26784524mm²**, or **5.536731543um²/selection**, versus W5's25.640028um² tall-bank rectangle. All1,638,400 programmed bits match the real K64 projection. Full-bank physical and timing qualification remains in progress; no complete-macro claim is made.

The corrected64-row test slice is1004×234.17um, **11.479818359um²/selection**, with selected GF180 DRC0 and all81,920 bits matching. Independent LVS and the negative control are running. The failed first revision (160DRCmarkers) is preserved in `r64-v1/`.

Uniform-density extrapolation is **31,457,280×5.536731543/1e6 =174.170514mm²** for arrays, analog readouts and local wiring. This is an extrapolation, not a98-tensor physical allocation. The October cells+receiver-strip sum was164.837mm²; its complete listed fixed-index component subtotal was221.421mm². W6 does not include decoder/WL/PCdriver/selector integration. Adding the older56.584mm² nonreceiver component terms yields an unplaced mixed estimate of230.754514mm², with remaining exclusions. Do not add the old11.004mm² receiver term again.

Pending results will be integrated here and in [results.json](results.json). Source reading, choice and limits are in [READING.md](READING.md). No git or cloud operations.
