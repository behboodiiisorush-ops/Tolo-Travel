#!/bin/bash
# Render both shorts one after the other (never two Blenders at once), restarting a crashed render.
cd "$(dirname "$0")"
for ep in Episode_01 Episode_02; do
  for try in 1 2 3 4 5; do
    ../../cast/bpy.sh render_short.py $ep "$@" > /tmp/render_$ep.log 2>&1 && break
    echo "retry $ep $try"
  done
done
echo ALL DONE
