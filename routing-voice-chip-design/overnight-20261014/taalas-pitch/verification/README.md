# W6 independent verification

`verify.py` independently unpacks the original K64 candidate tensor using its
block metadata, checks all 409,600 selections against W5's image and W2b's RTL,
and generates transistor-level reference connectivity directly from that image.
It does not use a schematic emitted by the layout generator.

Run each stage with a fresh `--run` name for every changed GDS. Inputs and GDS
SHA-256 are pinned by `input.json`. The stages are `extract`, `compare`,
`netgen`, and `negative`; the optional `partitions` stage is a bounded fallback.
The full reference uses four access NMOS per selection and the four-device
pre2 receiver (precharge PMOS W/L 2.88/0.28 µm).

`compare` permits only checked bijective hierarchical-prefix removal. It
requires every named physical boundary net and exact device connectivity,
model, width and length multiplicities, allowing transistor source/drain
symmetry. `netgen` requires the unique-match phrase and absence of property
errors. `negative` doubles only one reference precharge width and requires a
reported property error, even if Netgen also prints a topology-match phrase.

`readback.py` reopens GDS, checks each array is instantiated once in its group,
decodes the actual programmed Via1 centers, rejects extra/duplicate programming
sites, and compares against the independently unpacked original tensor.

Commands use the repository `.venv/bin/python` and the prescribed Nix shell,
with nice level 10 and one-thread BLAS/OpenMP. Full LVS extraction omits the
capacitance SPICE dump; timing extraction is a separate worker's scoped result.
Every stage checks the 22 GiB free-space guard. Extractor, Netgen and negative
control failures remain in their original run directories.

These checks qualify the stated array-plus-receiver geometry. They do not
qualify missing row/phase drivers, output latches, whole-chip PDN or timing.

`verify-connectivity.py` preserves the same full-bank MOS/reference checks but
explicitly disables capacitance, coupling, lumped/full resistance, length and
adjust extraction. The separately named `r1280-v2-connectivity` attempt was cancelled
after the original full-C extraction in `r1280-v2` completed successfully.
The original full-C extraction supplies both full LVS and timing capacitances;
the cancelled parse retains its native SIGTERM and cancellation receipts and
receives no verification pass/fail credit. Its runner enforces a
3600-second bound and 22.2 GiB disk termination reserve while retaining native
return codes. No completed receipt is copied between these configurations.

The completed native full-bank `.ext` was archived after timing confirmed no
live/future readers. `r1280-v2/native-ext-compression.json` records source and
independently decompressed SHA-256, byte counts, and no-reader checks before
raw removal. Restore for reproduction with `gzip -dc W6_PITCH_BANK_FLAT.ext.gz
> W6_PITCH_BANK_FLAT.ext` in that directory, with enough space to retain the
22 GiB reserve; verify SHA-256 `73b3502c7294f325537d86a8b62a5b94ae75d93224c933e23dffc143c00c3717`.

The four completed full-bank SPICE netlists (`extracted`, `canonical`,
`reference`, `reference-wrong-width`) are also losslessly archived with `.gz`
suffixes. `r1280-v2/spice-evidence-compression.json` records native/archive/
roundtrip hashes, sizes, no-reader checks and restoration instructions.
Restore required files before rerunning compare or Netgen; preserve22GiB free.
Historical process receipts accurately retain paths used before archival.

The completed 64-row native `.ext` and four SPICE files are losslessly
archived too. `r64-v2/slice-evidence-compression.json` preserves original and
archive hashes, independent decompressed hashes, two no-reader checks per
file, and restoration commands. All prior extraction/LVS receipts remain.
After this final archival and report update, verification outputs are frozen;
`freeze.json` inventories their sizes and SHA-256 values (excluding itself).
