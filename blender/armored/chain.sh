#!/bin/bash
# build the scene once, then render all frames; restarts the renderer whenever EEVEE crashes.
# Needs libEGL (apt-get install -y libegl1 libegl-mesa0) for EEVEE on a headless server.
cd "$(dirname "$0")"
LOG=${LOG:-/tmp/claude-0}
mkdir -p "$LOG"
[ -f armored.blend ] || ../cast/bpy.sh scene.py --save > "$LOG/armored_build.log" 2>&1
N=1694
for i in $(seq 1 300); do
  [ $(ls frames/f_*.png 2>/dev/null | wc -l) -ge $N ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py 1-$N >> "$LOG/armored_render.log" 2>&1
done
echo CHAIN_DONE >> "$LOG/armored_render.log"
