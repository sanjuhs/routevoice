#!/usr/bin/env bash
# run_unit.sh <unit>: generic (+gf180 if generic passes) and fpga (if listed), no memory cap
u=$1; cd /Users/sanju/rvssd/w12-local-retry/units/$u || exit 1
plan=/Users/sanju/rvssd/w12-local-retry/plan.json
want(){ python3 -c "import json,sys;p=json.load(open('$plan'));print(int(any(j==['$u','$1'] for j in p['jobs'])))"; }
run(){ s=$(date +%s); /usr/bin/time -l yosys -q -l $1.log $1.ys > $1.console 2>&1; rc=$?; echo "{\"unit\":\"$u\",\"stage\":\"$1\",\"exit\":$rc,\"wall_s\":$(( $(date +%s)-s )),\"peak_rss_bytes\":$(grep -m1 'maximum resident' $1.console | awk '{print $1}')}" > $1.result.json; echo "$u $1 exit=$rc"; return $rc; }
[ "$(want generic)" = 1 ] && { run generic && run gf180; }
[ "$(want fpga)" = 1 ] && run fpga
