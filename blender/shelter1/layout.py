"""Lay the recorded lines out on the timeline (one after another, short gaps, story pauses)
and write times.py, which captions.py reads.  Run after cut_voices.py."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402

TEMPO = 1.1          # mix_voices.py speeds lines up by at most this much to fit
GAP = 0.25
EXTRA = {"n1": 0.6,       # the alarm first, then the voice
         "mom1": 0.5, "lena1": 0.2, "me1": 0.2,
         "mom2": 1.6,     # we run out of the house: the street
         "me2": 0.3, "lena2": 1.0,
         "guard1": 2.0,   # running into the park, the bunker door
         "me3": 0.2, "jalal1": 0.4, "guard2": 0.3,
         "n2": 0.8,       # the door is shut
         "lena3": 4.5,    # the flash, the shaking, silence, the dark (FLASH_AFTER + ~4 s)
         "radio1": 1.2,
         "n3": 2.6}       # three knocks on the door


def dur(name, text=""):
    path = os.path.join(HERE, "voices", "clips", name)
    if not os.path.exists(path):  # no recording yet: estimate from the text (≈ episode 3's pace)
        return 0.09 * len(text.replace("\n", "")) + 1.0
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          os.path.join(HERE, "voices", "clips", name)], capture_output=True, text=True).stdout
    return float(out) / TEMPO


t, times = 0.0, {}
for key, who, text in LINES:
    s = t + (GAP if times else 0) + EXTRA.get(key, 0)
    e = s + dur(f"{key}.wav", text)
    times[key] = (round(s, 2), round(e, 2))
    t = e
with open(os.path.join(HERE, "times.py"), "w") as f:
    f.write("# written by layout.py from the recorded voices\nTIMES = {\n")
    for k, (s, e) in times.items():
        f.write(f"    {k!r}: ({s}, {e}),\n")
    f.write("}\n")
os.makedirs(os.path.join(HERE, "voices"), exist_ok=True)
with open(os.path.join(HERE, "voices", "clips.txt"), "w") as f:
    for key, who, text in LINES:
        f.write(f"{times[key][0]}\t{times[key][1]}\t{who}\t{key}.wav\n")
for k, v in times.items():
    print(k, v)
