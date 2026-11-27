#!/bin/bash
# build the scene once, then render frames A..B (default all); restarts the renderer whenever EEVEE crashes
# usage: ./chain.sh [A B]
cd "$(dirname "$0")"
N=1464
A=${1:-1}; B=${2:-$N}
[ -f bird.blend ] || ../cast/bpy.sh scene.py --save > /tmp/bird_build.log 2>&1
missing() { local m=0; for f in $(seq $A $B); do [ -s frames/f_$(printf %04d $f).png ] || m=$((m+1)); done; echo $m; }
for i in $(seq 1 300); do
  [ "$(missing)" -eq 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A-$B >> /tmp/bird_render.log 2>&1
done
echo CHAIN_DONE >> /tmp/bird_render.log
