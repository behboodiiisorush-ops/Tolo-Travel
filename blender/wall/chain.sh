#!/bin/bash
# build the scene once, then render all frames; restarts the renderer whenever EEVEE crashes
cd "$(dirname "$0")"
[ -f wall.blend ] || ../cast/bpy.sh scene.py --save > /tmp/claude-0/wall_build.log 2>&1
A=${1:-1}; B=${2:-1812}           # odd frames A..B (rendered on twos)
mkdir -p frames
for i in $(seq 1 300); do
  missing=0
  for f in $(seq $((A | 1)) 2 $B); do [ -s frames/$(printf 'f_%04d.png' $f) ] || { missing=1; break; }; done
  [ $missing = 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A-$B >> /tmp/claude-0/wall_render_$A.log 2>&1
done
echo CHAIN_DONE >> /tmp/claude-0/wall_render.log
