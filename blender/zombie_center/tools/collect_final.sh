#!/bin/bash
# Collect EP01 final frames from the worker branches claude/zc-ep01-final-01..23 and report missing frames.
cd "$(dirname "$0")/../../.."
for i in $(seq -w 1 23); do
  b=claude/zc-ep01-final-$i
  git fetch -q origin "$b" 2>/dev/null || { echo "$b: not pushed yet"; continue; }
  git checkout FETCH_HEAD -- blender/zombie_center/episodes/ep01/out 2>/dev/null && git reset -q blender/zombie_center/episodes/ep01/out
done
O=blender/zombie_center/episodes/ep01/out
miss() { local n=0; for f in $(seq $2 $3); do [ -s "$O/$1/f_$(printf %04d $f).png" ] || n=$((n+1)); done; echo "$1 $2-$3 missing $n"; }
miss sc001 1 1080; miss sc002 1081 2684; miss sc003 2685 3252; miss sc004 3253 4332; miss sc005 1 1919
