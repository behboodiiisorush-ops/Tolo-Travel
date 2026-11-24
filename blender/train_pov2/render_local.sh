#!/usr/bin/env bash
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python
"$PY" part_door.py --render --range 1 449 > render_a.log 2>&1 &
"$PY" part_door.py --render --range 721 1169 > render_b.log 2>&1 &
wait
echo LOCAL_DONE
