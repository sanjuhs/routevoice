# Recorded W2 physical launch commands

These are provenance commands, not a request to rerun failed attempts. Run directories and frozen `resolved.json` files retain each attempt’s actual configuration. Current base configs incorporate documented corrections. Checkpoint paths may require archive restoration; see `evidence/checkpoint-path-audit.json`.

## rv_fixed_proj320_rom-v1.supervisor.json

Exit: `-15`; stop reason: `supervisor interrupted: `; elapsed: 103.54 seconds.

```sh
env bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom v1
```

## rv_fixed_proj320_rom-condensed.supervisor.json

Exit: `-15`; stop reason: `disk safety margin: free below 22 GiB`; elapsed: 100.12 seconds.

```sh
env bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom condensed
```

## rv_fixed_proj320_dp-v1.supervisor.json

Exit: `None`; stop reason: `disk safety margin: free below 22 GiB`; elapsed: 0.00 seconds.

```sh
env bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp v1
```

## rv_fixed_proj64x320_rom-v1.supervisor.json

Exit: `1`; stop reason: `None`; elapsed: 10.01 seconds.

```sh
env bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj64x320_rom v1
```

## rv_fixed_proj64x320_rom-restored.supervisor.json

Exit: `2`; stop reason: `None`; elapsed: 1636.44 seconds.

```sh
env bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj64x320_rom restored
```

## rv_fixed_proj64x320_rom-util30.supervisor.json

Exit: `-15`; stop reason: `supervisor interrupted: `; elapsed: 3942.62 seconds.

```sh
env W2_FROM_STEP=OpenROAD.Floorplan W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj64x320_rom-restored/12-openroad-staprepnr/state_out.json bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj64x320_rom util30
```

## rv_fixed_proj320_dp-synthesis.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 495.46 seconds.

```sh
env W2_TO_STEP=Yosys.Synthesis W2_NUM_THREADS=1 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp synthesis
```

## rv_fixed_proj320_dp-precheck.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 350.32 seconds.

```sh
env W2_FROM_STEP=Checker.YosysUnmappedCells W2_TO_STEP=OpenROAD.STAPrePNR W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj320_dp-synthesis/06-yosys-synthesis/state_out.json W2_NUM_THREADS=1 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp precheck
```

## rv_fixed_proj64x320_rom-clock200.supervisor.json

Exit: `-15`; stop reason: `disk safety margin: free below 22 GiB`; elapsed: 5890.26 seconds.

```sh
env W2_FROM_STEP=OpenROAD.ResizerTimingPostCTS W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/evidence/slice-200ns-initial-state.json W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj64x320_rom-200ns.json bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj64x320_rom clock200
```

## rv_fixed_proj64x320_rom-pre-route-activity.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 75.07 seconds.

```sh
env W2_FROM_STEP=OpenROAD.STAMidPNR W2_TO_STEP=OpenROAD.STAMidPNR W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj64x320_rom-clock200/02-openroad-stamidpnr-2/state_out.json W2_NUM_THREADS=1 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj64x320_rom-pre-route-activity.json W2_VCD=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/tmp/rv_fixed_proj64x320_rom-pre-route-activity.vcd bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj64x320_rom pre-route-activity
```

## rv_fixed_proj64x320_rom-pre-route-slash-activity.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 105.09 seconds.

```sh
env W2_FROM_STEP=OpenROAD.STAMidPNR W2_TO_STEP=OpenROAD.STAMidPNR W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj64x320_rom-clock200/02-openroad-stamidpnr-2/state_out.json W2_NUM_THREADS=1 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj64x320_rom-pre-route-slash-activity.json W2_VCD=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/tmp/rv_fixed_proj64x320_rom-pre-route-slash-activity.vcd bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj64x320_rom pre-route-slash-activity
```

## rv_fixed_proj320_dp-physical20.supervisor.json

Exit: `1`; stop reason: `None`; elapsed: 95.07 seconds.

```sh
env W2_FROM_STEP=OpenROAD.Floorplan W2_TO_STEP=OpenROAD.STAMidPNR-1 W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj320_dp-precheck/06-openroad-staprepnr/state_out.json bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp physical20
```

