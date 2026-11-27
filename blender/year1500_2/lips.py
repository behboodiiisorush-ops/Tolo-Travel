"""Lips of «سال ۱۵۰۰ — قسمت دوم» from the ElevenLabs takes, placed as voices.py places them (shared lipsync.py).
lips.level(who, t) -> 0 silent, else loudness; lips.level("voice", t) drives the shop speaker's light."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
import lipsync  # noqa: E402
from captions import LINES  # noqa: E402

LS = lipsync.Voices(fps=24)
for a, b, who, _, take in LINES:
    src = os.path.join(HERE, "voices", take + ".mp3")
    d = len(lipsync._decode(src)) / lipsync.SR
    tempo = max(1.0, d / (b + 0.3 - a))
    LS.add(who, src, a, af=f"atempo={tempo:.3f}" if tempo > 1.0 else None)


def level(who, t):
    return LS.level(who, t)
