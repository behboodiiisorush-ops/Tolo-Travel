#!/usr/bin/env bash
# This machine's share of the frames; helper sessions render the rest.
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python
python3 make_textures.py
"$PY" shelter1.py --render --range 1 191 > render_a.log 2>&1 &
"$PY" shelter1.py --render --range 193 385 > render_b.log 2>&1 &
wait
echo LOCAL_DONE
