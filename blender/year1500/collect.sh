#!/bin/bash
# Pull frames rendered by the cloud workers (branches render-y1500-a/b/c, bundle/frames) into frames/.
cd "$(dirname "$0")"
T=/tmp/claude-0/y1500_collect; mkdir -p $T
while true; do
  for b in a b c; do
    git fetch -q origin render-y1500-$b 2>/dev/null || continue
    rm -rf $T/x; mkdir -p $T/x
    git archive FETCH_HEAD bundle/frames 2>/dev/null | tar -x -C $T/x 2>/dev/null
    for f in $T/x/bundle/frames/f_*.png; do
      [ -s "$f" ] && [ ! -s "frames/$(basename $f)" ] && cp "$f" frames/
    done
  done
  left=$(python3 -c "import os;from captions import FLASHBACK as F,WAKE as W;print(sum(1 for f in range(1,1729) if not (F[1]*24<f<=W*24) and not os.path.exists(f'frames/f_{f:04d}.png')))")
  echo "$(date +%H:%M) left $left"
  [ "$left" = 0 ] && { echo ALL_FRAMES; break; }
  sleep 300
done
