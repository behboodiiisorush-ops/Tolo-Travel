#!/bin/bash
# Render frames A..B of «جرقه» with auto-restart.  ./chain.sh 1 1152   (builds spark2.blend first if missing)
cd "$(dirname "$0")"
A=${1:-1}; B=${2:-1152}
export SAMPLES=${SAMPLES:-16}
LOG=/tmp/claude-0/spark2_render_$A.log
mkdir -p /tmp/claude-0
[ -f spark2.blend ] || ../cast/bpy.sh scene.py --save >> $LOG 2>&1
for try in 1 2 3 4 5 6; do
  ../cast/bpy.sh render.py $A $B >> $LOG 2>&1
  miss=0; for f in $(seq $A $B); do [ -f frames/f_$(printf %04d $f).png ] || { miss=1; break; }; done
  [ $miss = 0 ] && break
done
echo CHAIN_DONE >> $LOG
