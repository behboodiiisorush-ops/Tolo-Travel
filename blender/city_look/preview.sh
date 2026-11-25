#!/bin/bash
# render the 14 s look preview (restarts if EEVEE crashes), then encode test/preview.mp4
cd "$(dirname "$0")"
for i in $(seq 1 30); do
  [ $(ls test/p_*.png 2>/dev/null | wc -l) -ge 336 ] && break
  find test -name 'p_*.png' -size 0 -delete
  ../cast/bpy.sh look_test.py --frames 1-336 >> /tmp/claude-0/look_preview.log 2>&1
done
ffmpeg -v error -y -framerate 24 -i test/p_%04d.png -vf "scale=1080:1920:flags=lanczos" -c:v libx264 -crf 18 -pix_fmt yuv420p look_preview.mp4
echo PREVIEW_DONE >> /tmp/claude-0/look_preview.log
