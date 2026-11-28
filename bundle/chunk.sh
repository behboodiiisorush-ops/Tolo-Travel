#!/bin/bash
# Render one chunk of «قانون‌ها ۲» frames in a cloud session and push it as ONE mp4 to its own branch.
#   bash bundle/chunk.sh 141-280        -> branch render-r2-141-280, file chunks/chunk_141-280.mp4
# Safe to run again: frames already on disk are skipped.
set -u
cd "$(dirname "$0")"
R=$1; A=${R%-*}; B=${R#*-}; BR=${2:-render-r2-$R}
[ -s rules_2.blend ] || cat rules_2.blend.part* > rules_2.blend
[ -x venv/bin/python ] || { python3 -m venv venv && venv/bin/pip install -q bpy==5.3.0 numpy imageio-ffmpeg; }
FF=$(command -v ffmpeg || venv/bin/python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
mkdir -p frames ../chunks
for i in $(seq 1 100); do
  left=$(python3 -c "
import os
print(sum(1 for f in range($A, $B + 1) if not (os.path.exists(f'frames/f_{f:04d}.png') and os.path.getsize(f'frames/f_{f:04d}.png') > 0)))")
  echo "$(date +%H:%M) frames left $left" >> render.log
  [ "$left" = 0 ] && break
  find frames -size 0 -delete 2>/dev/null
  venv/bin/python render.py $A-$B >> render.log 2>&1
done
OUT=../chunks/chunk_$R.mp4
"$FF" -v error -y -framerate 24 -start_number $A -i frames/f_%04d.png -frames:v $((B - A + 1)) \
      -c:v libx264 -preset slow -crf 6 -pix_fmt yuv444p "$OUT"
cd ..
git checkout -B "$BR" >/dev/null 2>&1
git add chunks/chunk_$R.mp4
git commit -qm "chunk $R"
for i in 1 2 3 4 5; do git push -q -u origin "$BR" && break; sleep $((2**i)); done
echo "CHUNK_DONE $R $(ls -la chunks/chunk_$R.mp4)"
