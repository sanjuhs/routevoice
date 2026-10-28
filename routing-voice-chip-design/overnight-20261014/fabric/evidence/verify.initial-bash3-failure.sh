#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export TMPDIR="$PWD/tmp"
for variant in rv_fixed_proj320_rom rv_fixed_proj320_dp rv_fixed_proj64x320_rom; do
  rows=320
  flags=()
  if [[ "$variant" == rv_fixed_proj320_dp ]]; then flags+=(-DEXTERNAL); fi
  if [[ "$variant" == rv_fixed_proj64x320_rom ]]; then rows=64; fi
  nice -n 10 iverilog -g2012 -s tb -DDUT="$variant" -DROWS="$rows" "${flags[@]}" -o "tb/$variant.vvp" "rtl/$variant.sv" tb/tb.sv > "logs/$variant.compile.log" 2>&1
  nice -n 10 vvp "tb/$variant.vvp" "+vcd=vectors/$variant.vcd" > "logs/$variant.verify.log" 2>&1
  tail -2 "logs/$variant.verify.log"
done
