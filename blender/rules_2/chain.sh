#!/bin/bash
# build the scene once, then render frames A..N; restarts the renderer whenever EEVEE crashes.
#   ./chain.sh            all frames        A=1200 ./chain.sh   from frame 1200 (backup render from the end)
cd "$(dirname "$0")"
[ -f rules_2.blend ] || ../cast/bpy.sh scene.py --spy --save > /tmp/claude-0/rules2_build.log 2>&1
A=${A:-1}; N=${N:-1812}
for i in $(seq 1 300); do
  left=$(python3 -c "import os;print(sum(1 for f in range($A,$N+1) if not (os.path.exists(f'frames/f_{f:04d}.png') and os.path.getsize(f'frames/f_{f:04d}.png')>0)))")
  [ "$left" = 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A-$N >> /tmp/claude-0/rules2_render.log 2>&1
done
echo CHAIN_DONE >> /tmp/claude-0/rules2_render.log
