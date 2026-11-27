#!/bin/bash
# re-render only the dialogue frames (voice-driven lips), then sound + post
cd "$(dirname "$0")"
B=../../../cast/bpy.sh
for i in $(seq 1 20); do
  [ $(ls frames | wc -l) -ge 744 ] && break
  $B render.py -- --still $(cat relips.txt) --out frames >> render_lips.log 2>&1
done
python3 audio.py >> chain.log 2>&1 && python3 post.py >> chain.log 2>&1 && echo "[chain_lips] DONE" >> chain.log
