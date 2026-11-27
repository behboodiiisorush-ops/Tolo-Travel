#!/bin/bash
# build nila.blend once, then render every frame; restarts the renderer if EEVEE crashes
cd "$(dirname "$0")"
[ -f nila.blend ] || ../cast/bpy.sh scene.py --save > build.log 2>&1
A=${1:-1}; B=${2:-264}
mkdir -p frames
for i in $(seq 1 50); do
  missing=0
  for f in $(seq $A $B); do [ -s frames/$(printf 'f_%04d.png' $f) ] || { missing=1; break; }; done
  [ $missing = 0 ] && break
  ../cast/bpy.sh render.py $A $B ${PCT:-67} ${SAMPLES:-24} >> render.log 2>&1
done
echo CHAIN_DONE >> render.log
