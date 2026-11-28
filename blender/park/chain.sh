#!/bin/bash
# Final render of «پارک» with auto-restart:  ./chain.sh 0 1439   (frames are skipped if they exist)
cd "$(dirname "$0")"
exec 9>.chain.lock; flock -n 9 || { echo "already running"; exit 0; }
A=${1:-0}; B=${2:-1439}
LOG=render.log
for try in $(seq 1 60); do
  miss=0; for f in $(seq $A $B); do [ -s frames/f_$(printf %04d $f).png ] || { miss=1; break; }; done
  [ $miss = 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  ../cast/bpy.sh scene.py --render $A $B >> $LOG 2>&1
done
echo CHAIN_DONE >> $LOG
