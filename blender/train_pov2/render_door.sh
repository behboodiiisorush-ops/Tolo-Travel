#!/usr/bin/env bash
# Two processes share the frames (each renders every 2nd frame of its half; frame_step=2).
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python
"$PY" part_door.py --render --range 1 623 > render_a.log 2>&1 &
"$PY" part_door.py --render --range 625 1248 > render_b.log 2>&1 &
wait
echo DOOR_DONE
