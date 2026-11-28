#!/bin/bash
# pull the helpers' frames (branches claude/wagon7-frames-a..f) into frames/; with "render": render up to 6 missing
# odd frames here (from the end of the film backwards, so a helper still working from its start is not duplicated)
cd "$(dirname "$0")"
mkdir -p frames
for x in a b c d e f; do
  git -C ../.. fetch -q origin claude/wagon7-frames-$x 2>/dev/null || continue
  git -C ../.. archive FETCH_HEAD blender/train_pov7/frames 2>/dev/null | tar -x -C /tmp/claude-0/ 2>/dev/null && \
    cp -n /tmp/claude-0/blender/train_pov7/frames/f_*.png frames/ 2>/dev/null
done
N=$(../cast/vendor/venv/bin/python -c "import sys; sys.path.insert(0,'.'); from captions import END; print(int(END*24))")
MISS=$(for f in $(seq 1 2 $N); do [ -s frames/f_$(printf %04d $f).png ] || echo $f; done)
echo "missing: $(echo $MISS | wc -w)"
if [ "$1" = render ] && [ -n "$MISS" ]; then
  for f in $(echo $MISS | tr ' ' '\n' | sort -rn | head -6); do
    ../cast/vendor/venv/bin/python render.py $f-$f >> /tmp/claude-0/w7_render.log 2>&1
  done
fi
