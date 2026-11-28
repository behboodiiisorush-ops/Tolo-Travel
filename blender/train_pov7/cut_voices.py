"""Cut the user's single ElevenLabs recording (voices/recording_sara_all.mp3, all 26 lines in RECORDED order)
into voices/clips/<key>.wav, and give each character its own colour (the whole file is one voice, Sara):
  Mom   - as recorded, light walkie-talkie band (she speaks over the radio)
  Lena  - +2 semitones, formants kept (a little girl)
  Me    - -2 semitones (a boy)
  Rahim - -4 semitones, formants lowered (a grown man)
every line loudness-matched (loudnorm I=-16)."""
import os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402

SRC = os.path.join(HERE, "voices", "recording_sara_all.mp3")
# line starts (s) in the recording, from faster-whisper word timestamps; boundaries snapped to the quietest spot
STARTS = {"mom1": 0.0, "mom2": 3.22, "mom3": 6.94, "lena1": 8.94, "lena2": 10.94, "lena3": 13.26, "lena4": 16.16,
          "lena5": 19.2, "lena6": 21.4, "lena7": 24.32, "lena8": 26.48, "lena9": 29.0, "n1": 31.06, "n2": 34.56,
          "n3": 37.16, "n4": 40.14, "n5": 43.28, "n6": 46.84, "n7": 49.22, "n8": 51.34, "n9": 55.02,
          "rahim1": 57.9, "rahim2": 60.32, "rahim3": 64.0, "rahim4": 67.02, "rahim5": 70.7}
NOSNAP = {"rahim3"}  # its start sits in a long pause; snapping would cut into «باشه»
WHO = {k: w for k, w, _ in LINES}
FX = {"Mom": "highpass=f=250,lowpass=f=4200",
      "Lena": "rubberband=pitch=1.122:formant=preserved",
      "Me": "rubberband=pitch=0.891",
      "Rahim": "rubberband=pitch=0.794,lowpass=f=6000"}
SR = 48000


def load():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def snap(x, t, w=0.25):
    """move t to the quietest 20 ms inside t±w"""
    a, b = int(max(0, t - w) * SR), int(min(len(x) / SR, t + w) * SR)
    if b - a < 2000:
        return t
    e = np.convolve(np.abs(x[a:b]), np.ones(960) / 960, "same")
    return (a + int(np.argmin(e))) / SR


if __name__ == "__main__":
    x = load()
    keys = sorted(STARTS, key=STARTS.get)
    cuts = [snap(x, STARTS[k]) if STARTS[k] > 0 and k not in NOSNAP else STARTS[k] for k in keys] + [len(x) / SR]
    os.makedirs(os.path.join(HERE, "voices", "clips"), exist_ok=True)
    for i, k in enumerate(keys):
        a, b = cuts[i], cuts[i + 1]
        out = os.path.join(HERE, "voices", "clips", k + ".wav")
        flt = ("silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
               "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
               f"{FX[WHO[k]]},loudnorm=I=-16:TP=-1.5")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", SRC, "-af", flt,
                        "-ar", str(SR), "-ac", "1", out], check=True)
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                                 capture_output=True, text=True).stdout)
        print(f"{k:7s} {a:6.2f}-{b:6.2f}  {d:5.2f}s")
