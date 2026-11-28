"""Put the recorded lines on the timeline (story order, short gaps, pauses for the action) -> times.py."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402
GAP, TITLE, TAIL = 0.35, 2.0, 3.5
EXTRA = {"n1": TITLE + 0.3,
         "n2": 3.2,      # horn, the floodlight blazes, the beast screams and runs into the trees
         "me1": 0.2,
         "n3": 2.6,      # the car rolls up and stops; two figures in white get out
         "str1a": 1.8,   # they walk up to the bus door, the door folds open
         "mom1": 0.4, "resc3": 0.3, "old2": 0.4,
         "n4": 1.6,      # they walk back to their car
         "str2b": 0.5, "n5": 0.8,
         "mom2": 1.2,    # Lena's seat is empty
         "me5": 0.1, "str1e": 0.4, "n7": 0.8}


def dur(k):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 os.path.join(HERE, "voices", "clips", k + ".wav")], capture_output=True, text=True).stdout)


t, times = 0.0, {}
for k, who, _ in LINES:
    s = t + (GAP if times else 0) + EXTRA.get(k, 0)
    times[k] = (round(s, 2), round(s + dur(k), 2))
    t = times[k][1]
with open(os.path.join(HERE, "times.py"), "w") as f:
    f.write("# written by layout.py\nTIMES = {\n" + "".join(f"    {k!r}: {v},\n" for k, v in times.items()) +
            f"}}\nTAIL = {TAIL}\nTITLE = {TITLE}\n")
print("end", round(t, 2))
