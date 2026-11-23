#!/bin/bash
# After run_all.sh: re-render the house part (banner fix), rebuild the final videos, commit and push.
cd "$(dirname "$0")"
while pgrep -f run_all.sh >/dev/null; do sleep 60; done
rm -f frames/f_00{01..99}.png frames/f_01??.png frames/f_02[0-5]?.png frames/f_026[0-4].png
../cast/bpy.sh scene.py --part house --render
ffmpeg -v error -y -framerate 24 -start_number 1 -i frames/f_%04d.png -frames:v 264 \
  -vf scale=1080:1920:flags=lanczos -c:v libx264 -crf 20 -pix_fmt yuv420p out/parts/house.mp4
python3 post.py
cd ..
git add last_bell_real/out
git commit -q -m "Realistic last bell: final film (captions, clean, with sfx)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0195jcA7K3GmXATgzLTbYzbF"
for i in 1 2 3 4; do git push -q -u origin claude/stick-figure-jo3vsw && break; sleep $((i * 10)); done
echo FINISHED $(date +%T)
