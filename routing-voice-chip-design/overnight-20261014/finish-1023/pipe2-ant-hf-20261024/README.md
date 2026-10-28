# Antenna close-out run backup record (24 Oct 2026)

The antenna close-out run (`~/rvssd/pipe2-local/runs/pipe2-ant`, plus `inputs/full-pipe2-ant-local.json` and `flow-ant.log`: 46 GB, 680 files) was added to the public Hugging Face dataset
**https://huggingface.co/datasets/sanjuhs/routevoice-engine-fix2-20261024**, under `archives/pipe2-ant/`. It is a tar + zstd archive of 9.0 GB in 2 parts. The earlier fix-2 archive (`archives/pipe2-local/`) is unchanged in the same dataset.

**Verification.** The new files were downloaded back from HF. Both part checksums matched, and the extracted tree matched `manifest-pipe2-ant.sha256` for **680 of 680 files** (`verify.txt`, `upload.log`). A secret scan run before packing found nothing.

| File | Contents |
|---|---|
| `manifest-pipe2-ant.sha256` | SHA-256 of every file before packing |
| `parts-pipe2-ant.sha256` | SHA-256 of each archive part |
| `verify.txt` | per-file check output |
| `pack_upload.sh` | the script that was run |
| `README-hf.md` | the dataset card (now covers both archives), with restore commands |

With this, both SSD runs (`runs/pipe2` and `runs/pipe2-ant`) have verified copies on HF, so the SSD is no longer the only copy.
