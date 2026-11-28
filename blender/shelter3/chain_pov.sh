#!/bin/bash
# «پناهگاه ۳» (vertical POV, the series' characters): build pov.blend once (if missing), then render the odd
# frames A..B with Cycles; restarts the renderer if it crashes.   ./chain_pov.sh 1 432
cd "$(dirname "$0")"
A=${1:-1}; B=${2:?give the last frame}
LOG=${LOG:-/tmp/claude-0}
if [ "$WIDE" = 1 ]; then FR=frames_wide; BL=pov_wide.blend; else FR=frames; BL=pov.blend; fi
mkdir -p "$LOG" $FR
[ -f $BL ] || ../cast/bpy.sh pov.py --save > "$LOG/pov_build.log" 2>&1
for i in $(seq 1 200); do
  missing=0
  for f in $(seq $((A | 1)) 2 $B); do [ -s $FR/$(printf 'f_%04d.png' $f) ] || { missing=1; break; }; done
  [ $missing = 0 ] && break
  find $FR -size 0 -delete 2>/dev/null
  ../cast/bpy.sh render_pov.py $A-$B >> "$LOG/pov_render_$A.log" 2>&1
done
echo CHAIN_DONE >> "$LOG/pov_render_$A.log"
