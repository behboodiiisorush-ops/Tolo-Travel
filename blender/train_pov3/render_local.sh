#!/usr/bin/env bash
# This machine's share of the frames; helper sessions render 415-1765 (see the episode notes).
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python
"$PY" part3.py --render --range 1 205 > render_a.log 2>&1 &
"$PY" part3.py --render --range 207 413 > render_b.log 2>&1 &
wait
echo LOCAL_DONE
