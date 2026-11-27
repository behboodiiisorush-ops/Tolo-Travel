"""ElevenLabs takes el/<key>.mp3 -> voices/clips/<key>.wav (silence trimmed, 48 kHz mono, the character's colour:
Lena pitched up to a girl, the rescuer's first two lines through the bus loudspeaker outside, the radio voice
through the walkie-talkie).  Then run layout.py to put the lines on the timeline."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402
from el_lines import VOICES  # noqa: E402
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
SPEAKER = "highpass=f=220,lowpass=f=6000,aecho=0.8:0.35:80:0.18"          # light loudspeaker outside
RADIO = "highpass=f=280,lowpass=f=4800,acrusher=bits=14:mix=0.06"          # light walkie-talkie colour
EXTRA = {"resc1": SPEAKER, "resc2": SPEAKER, "radio1": RADIO, "radio2": RADIO}
SRC = os.path.join(HERE, "el2")   # eleven_multilingual_v2 takes (el_v3/ keeps the old v3 takes)
os.makedirs(os.path.join(HERE, "voices", "clips"), exist_ok=True)
for key, who, _ in LINES:
    af = [TRIM]
    if VOICES[who][2]:
        af.append(VOICES[who][2])
    if key in EXTRA:
        af.append(EXTRA[key])
    af.append("loudnorm=I=-16:TP=-1.5:LRA=11")
    af.append("afade=t=in:d=0.02,areverse,afade=t=in:d=0.05,areverse")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(SRC, key + ".mp3"), "-af", ",".join(af),
                    "-ar", "48000", "-ac", "1", os.path.join(HERE, "voices", "clips", key + ".wav")], check=True)
print("clips ready")
