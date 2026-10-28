# Commands

From repository root, use `PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 .venv/bin/python` for each Python command below. Run sequentially, one CPU thread. Check `df -h /` before launches; preserve at least22GiB free. Do not rerun into retained output names: use a fresh verification run name and readback filename. Native Magic/Netgen are resolved from the installed Nix tools; every expanded invocation is saved in bank3-v1/*-command.json.

```sh
.venv/bin/python overnight-20261014/taalas-array/tall-bank/verification/readback.py --gds overnight-20261014/taalas-array/tall-bank/r320/assembly.gds --output assembly-r320-v1-readback.json
.venv/bin/python overnight-20261014/taalas-array/tall-bank/verification/verify.py extract --gds overnight-20261014/taalas-array/tall-bank/r320/bank3.gds --top TALL_BANK_R320_B03 --bank 3 --run bank3-v1
.venv/bin/python overnight-20261014/taalas-array/tall-bank/verification/verify.py compare --gds overnight-20261014/taalas-array/tall-bank/r320/bank3.gds --top TALL_BANK_R320_B03 --bank 3 --run bank3-v1
.venv/bin/python overnight-20261014/taalas-array/tall-bank/verification/control_caps.py --run bank3-v1
.venv/bin/python overnight-20261014/taalas-array/tall-bank/verification/verify.py partitions --gds overnight-20261014/taalas-array/tall-bank/r320/bank3.gds --top TALL_BANK_R320_B03 --bank 3 --run bank3-v1
.venv/bin/python overnight-20261014/taalas-array/tall-bank/verification/readback.py --gds overnight-20261014/taalas-array/tall-bank/r1280/assembly.gds --rows 1280 --bank 0 --output assembly-r1280-v1-readback.json
.venv/bin/python overnight-20261014/taalas-array/tall-bank/verification/extra_lvs.py
.venv/bin/python overnight-20261014/taalas-array/tall-bank/verification/compress_ext.py
```

`extra_lvs.py` and `compress_ext.py` intentionally identify bank3-v1; copy/change their run path for a new experiment. The first monolithic Netgen command is bounded to120s; the retained successful run took42.27s. The compression script verifies both original and decompressed bytes/hash before replacing the uncompressed intermediate. Restore inside bank3-v1 using:

```sh
gzip -dc W5_TALL_BANK_FLAT.ext.gz > W5_TALL_BANK_FLAT.ext
```

The expected restored SHA256 is27453a185fd623e9cc10188b7c8bbb2be0ae90576fc7deff2c216c2364ae2718.
