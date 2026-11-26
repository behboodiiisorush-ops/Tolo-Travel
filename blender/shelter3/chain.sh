#!/bin/bash
# Build shelter3.blend once (if missing), then render the odd frames A..B; restarts the renderer if EEVEE crashes.
#   ./chain.sh 1 1200        (needs blender/cast/setup.sh done and libEGL: apt-get install -y libegl1 libegl-mesa0)
cd "$(dirname "$0")"
A=${1:-1}; B=${2:?give the last frame}
LOG=${LOG:-/tmp/claude-0}
mkdir -p "$LOG" frames
[ -f shelter3.blend ] || SAMPLES=${SAMPLES:-4} ../cast/bpy.sh scene.py --save > "$LOG/sh3_build.log" 2>&1
for i in $(seq 1 200); do
  missing=0
  for f in $(seq $((A | 1)) 2 $B); do [ -s frames/$(printf 'f_%04d.png' $f) ] || { missing=1; break; }; done
  [ $missing = 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A-$B >> "$LOG/sh3_render_$A.log" 2>&1
done
echo CHAIN_DONE >> "$LOG/sh3_render_$A.log"
