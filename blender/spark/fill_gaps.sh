#!/bin/bash
# Backup renderer: pulls helper frame branches, then renders the first still-missing frames (5 at a time)
# from the start of the film, until all 1..N exist.   ./fill_gaps.sh [N] [branch letters...]
cd "$(dirname "$0")"
N=${1:-1392}; shift; BR=${@:-b c d e f g h i j}
LOG=/tmp/claude-0/spark_fill.log
pull() {
  for x in $BR; do
    git fetch -q origin claude/spark-frames-$x 2>/dev/null || continue
    d=$(mktemp -d); git archive FETCH_HEAD blender/spark/frames 2>/dev/null | tar -x -C $d 2>/dev/null
    cp --update=none $d/blender/spark/frames/*.png frames/ 2>/dev/null; rm -rf $d
  done
}
while true; do
  pull
  miss=$(for f in $(seq 1 $N); do [ -f frames/f_$(printf %04d $f).png ] || echo $f; done)
  [ -z "$miss" ] && break
  a=$(echo "$miss" | head -1); b=$a
  for f in $(echo "$miss" | head -5); do [ $f -le $((a+4)) ] && b=$f; done
  echo "rendering $a-$b ($(echo "$miss" | wc -l) missing)" >> $LOG
  SAMPLES=${SAMPLES:-16} ../cast/bpy.sh render.py $a $b >> $LOG 2>&1
done
echo FILL_DONE >> $LOG
