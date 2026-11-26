#!/bin/bash
# Render a range of «سال ۱۵۰۰» frames in a cloud session and push them back in batches.
#   bash bundle/worker.sh 841-1135 <branch>
set -u
cd "$(dirname "$0")"
R=$1; BR=$2
A=${R%-*}; B=${R#*-}
[ -s year1500.blend ] || cat year1500.blend.part* > year1500.blend
[ -x venv/bin/python ] || { python3 -m venv venv && venv/bin/pip install -q bpy==5.3.0 numpy; }
mkdir -p frames
git checkout -B "$BR" >/dev/null 2>&1
need() { python3 - "$A" "$B" <<'PY'
import os, sys
from captions import FLASHBACK as F, WAKE as W
a, b = int(sys.argv[1]), int(sys.argv[2])
print(sum(1 for f in range(a, b + 1) if not (F[1]*24 < f <= W*24) and not (os.path.exists(f"frames/f_{f:04d}.png") and os.path.getsize(f"frames/f_{f:04d}.png") > 0)))
PY
}
push() { git add frames >/dev/null 2>&1; git commit -qm "frames $R" >/dev/null 2>&1; for i in 1 2 3 4; do git push -q -u origin "$BR" && break; sleep $((2**i)); done; }
for i in $(seq 1 200); do
  [ "$(need)" = "0" ] && break
  find frames -size 0 -delete 2>/dev/null
  # render in chunks of 20 frames, push after each chunk
  for s in $(seq $A 20 $B); do
    e=$((s + 19)); [ $e -gt $B ] && e=$B
    venv/bin/python render.py $s-$e >> render.log 2>&1
    push
  done
done
push
echo "WORKER_DONE $R"
