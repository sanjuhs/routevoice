# Pod backup record: 22 Oct 2026

The RunPod pod `rv-overnight-pnr2` was deleted after its full `/workspace` was uploaded to the public Hugging Face dataset
**https://huggingface.co/datasets/sanjuhs/routevoice-pod-final-20261022** and verified.

| File | What it is |
|---|---|
| `hf-verify.json` | The check result: every archive was downloaded back from HF and every tar member hashed. 105,827/105,827 files match, 0 missing, 0 problems. |
| `pod-manifest.sha256` | SHA-256 of all 105,826 files under the pod's `rv/`, taken before packing |
| `<archive>.parts.sha256`, `<archive>.filecount` | Checksum of each archive part, and the file count inside each tar |
| `upload.log` | The pack-and-upload log from the pod |
| `pack_upload.sh`, `verify_hf.py` | The scripts that were run on the pod |
| `README-hf.md` | The README published on the HF dataset, including restore commands |

There are six archives:
- `w10-runs-full`: the routed engine;
- `w10-runs-C`;
- `w10-rest`;
- `w15-chip`;
- `w12-synth`;
- `misc`: inputs, the PDK copy, tools and `setup.log`.

To resume the routed-engine work, restore `w10-runs-full` onto a new pod (see `README-hf.md`).
