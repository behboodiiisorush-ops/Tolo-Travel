"""
Place every voice clip at its line's start time and mix it over the sound effects.

    python3 mix_voices.py   # voices/clips/*.wav + out/sfx.wav + out/last_wagon2_full.mp4
                            #   -> out/voices.wav, out/last_wagon2_voiced.mp4

Clips are listed in voices/clips.txt (start, end, speaker, file).  A clip never
starts before the previous one has finished, so lines don't talk over each other.
"""

import os
import subprocess
import wave

import numpy as np

from voice_fx import PRESETS

# which colouring each speaker gets (recorded voices are re-used for several characters)
FX = {"Lena": "lena", "Grandma": "grandma", "Mom": "mom", "Mom phone": "mom_phone", "Radio": "radio"}

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = 71.0


def read_wav(path):
    with wave.open(path) as w:
        assert w.getframerate() == SR
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(axis=1)


def main():
    rows = [line.rstrip("\n").split("\t") for line in open(os.path.join(HERE, "voices", "clips.txt"), encoding="utf-8")]
    track = np.zeros(int(SR * DUR), dtype=np.float32)
    prev_end = 0.0
    tmp = os.path.join(HERE, "voices", "fitted")
    os.makedirs(tmp, exist_ok=True)
    for a, b, who, name in rows:
        src = os.path.join(HERE, "voices", "clips", name)
        if who in FX:
            col = os.path.join(tmp, "fx_" + name)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af", PRESETS[FX[who]],
                            "-ar", str(SR), col], check=True)
            src = col
        dur = len(read_wav(src)) / SR
        window = float(b) - float(a) + 0.35
        tempo = min(1.3, max(1.0, dur / window))  # gently speed up lines that run long
        dst = os.path.join(tmp, name)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af",
                        f"rubberband=tempo={tempo:.3f}:formant=preserved", "-ar", str(SR), dst], check=True)
        x = read_wav(dst)
        x = x / max(1e-6, np.abs(x).max()) * 0.9
        t = max(float(a), prev_end + 0.05)
        i = int(t * SR)
        n = min(len(x), len(track) - i)
        track[i:i + n] += x[:n]
        prev_end = t + len(x) / SR
        if t - float(a) > 0.3:
            print(f"note: {name} starts {t - float(a):.1f}s late (previous line ran long)")
    out_voice = os.path.join(HERE, "out", "voices.wav")
    with wave.open(out_voice, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes())
    # voices up front, effects ducked a little underneath
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(HERE, "out", "last_wagon2_full.mp4"),
        "-i", os.path.join(HERE, "out", "sfx.wav"), "-i", out_voice,
        "-filter_complex",
        "[1:a]volume=0.55[fx];[2:a]aformat=channel_layouts=stereo,volume=1.0[vo];"
        "[fx][vo]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        os.path.join(HERE, "out", "last_wagon2_voiced.mp4")], check=True)
    print(os.path.join(HERE, "out", "last_wagon2_voiced.mp4"))


if __name__ == "__main__":
    main()
