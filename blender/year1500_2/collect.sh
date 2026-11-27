#!/bin/bash
# Pull the mp4 chunks rendered by the cloud workers (branches render-y1500-<a>-<b>, chunks/chunk_<a>-<b>.mp4)
# and unpack each into frames/ (only frames not already rendered here). Ends when every frame exists.
cd "$(dirname "$0")"
T=/tmp/claude-0/y1500_collect_p2; mkdir -p $T/chunks
RANGES=${RANGES:-"1-140 141-288 289-436 437-584 585-732 733-880 881-1028 1029-1176 1177-1324 1325-1472 1473-1620 1621-1768 1769-1916 1917-2064"}
PFX=${PFX:-render-y1500p2-}
while true; do
  for r in $RANGES; do
    c=$T/chunks/chunk_$r.mp4
    [ -s $c ] && continue
    git fetch -q origin $PFX$r 2>/dev/null || continue
    git show FETCH_HEAD:chunks/chunk_$r.mp4 > $c.part 2>/dev/null && mv $c.part $c || { rm -f $c.part; continue; }
    a=${r%-*}; rm -rf $T/x; mkdir -p $T/x
    ffmpeg -v error -i $c -start_number $a $T/x/f_%04d.png
    n=0; for f in $T/x/f_*.png; do [ -s "frames/$(basename $f)" ] || { cp $f frames/; n=$((n+1)); }; done
    echo "$(date +%H:%M) chunk $r arrived: $n new frames"
  done
  left=$(python3 -c "import os;from captions import FLASHBACK as F,WAKE as W;print(sum(1 for f in range(1,2065) if not (F[1]*24<f<=W*24) and not os.path.exists(f'frames/f_{f:04d}.png')))")
  echo "$(date +%H:%M) left $left"
  [ "$left" = 0 ] && { echo ALL_FRAMES; break; }
  sleep 300
done
