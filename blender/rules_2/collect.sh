#!/bin/bash
# Pull the mp4 chunks rendered by the cloud workers (branches render-r2-<a>-<b>, chunks/chunk_<a>-<b>.mp4)
# and unpack each into frames/ (only frames not already rendered here). Ends when every frame exists.
cd "$(dirname "$0")"
T=/tmp/claude-0/r2_collect; mkdir -p $T/chunks frames
RANGES=${RANGES:-"1-140 141-280 281-420 421-560 561-700 701-840 841-980 981-1120 1121-1260 1261-1400 1401-1540 1541-1680 1681-1812"}
PFX=${PFX:-render-r2-}
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
  left=$(python3 -c "import os;print(sum(1 for f in range(1,1813) if not os.path.exists(f'frames/f_{f:04d}.png')))")
  echo "$(date +%H:%M) left $left"
  [ "$left" = 0 ] && { echo ALL_FRAMES; pkill -f chain.sh; pkill -f "render.py"; break; }
  sleep 300
done
