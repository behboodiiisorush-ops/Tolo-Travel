"""ElevenLabs takes el/<key>.mp3 -> voices/clips/<key>.wav (silence trimmed, 48 kHz mono, the character's colour:
Lena pitched up to a girl, the rescuer's first two lines through the bus loudspeaker outside, the radio voice
through the walkie-talkie).  Then run layout.py to put the lines on the timeline."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402
from el_lines import VOICES  # noqa: E402
from voice_fx import PRESETS  # noqa: E402
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
EXTRA = {"resc1": "highpass=f=300,lowpass=f=4000,acrusher=bits=12:mix=0.15,aecho=0.8:0.5:90|200:0.3|0.2",
         "resc2": "highpass=f=300,lowpass=f=4000,acrusher=bits=12:mix=0.15,aecho=0.8:0.5:90|200:0.3|0.2",
         "radio1": PRESETS["radio"], "radio2": PRESETS["radio"]}
os.makedirs(os.path.join(HERE, "voices", "clips"), exist_ok=True)
for key, who, _ in LINES:
    af = [TRIM]
    if VOICES[who][2]:
        af.append(VOICES[who][2])
    if key in EXTRA:
        af.append(EXTRA[key])
    af.append("afade=t=in:d=0.02,areverse,afade=t=in:d=0.05,areverse")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(HERE, "el", key + ".mp3"), "-af", ",".join(af),
                    "-ar", "48000", "-ac", "1", os.path.join(HERE, "voices", "clips", key + ".wav")], check=True)
print("clips ready")
