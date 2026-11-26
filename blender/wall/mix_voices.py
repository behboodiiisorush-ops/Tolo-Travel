"""Put the user's voice clips (voices/clips/<line>.wav, cut from their ElevenLabs export) on «دیوار».

    python3 mix_voices.py   # voices/clips + out/wall_sfx.wav + out/wall_captions.mp4
                            #   -> out/wall_voices.wav, out/wall_voiced.mp4

Each clip starts at its caption's start; a line that runs long is gently sped up (max 1.3x, formant kept,
no pitch change) and never starts before the previous one has finished.
"""
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import END, LINES  # noqa: E402

SR = 48000
CARD = 4.0
DUR = END + CARD
# clip name per caption line, in LINES order
CLIPS = ["mom1", "mom2", "kazemi", "mom3", "arian", "mahsa", "rezaei", "anchor", "kian"]
FX = {"anchor": "highpass=f=300,lowpass=f=4200,aecho=0.8:0.3:25:0.2,volume=1.2",   # through the TV
      "rezaei": "aecho=0.8:0.35:45:0.18"}
ROOM = "aecho=0.8:0.4:40:0.15"


def read_wav(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(axis=1)


def main():
    track = np.zeros(int(SR * DUR), dtype=np.float32)
    tmp = os.path.join(HERE, "voices", "fitted")
    os.makedirs(tmp, exist_ok=True)
    prev_end = 0.0
    for (a, b, who, _), name in zip(LINES, CLIPS):
        src = os.path.join(HERE, "voices", "clips", name + ".wav")
        dur = len(read_wav(src)) / 44100
        tempo = min(1.3, max(1.0, dur / (b - a + 0.35)))
        dst = os.path.join(tmp, name + ".wav")
        af = f"{FX.get(who, ROOM)},rubberband=tempo={tempo:.3f}:formant=preserved"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af", af, "-ar", str(SR), "-ac", "1", dst],
                       check=True)
        x = read_wav(dst)
        x = x / max(1e-6, np.abs(x).max()) * 0.9
        t = max(a, prev_end + 0.05)
        i = int(t * SR)
        n = min(len(x), len(track) - i)
        track[i:i + n] += x[:n]
        prev_end = t + len(x) / SR
        print(f"{name:7s} {t:6.2f}-{prev_end:6.2f}  caption {a}-{b}  tempo {tempo:.2f}")
    out_voice = os.path.join(HERE, "out", "wall_voices.wav")
    with wave.open(out_voice, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes())
    out = os.path.join(HERE, "out", "wall_voiced.mp4")
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(HERE, "out", "wall_captions.mp4"),
        "-i", os.path.join(HERE, "out", "wall_sfx.wav"), "-i", out_voice,
        "-filter_complex",
        "[1:a]aformat=channel_layouts=stereo,volume=0.55[fx];[2:a]aformat=channel_layouts=stereo[vo];"
        "[fx][vo]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
