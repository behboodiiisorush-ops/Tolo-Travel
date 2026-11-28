#!/bin/bash
# build the scene once, then render frames A..B (default all); restarts the renderer whenever EEVEE crashes
cd "$(dirname "$0")"
A=${1:-1}; B=${2:-1548}
[ -f radio.blend ] || ../cast/bpy.sh scene.py --save > /tmp/claude-0/radio_build.log 2>&1
for i in $(seq 1 300); do
  n=0; for f in $(seq $A $B); do [ -s frames/f_$(printf %04d $f).png ] && n=$((n+1)); done
  [ $n -ge $((B-A+1)) ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A-$B >> /tmp/claude-0/radio_render.log 2>&1
done
echo CHAIN_DONE >> /tmp/claude-0/radio_render.log
