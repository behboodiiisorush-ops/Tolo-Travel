#!/bin/bash
# build the scene once, then render all frames; restarts the renderer whenever EEVEE crashes
cd "$(dirname "$0")"
[ -f year1500.blend ] || ../cast/bpy.sh scene.py --save > /tmp/claude-0/y1500_build.log 2>&1
N=1728
BLACK=$(python3 -c "from captions import FLASHBACK as F, WAKE as W; print(sum(1 for f in range(1, 2000) if F[1]*24 < f <= W*24))")
for i in $(seq 1 300); do
  [ $(ls frames/f_*.png 2>/dev/null | wc -l) -ge $((N - BLACK)) ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py 1-$N >> /tmp/claude-0/y1500_render.log 2>&1
done
echo CHAIN_DONE >> /tmp/claude-0/y1500_render.log
