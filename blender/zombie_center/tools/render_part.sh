#!/bin/bash
# Worker-chat render of one frame range of a Zombie Center scene script.
# usage: render_part.sh <scene.py relative to repo> <mode: preview|final> <A> <B> <outdir relative to repo>
# Renders frames A..B (preview = every 2nd frame) and restarts Blender if it crashes, until every frame exists.
set -u
cd "$(dirname "$0")/../../.."          # repo root
S=$1; MODE=$2; A=$3; B=$4; OUT=$5
STEP=1; [ "$MODE" = preview ] && STEP=2
PREFIX=prev_; [ "$MODE" = final ] && PREFIX=f_
bash blender/cast/setup.sh > /tmp/zc_setup.log 2>&1 || { echo "SETUP FAILED"; tail -20 /tmp/zc_setup.log; exit 1; }
missing() { local m=0; for f in $(seq $A $STEP $B); do [ -s "$OUT/${PREFIX}$(printf %04d $f).png" ] || m=$((m+1)); done; echo $m; }
for i in $(seq 1 50); do
  [ "$(missing)" -eq 0 ] && break
  find "$OUT" -name "${PREFIX}*.png" -size 0 -delete 2>/dev/null
  # resume after the last finished frame
  S0=$A; for f in $(seq $A $STEP $B); do [ -s "$OUT/${PREFIX}$(printf %04d $f).png" ] || { S0=$f; break; }; done
  PREV_START=$S0 PREV_END=$B blender/cast/bpy.sh "$S" "$MODE" >> /tmp/zc_render.log 2>&1
done
echo "missing: $(missing)"
