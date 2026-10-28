# Lead guidance (concurrency)

You may run your F64 `positive` simulation NOW, concurrently with W1's and W1b's. The "one long simulation at a time" rule applies per worker, not globally. Each simulation is single-threaded and uses about 2 GB, and the Mac has headroom. Keep the 20 GiB disk floor and `nice -n 10`. Continue from where you stopped (compile → fixture → positive → render → RESULTS.md).
