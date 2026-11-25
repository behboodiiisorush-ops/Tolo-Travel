#!/usr/bin/env bash
# This machine's share of the frames; helper sessions render 341-1714.
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python
"$PY" part4.py --render --range 1 169 > render_a.log 2>&1 &
"$PY" part4.py --render --range 171 339 > render_b.log 2>&1 &
wait
echo LOCAL_DONE
