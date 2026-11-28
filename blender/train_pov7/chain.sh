#!/bin/bash
# build the scene once, then render frames A..B (default all, odd frames only); restarts the renderer if it crashes
# usage: ./chain.sh [A B]
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python
N=$($PY -c "import sys; sys.path.insert(0,'.'); from captions import END; print(int(END*24))")
A=${1:-1}; B=${2:-$N}
[ -f train_bridge7.blend ] || $PY part7.py --save > /tmp/claude-0/w7_build.log 2>&1
missing() { local m=0; for f in $(seq $A $B); do [ $((f % 2)) -eq 1 ] || continue; [ -s frames/f_$(printf %04d $f).png ] || m=$((m+1)); done; echo $m; }
mkdir -p frames
for i in $(seq 1 300); do
  [ "$(missing)" -eq 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  $PY render.py $A-$B >> /tmp/claude-0/w7_render.log 2>&1
done
echo CHAIN_DONE >> /tmp/claude-0/w7_render.log
