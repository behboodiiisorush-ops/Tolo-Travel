#!/usr/bin/env bash
cd "$(dirname "$0")"
PY=../cast/vendor/venv/bin/python
"$PY" part_wagon.py --render --range 1 648
"$PY" part_wagon.py --render --range 1345 1584
echo WAGON_DONE
