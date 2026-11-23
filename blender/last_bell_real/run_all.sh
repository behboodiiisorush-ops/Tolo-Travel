#!/bin/bash
# Render all four parts (skips frames already on disk), save each part as an mp4 and push it,
# then build the final film with post.py.
cd "$(dirname "$0")"
B=../cast/bpy.sh
declare -A R=([house]="1 264" [street]="265 360" [class]="361 1512" [roof]="1513 1800")
mkdir -p out/parts
for part in house street class roof; do
  $B scene.py --part $part --render
  set -- ${R[$part]}
  ffmpeg -v error -y -framerate 24 -start_number $1 -i frames/f_%04d.png -frames:v $(( $2 - $1 + 1 )) \
    -vf scale=1080:1920:flags=lanczos -c:v libx264 -crf 20 -pix_fmt yuv420p out/parts/$part.mp4
  (cd .. && git add last_bell_real/out/parts/$part.mp4 && \
   git commit -q -m "Render realistic last bell: $part part

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0195jcA7K3GmXATgzLTbYzbF" && \
   for i in 1 2 3 4; do git push -q -u origin claude/stick-figure-jo3vsw && break; sleep $((i * 10)); done)
  echo "PART DONE $part $(date +%T)"
done
python3 post.py
echo ALL DONE
