#!/bin/bash
# build the scene once, then render all frames; restarts the renderer whenever EEVEE crashes
cd "$(dirname "$0")"
[ -f bird.blend ] || ../cast/bpy.sh scene.py --save > /tmp/claude-0/bird_build.log 2>&1
N=1464
for i in $(seq 1 300); do
  [ $(ls frames/f_*.png 2>/dev/null | wc -l) -ge $N ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py 1-$N >> /tmp/claude-0/bird_render.log 2>&1
done
echo CHAIN_DONE >> /tmp/claude-0/bird_render.log
