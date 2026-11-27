#!/bin/bash
# Render frames A..B of «جرقه ۲» with auto-restart.  ./chain.sh 1 1296   (builds spark2.blend first if missing)
cd "$(dirname "$0")"
A=${1:-1}; B=${2:-1296}
export SAMPLES=${SAMPLES:-16}
LOG=render.log
[ -f spark2.blend ] || ../cast/bpy.sh scene.py --save >> build.log 2>&1
for try in $(seq 1 50); do
  miss=0; for f in $(seq $A $B); do [ -s frames/f_$(printf %04d $f).png ] || { miss=1; break; }; done
  [ $miss = 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render.py $A $B >> $LOG 2>&1
done
echo CHAIN_DONE >> $LOG
