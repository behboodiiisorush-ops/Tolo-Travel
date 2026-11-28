"""Lay the cut lines (voices/clips/<key>.wav) out on the timeline -> times.py.  EXTRA = seconds of action before a line."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402

GAP = 0.35
EXTRA = {"mom1": 2.0,     # by the locomotive at the broken bridge; the radio crackles
         "lena1": 0.3,
         "n1": 3.2,       # the helicopter comes down on the far bank
         "mom3": 1.6,     # its door slides open (heard over the radio)
         "lena2": 1.4,    # the radio breaks up and dies; the searchlight swings and goes out
         "rahim1": 0.4,
         "lena4": 2.2,    # the rotor winds down; silence; Lena on the step
         "lena5": 3.6,    # three knocks on the radio
         "rahim2": 1.6,   # at the edge of the bridge
         "rahim4": 0.6,   # the rope round our waists
         "lena7": 0.3, "rahim5": 0.3,
         "n6": 2.4,       # out on the two rails
         "lena8": 2.0,    # a plank cracks and falls into the river
         "lena9": 3.4,    # the train horn behind us; a shadow rises by the helicopter
         "n8": 0.6, "n9": 0.3}


def dur(key):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          os.path.join(HERE, "voices", "clips", key + ".wav")], capture_output=True, text=True).stdout
    return float(out)


if __name__ == "__main__":
    t, times = 0.0, {}
    for key, who, text in LINES:
        s = t + (GAP if times else 0) + EXTRA.get(key, 0)
        e = s + dur(key)
        times[key] = (round(s, 2), round(e, 2))
        t = e
    with open(os.path.join(HERE, "times.py"), "w") as f:
        f.write("# written by layout.py from voices/clips\nTIMES = {\n")
        for k, (s, e) in times.items():
            f.write(f"    {k!r}: ({s}, {e}),\n")
        f.write("}\n")
    for k, v in times.items():
        print(k, v)
