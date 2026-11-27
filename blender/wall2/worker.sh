#!/bin/bash
# One render worker for «دیوار ۲»: ./worker.sh K A B
#   sets up Blender + the cast (if needed), builds wall2.blend, renders frames A..B, encodes them as
#   out/part_KK.mp4 (frame A first) and pushes ONLY that mp4 to the branch claude/wall2-part-KK.
set -e
cd "$(dirname "$0")"
K=$(printf %02d $1); A=$2; B=$3
[ -x ../cast/vendor/venv/bin/python ] || bash ../cast/setup.sh
LOG=/tmp/wall2_render_$K.log ./chain.sh $A $B
n=$(for f in $(seq $A $B); do [ -s frames/f_$(printf %04d $f).png ] && echo x; done | wc -l)
[ "$n" -eq $((B - A + 1)) ] || { echo "MISSING FRAMES: $n of $((B - A + 1))"; exit 1; }
mkdir -p out
ffmpeg -v error -y -framerate 24 -start_number $A -i frames/f_%04d.png -frames:v $((B - A + 1)) \
  -c:v libx264 -crf 12 -pix_fmt yuv420p out/part_$K.mp4
echo "PART_DONE out/part_$K.mp4 frames $A-$B"
