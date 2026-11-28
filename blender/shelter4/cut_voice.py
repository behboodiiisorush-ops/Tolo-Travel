"""The user's take -> voices/clips/<key>.wav: cut, trimmed, loudness-matched, with the colour of each voice
(the strangers behind glass visors, their whispers on our walkie-talkie)."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "user_voice"))
from segments import SEG  # noqa: E402
SRC = os.path.join(HERE, "user_voice", "take1.mp3")
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
VISOR = "highpass=f=180,lowpass=f=5200,aecho=0.8:0.5:12|24:0.25|0.15"          # inside a glass helmet
RADIO = "highpass=f=280,lowpass=f=4800,acrusher=bits=14:mix=0.06"               # light walkie-talkie colour
FX = {"str1a": VISOR, "str1b": VISOR, "str1c": "highpass=f=180,lowpass=f=6000", "str1e": VISOR, "str2a": VISOR,
      "str2b": RADIO, "str1d": RADIO}
out = os.path.join(HERE, "voices", "clips")
os.makedirs(out, exist_ok=True)
for k, a, b in SEG:
    af = [TRIM] + ([FX[k]] if k in FX else []) + ["loudnorm=I=-16:TP=-1.5:LRA=11",
                                                   "afade=t=in:d=0.02,areverse,afade=t=in:d=0.05,areverse"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", SRC, "-af", ",".join(af),
                    "-ar", "48000", "-ac", "1", os.path.join(out, k + ".wav")], check=True)
print("clips ready")
