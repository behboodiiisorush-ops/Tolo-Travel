#!/bin/bash
# build the scene once, then render all frames; restarts the renderer whenever EEVEE crashes
cd "$(dirname "$0")"
[ -f year1500.blend ] || ../cast/bpy.sh scene.py --save > /tmp/claude-0/y1500_build.log 2>&1
N=${N:-1728}; A=${A:-1}
BLACK=$(python3 -c "from captions import FLASHBACK as F, WAKE as W; print(sum(1 for f in range(1, 2000) if F[1]*24 < f <= W*24))")
for i in $(seq 1 300); do
  [ "$(python3 -c "import os;from captions import FLASHBACK as F,WAKE as W;print(sum(1 for f in range($A,$N+1) if not (F[1]*24<f<=W*24) and not os.path.exists(f\"frames/f_{f:04d}.png\")))")" = 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A-$N >> /tmp/claude-0/y1500_render.log 2>&1
done
echo CHAIN_DONE >> /tmp/claude-0/y1500_render.log