## rv_fixed_proj320_dp-io-microns.supervisor.json

Exit: `-15`; stop reason: `supervisor interrupted: `; elapsed: 1853.61 seconds.

```sh
env W2_FROM_STEP=OpenROAD.IOPlacement W2_TO_STEP=OpenROAD.STAMidPNR-1 W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj320_dp-physical20/12-openroad-globalplacementskipio/state_out.json bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp io-microns
```

## rv_fixed_proj64x320_rom-preroute-render.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 10.01 seconds.

```sh
env W2_FROM_STEP=KLayout.Render W2_TO_STEP=KLayout.Render W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj64x320_rom-clock200/02-openroad-stamidpnr-2/state_out.json W2_NUM_THREADS=1 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj64x320_rom-200ns.json bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj64x320_rom preroute-render
```

## rv_fixed_proj320_rom-synthesis-retry.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 635.99 seconds.

```sh
env W2_TO_STEP=Yosys.Synthesis W2_NUM_THREADS=1 W2_MIN_FREE_GIB=23.5 W2_LIMIT_SECONDS=3600 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom synthesis-retry
```

## rv_fixed_proj64x320_rom-pre-route-gate-cell-activity.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 100.16 seconds.

```sh
env W2_FROM_STEP=OpenROAD.STAMidPNR W2_TO_STEP=OpenROAD.STAMidPNR W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj64x320_rom-clock200/02-openroad-stamidpnr-2/state_out.json W2_NUM_THREADS=1 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj64x320_rom-pre-route-gate-cell-activity.json W2_VCD=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/vectors/rv_fixed_proj64x320_rom.gate-cell-pins-power-200ns.normalized.vcd.gz W2_MIN_FREE_GIB=23 W2_LIMIT_SECONDS=900 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj64x320_rom pre-route-gate-cell-activity
```

## rv_fixed_proj320_dp-typical-repair20.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 1106.60 seconds.

```sh
env W2_FROM_STEP=OpenROAD.RepairDesignPostGPL W2_TO_STEP=OpenROAD.STAMidPNR-1 W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj320_dp-io-microns/07-openroad-stamidpnr/state_out.json W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_dp-typical-repair.json bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp typical-repair20
```

## rv_fixed_proj320_rom-physical20.supervisor.json

Exit: `-15`; stop reason: `supervisor interrupted: `; elapsed: 3714.54 seconds.

```sh
env W2_FROM_STEP=Checker.YosysUnmappedCells W2_TO_STEP=OpenROAD.STAMidPNR-1 W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj320_rom-synthesis-retry/06-yosys-synthesis/state_out.json W2_NUM_THREADS=4 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_rom-physical20.json W2_LIMIT_SECONDS=6564 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom physical20
```

## rv_fixed_proj320_dp-util20-200ns.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 1782.59 seconds.

```sh
env W2_FROM_STEP=OpenROAD.Floorplan W2_TO_STEP=OpenROAD.STAMidPNR-1 W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/evidence/dp-util20-200ns-initial-state.json W2_NUM_THREADS=4 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_dp-util20-200ns.json bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp util20-200ns
```

## rv_fixed_proj320_dp-pre-route-rtl-activity.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 215.25 seconds.

```sh
env W2_FROM_STEP=OpenROAD.STAMidPNR W2_TO_STEP=OpenROAD.STAMidPNR W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/evidence/rv_fixed_proj320_dp-pre-route-rtl-activity-minimal-state.json W2_NUM_THREADS=1 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_dp-pre-route-rtl-activity.json W2_VCD=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/tmp/rv_fixed_proj320_dp-pre-route-rtl-activity.vcd W2_MIN_FREE_GIB=23 W2_LIMIT_SECONDS=900 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp pre-route-rtl-activity
```

## rv_fixed_proj320_dp-pre-route-render.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 10.01 seconds.

```sh
env W2_FROM_STEP=KLayout.Render W2_TO_STEP=KLayout.Render W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/evidence/rv_fixed_proj320_dp-pre-route-render-state.json W2_NUM_THREADS=1 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_dp-util20-200ns.json W2_MIN_FREE_GIB=23 W2_LIMIT_SECONDS=600 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_dp pre-route-render
```

