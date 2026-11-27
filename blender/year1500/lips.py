"""Lip sync of «سال ۱۵۰۰» from the real ElevenLabs takes (voices/*.mp3), placed and sped up exactly as voices.py
mixes them, via the shared blender/cast/lipsync.py.   import lips; lips.LS.level("kian", t)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cast"))
import lipsync  # noqa: E402
import voices as VO  # noqa: E402

LS = lipsync.Voices(fps=24)
for name, start, latest, fx in VO.TAKES:
    who = name.split("_", 1)[1]
    if who not in ("me", "kian", "mom"):
        continue
    src = os.path.join(VO.V, name + ".mp3")
    d = len(lipsync._decode(src)) / lipsync.SR
    tempo = max(1.0, d / (latest - start))
    LS.add(who, src, start, af=f"atempo={tempo:.3f}" if tempo > 1.0 else None)


def level(who, t):
    return LS.level(who, t)
