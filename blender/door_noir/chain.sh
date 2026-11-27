#!/bin/bash
# build the scene once, then render frames A..B (default all); restarts the renderer if Blender dies
# usage: ./chain.sh [A B]
cd "$(dirname "$0")"
N=1128
A=${1:-1}; B=${2:-$N}
LOG=${LOG:-/tmp/door_render.log}
[ -f door.blend ] || ../cast/bpy.sh scene.py --save > /tmp/door_build.log 2>&1
missing() { local m=0; for f in $(seq $A $B); do [ -s frames/f_$(printf %04d $f).png ] || m=$((m+1)); done; echo $m; }
for i in $(seq 1 100); do
  [ "$(missing)" -eq 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A-$B >> $LOG 2>&1
done
echo CHAIN_DONE $A $B >> $LOG