## rv_fixed_proj320_rom-util20-200ns.supervisor.json

Exit: `2`; stop reason: `None`; elapsed: 680.95 seconds.

```sh
env W2_FROM_STEP=OpenROAD.Floorplan W2_TO_STEP=OpenROAD.STAMidPNR-1 W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/evidence/full-rom-util20-200ns-initial-state.json W2_NUM_THREADS=4 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_rom-util20-200ns.json W2_LIMIT_SECONDS=2833 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom util20-200ns
```

## rv_fixed_proj320_rom-util20-density35-200ns.supervisor.json

Exit: `2`; stop reason: `None`; elapsed: 570.74 seconds.

```sh
env W2_FROM_STEP=OpenROAD.GlobalPlacement W2_TO_STEP=OpenROAD.STAMidPNR-1 W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj320_rom-util20-200ns/15-odb-applydeftemplate/state_out.json W2_NUM_THREADS=4 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_rom-util20-density35-200ns.json W2_LIMIT_SECONDS=2126 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom util20-density35-200ns
```

## rv_fixed_proj320_rom-util20-density35-noinflate-200ns.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 1046.48 seconds.

```sh
env W2_FROM_STEP=OpenROAD.GlobalPlacement W2_TO_STEP=OpenROAD.STAMidPNR-1 W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj320_rom-util20-200ns/15-odb-applydeftemplate/state_out.json W2_NUM_THREADS=4 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_rom-util20-density35-noinflate-200ns.json W2_LIMIT_SECONDS=1520 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom util20-density35-noinflate-200ns
```

## rv_fixed_proj320_rom-route-util20-density35-noinflate-200ns.supervisor.json

Exit: `1`; stop reason: `None`; elapsed: 465.64 seconds.

```sh
env W2_FROM_STEP=OpenROAD.ResizerTimingPostCTS W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/runs/rv_fixed_proj320_rom-util20-density35-noinflate-200ns/09-openroad-stamidpnr-1/state_out.json W2_NUM_THREADS=4 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_rom-util20-density35-noinflate-200ns.json W2_LIMIT_SECONDS=473 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom route-util20-density35-noinflate-200ns
```

## rv_fixed_proj320_rom-pre-route-render.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 10.02 seconds.

```sh
env W2_FROM_STEP=KLayout.Render W2_TO_STEP=KLayout.Render W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/evidence/rv_fixed_proj320_rom-pre-route-render-state.json W2_NUM_THREADS=1 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_rom-util20-density35-noinflate-200ns.json W2_MIN_FREE_GIB=23 W2_LIMIT_SECONDS=600 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom pre-route-render
```

## rv_fixed_proj320_rom-pre-route-rtl-activity.supervisor.json

Exit: `0`; stop reason: `None`; elapsed: 115.17 seconds.

```sh
env W2_FROM_STEP=OpenROAD.STAMidPNR W2_TO_STEP=OpenROAD.STAMidPNR W2_INITIAL_STATE=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/evidence/rv_fixed_proj320_rom-pre-route-rtl-activity-minimal-state.json W2_NUM_THREADS=1 W2_CONFIG_PATH=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/configs/rv_fixed_proj320_rom-pre-route-rtl-activity.json W2_VCD=/Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/tmp/rv_fixed_proj320_rom-pre-route-rtl-activity.vcd W2_MIN_FREE_GIB=23 W2_LIMIT_SECONDS=600 bash /Users/sanju/Desktop/coding/llm-hardware/route-voice-llm-hardware-v1/routing-voice-chip-design/overnight-20261014/fabric/run_flow.sh rv_fixed_proj320_rom pre-route-rtl-activity
```

Every completed LibreLane step has its actual tool command in `runs/<attempt>/<step>/COMMANDS`. Gate compiler/simulator argv are in `evidence/*gate*verification.json` and `evidence/*activity-stream.json`. Original RTL commands are in `verify.sh`; the exact NumPy seed, dimensions and input hashes are in `evidence/generation.json`.
