#!/bin/bash
# Helper: render frames A..B and encode them into one near-lossless mp4 chunk (out/chunk_A_B.mp4).
#   ./chunk.sh 145 288
cd "$(dirname "$0")"
A=$1; B=$2
./chain.sh $A $B
mkdir -p chunks
ffmpeg -v error -y -framerate 24 -start_number $A -i frames/f_%04d.png -frames:v $((B - A + 1)) \
  -c:v libx264 -crf 10 -preset slow -pix_fmt yuv444p chunks/chunk_$(printf %04d $A)_$(printf %04d $B).mp4
echo CHUNK_DONE >> /tmp/claude-0/spark2_render_$A.log
