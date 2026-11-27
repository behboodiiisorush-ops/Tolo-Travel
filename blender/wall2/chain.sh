#!/bin/bash
# build wall2.blend once, then render frames A..B (default all); restarts the renderer if it crashes
# usage: ./chain.sh [A B]
cd "$(dirname "$0")"
N=1548
A=${1:-1}; B=${2:-$N}
LOG=${LOG:-/tmp/wall2_render.log}
[ -s wall2.blend ] || ../cast/bpy.sh scene.py --save > /tmp/wall2_build.log 2>&1
missing() { local m=0; for f in $(seq $A $B); do [ -s frames/f_$(printf %04d $f).png ] || m=$((m+1)); done; echo $m; }
for i in $(seq 1 300); do
  [ "$(missing)" -eq 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A-$B >> $LOG 2>&1
done
echo CHAIN_DONE >> $LOG
