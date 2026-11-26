#!/bin/bash
# render frames A..B of the Arian walk-in test (restarts Blender if it dies): ./chain_arian.sh 1 150
cd "$(dirname "$0")"
A=${1:-1}; B=${2:-150}
for try in 1 2 3 4 5; do
  ../cast/bpy.sh arian_board.py --part anim --frames $A $B >> /tmp/claude-0/arian_$A.log 2>&1
  miss=0; for f in $(seq $A $B); do [ -f frames/arian/f_$(printf %04d $f).png ] || miss=1; done
  [ $miss = 0 ] && break
done
echo CHAIN_DONE >> /tmp/claude-0/arian_$A.log
