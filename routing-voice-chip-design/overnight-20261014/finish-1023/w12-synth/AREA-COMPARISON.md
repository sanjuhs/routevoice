# GF180 comparison contract

The final floorplan allowances are frontend 12 mm², encoder dynamic attention 18 mm², decoder dynamic attention 15 mm², producer 6 mm² and control/clock/IO 12 mm²: **63 mm² total assumed logic allowance**. The shared projection engine, array decoder/phase allowance, ordinary registers and mutable SRAM are separate rows. The frontend 48.788 mm² row includes the 12 mm² logic allowance; do not compare all 48.788 mm² against logic alone.

W12 maps the actual instantiated v2 recognizer, with ROM-service modules excluded. The floorplan instead assumes a shared-engine physical architecture and separate SRAM. A generic `synth` run maps surviving writable memories into gates/flip-flops; its GF180 cell-area sum then includes that writable-state implementation. It must not be described as the same memory-macro budget. Neither quantity includes routed placement area.

The comparison uses `gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib`; Liberty cell areas are µm² and are divided by 1,000,000 for mm². No ABC delay target, placement utilization, clock tree or timing closure is implied. Black-box internal address/control/queue logic is excluded along with the ROM services and must be supplied in real macro implementations.

Final mapped measurements will be recorded in `results.json` and `RESULTS.md` when available. A synthesis failure leaves the area unset.
