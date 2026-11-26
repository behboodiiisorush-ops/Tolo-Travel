"""Lay the recorded lines out on the timeline (one after another, short gaps, story pauses) and write
times.py, which captions.py reads.  Run after cut_voices.py (before that it estimates from the text)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402

TEMPO = 1.05
GAP = 0.35
TITLE = 2.6           # «یک هفته بعد...» on black first
EXTRA = {"n1": TITLE + 0.6,
         "resc1": 1.6,    # a loudspeaker crackle outside; everyone looks up
         "resc2": 1.2,    # outside: the bus in the fog
         "me2": 0.4,
         "n3": 3.0,       # the door grinds open, grey daylight
         "resc3": 0.6,
         "old1": 3.2,     # they walk to the bus and get on
         "resc4": 0.4,
         "n4": 3.4,       # the bus pulls away; the city
         "mom3": 0.8, "old2": 1.2, "mom4": 0.3,
         "radio1": 3.0,   # dusk; the radio crackles
         "resc5": 0.5,
         "n5": 3.4,       # into the forest
         "lena5": 1.2, "old3": 0.4,
         "resc6": 2.0,    # the dogs burst out of the trees
         "me5": 0.8,
         "resc7": 1.6,    # bang: a tyre bursts
         "mom5": 0.2,
         "n6": 2.0,       # the bus grinds to a halt
         "radio2": 2.2,   # claws, silence
         "me6": 0.4,
         "n7": 1.0}
TAIL = 3.0            # the far headlights hold before the question card


def dur(name, text=""):
    path = os.path.join(HERE, "voices", "clips", name)
    if not os.path.exists(path):  # no recording yet: estimate from the text
        return 0.085 * len(text.replace("\n", "")) + 0.9
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout
    return float(out) / TEMPO


t, times = 0.0, {}
for key, who, text in LINES:
    s = t + (GAP if times else 0) + EXTRA.get(key, 0)
    e = s + dur(f"{key}.wav", text)
    times[key] = (round(s, 2), round(e, 2))
    t = e
with open(os.path.join(HERE, "times.py"), "w") as f:
    f.write("# written by layout.py\nTIMES = {\n")
    for k, (s, e) in times.items():
        f.write(f"    {k!r}: ({s}, {e}),\n")
    f.write(f"}}\nTAIL = {TAIL}\nTITLE = {TITLE}\n")
os.makedirs(os.path.join(HERE, "voices"), exist_ok=True)
with open(os.path.join(HERE, "voices", "clips.txt"), "w") as f:
    for key, who, text in LINES:
        f.write(f"{times[key][0]}\t{times[key][1]}\t{who}\t{key}.wav\n")
print("end", round(t, 1))
