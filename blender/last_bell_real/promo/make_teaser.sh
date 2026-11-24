#!/bin/bash
# 15 s teaser short from the final voiced film -> promo/teaser_short.mp4
cd "$(dirname "$0")/.."
SRC=out/last_bell_real_voice.mp4
T=promo/tmp; rm -rf $T; mkdir -p $T
i=0
for r in "40.9 44.6" "45.4 47.6" "58.5 60.4" "72.5 74.9"; do
  set -- $r
  ffmpeg -v error -y -ss $1 -to $2 -i $SRC -vf "fps=24,format=yuv420p" -af "aresample=48000" \
    -c:v libx264 -crf 18 -c:a aac -b:a 192k $T/c$i.mp4
  i=$((i+1))
done
# closing card: the 9:16 poster with a low hit
ffmpeg -v error -y -loop 1 -t 2.6 -i promo/teaser_9x16.png -f lavfi -t 2.6 \
  -i "sine=frequency=50:duration=2.6,volume=0.6,afade=t=out:st=0.6:d=2" \
  -vf "fps=24,format=yuv420p,fade=t=in:st=0:d=0.25" -c:v libx264 -crf 18 -c:a aac -b:a 192k -ar 48000 $T/c$i.mp4
ls $T/c*.mp4 | sed "s/^/file '..\/..\//; s/$/'/" > $T/list.txt
sed -i "s|file '../../promo/tmp/|file '|" $T/list.txt
ffmpeg -v error -y -f concat -safe 0 -i $T/list.txt -c:v libx264 -crf 19 -c:a aac -b:a 192k -movflags +faststart promo/teaser_short.mp4
rm -rf $T
echo promo/teaser_short.mp4
