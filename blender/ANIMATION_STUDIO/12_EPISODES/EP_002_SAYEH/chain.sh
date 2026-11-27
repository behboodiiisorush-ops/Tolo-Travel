#!/bin/bash
# Renders every frame of EP_002 (resumable: restarts Blender until all frames exist), then sound + post.
cd "$(dirname "$0")"
B=../../../cast/bpy.sh
N=$(python3 -c "import sys;sys.path.insert(0,'.');from lines import fr,END;print(fr(END)-1)")
for try in $(seq 1 40); do
  have=$(ls frames 2>/dev/null | grep -c '^f_.*png$')
  [ "$have" -ge "$N" ] && break
  echo "[chain] try $try, $have/$N frames" >> chain.log
  $B render.py >> render.log 2>&1
done
python3 sound.py >> chain.log 2>&1
python3 post.py >> chain.log 2>&1 && echo "[chain] DONE" >> chain.log
