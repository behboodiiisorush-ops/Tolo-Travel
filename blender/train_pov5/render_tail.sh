#!/usr/bin/env bash
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python
"$PY" part5.py --render --range 1647 1765 > render_c.log 2>&1 &
"$PY" part5.py --render --range 1247 1367 > render_d.log 2>&1 &
wait
echo TAIL_DONE
