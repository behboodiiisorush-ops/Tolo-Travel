#!/usr/bin/env bash
# This machine's share of the frames; helper sessions render the rest.
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python

"$PY" shelter2.py --render --range 1 79 > render_a.log 2>&1 &
"$PY" shelter2.py --render --range 81 161 > render_b.log 2>&1 &
wait
echo LOCAL_DONE
