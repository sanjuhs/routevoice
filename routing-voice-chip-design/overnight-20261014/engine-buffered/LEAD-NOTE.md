# W9 shared activity path — 07:19 IST

W9's original activity simulation passed and wrote a 370,949,150-byte SAIF. Its first-pass hash is preserved in `evidence/array_port-mapped-activity.json` (to be snapshotted as `array_port-mapped-activity-first-pass.json`). A separate process, PID 49777 under PID 49775, launched `gate-activity/sim > logs/lead-gate-activity.log` around 07:16 IST and reopened/truncated the same hardcoded SAIF path. W9 is leaving that replay untouched.

The attempted gzip and placed-annotation probe encountered the temporarily empty file; these failures will be preserved. W9 will freeze the completed repeat trace as `evidence/array_port-mapped-speech-w9-frozen.saif` and use that unique immutable path for subsequent annotation/power/archive. Please avoid restarting any executable that writes the frozen path.

Requested-settings physical continuation `buf-v4-physical` still runs RepairDesignPostGPL. Non-clock fanout is verified at <=16 in both synthesis and the placed database. The ideal-pre-CTS diagnostic was stopped as redundant after confirming repair_design.tcl already unsets propagated clocks and DESIGN_REPAIR_REMOVE_BUFFERS=false. See DIAGNOSTICS.md.
