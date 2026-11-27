"""Lay the ElevenLabs lines (el/<key>.mp3, silence trimmed) out on the timeline -> times.py."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402

GAP = 0.3
EXTRA = {"n1": 1.0,       # the helicopter beside the train
         "rahim1": 0.4, "lena1": 0.6, "rahim2": 0.3,
         "n2": 0.8,       # curtains closed, dark car
         "me1": 0.6,
         "lena2": 3.6,    # three blinks of the torch; the searchlight finds us
         "rahim3": 0.8,
         "me2": 4.2,      # the bag comes down on a rope to our window; we pull it in
         "mom1": 1.2,     # static, then her voice
         "lena3": 0.3, "mom2": 0.4,
         "rahim4": 0.5,
         "mom3": 5.5,     # Rahim runs to the front; brakes; we stop at the broken bridge
         "lena4": 1.2,    # the radio dies
         "n3": 1.2}


def dur(key):
    flt = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "el", key + ".mp3"), "-af", flt,
                          "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return len(raw) / 2 / 16000


if __name__ == "__main__":
    t, times = 0.0, {}
    for key, who, text in LINES:
        s = t + (GAP if times else 0) + EXTRA.get(key, 0)
        e = s + dur(key)
        times[key] = (round(s, 2), round(e, 2))
        t = e
    with open(os.path.join(HERE, "times.py"), "w") as f:
        f.write("# written by layout.py from the ElevenLabs clips\nTIMES = {\n")
        for k, (s, e) in times.items():
            f.write(f"    {k!r}: ({s}, {e}),\n")
        f.write("}\n")
    for k, v in times.items():
        print(k, v)
