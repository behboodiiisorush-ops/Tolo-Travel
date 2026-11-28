#!/bin/bash
# Render helper for «واگن آخر ۷» on a fresh cloud machine.
# usage: blender/train_pov7/worker.sh A B   (renders odd frames A..B into frames/, restarting on crashes)
cd "$(dirname "$0")"
V=../cast/vendor/venv
if [ ! -x $V/bin/python ] || ! $V/bin/python -c "import bpy" 2>/dev/null; then
  python3 -m venv $V && $V/bin/pip install -q bpy==5.3.0 numpy
fi
./chain.sh "$1" "$2"
echo WORKER_DONE
