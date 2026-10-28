# Fix-2 engine run backup record (24 Oct 2026)

The complete fix-2 LibreLane run (`~/rvssd/pipe2-local`: 51 GB, 1,227 files) is in the public Hugging Face dataset
**https://huggingface.co/datasets/sanjuhs/routevoice-engine-fix2-20261024**. It is stored as a tar + zstd archive of 9.3 GB in 2 parts.

**Verification.** The dataset was downloaded back from HF. Both part checksums matched, and the extracted tree matched `manifest.sha256` for **1,227 of 1,227 files** (`verify.txt`, `upload.log`). A secret scan run before upload found nothing.

| File | Contents |
|---|---|
| `manifest.sha256` | SHA-256 of every file before packing |
| `parts.sha256` | SHA-256 of each archive part |
| `verify.txt` | per-file check output |
| `pack_upload.sh` | the script that was run |
| `README-hf.md` | the dataset card, with restore commands |

The SSD copy is no longer the only copy.
