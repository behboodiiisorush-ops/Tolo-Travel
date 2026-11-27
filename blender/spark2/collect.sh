#!/bin/bash
# Pull helper chunks (branches claude/spark2-chunk-*), unpack them into frames/, then render whatever is still
# missing from the start of the film (backup if a helper failed).   ./collect.sh [render]
cd "$(dirname "$0")"
ROOT=$(git rev-parse --show-toplevel)
for br in $(git -C "$ROOT" ls-remote --heads origin 'claude/spark2-chunk-*' | awk '{print $2}' | sed 's|refs/heads/||'); do
  git -C "$ROOT" fetch -q origin "$br" || continue
  d=$(mktemp -d); git -C "$ROOT" archive FETCH_HEAD blender/spark2/chunks | tar -x -C "$d"
  for c in "$d"/blender/spark2/chunks/chunk_*.mp4; do
    [ -f "$c" ] || continue
    a=$(basename "$c" .mp4 | cut -d_ -f2); a=$((10#$a))
    t=$(mktemp -d); ffmpeg -v error -i "$c" -start_number $a "$t/f_%04d.png"
    cp --update=none "$t"/*.png frames/ 2>/dev/null; rm -rf "$t"
  done; rm -rf "$d"
done
miss=$(for f in $(seq 1 1152); do [ -f frames/f_$(printf %04d $f).png ] || echo $f; done)
echo "missing: $(echo "$miss" | grep -c .)"
if [ "$1" = render ] && [ -n "$miss" ]; then
  a=$(echo "$miss" | head -1); b=$a
  for f in $(echo "$miss" | head -6); do [ $f -le $((a + 5)) ] && b=$f; done
  SAMPLES=${SAMPLES:-16} ../cast/bpy.sh render.py $a $b >> /tmp/claude-0/spark2_fill.log 2>&1
fi
