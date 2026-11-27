"""Voices: ElevenLabs takes in voices/*.mp3 -> loudness-matched wavs (Arian: gentle pitch up, formants kept),
the phone lines band-passed like a phone speaker, the dialogue track out/dialogue.wav and per-frame mouth
levels out/levels.json (used by scene.py for the lips).   python3 voice.py"""
import json, os, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, END
V = os.path.join(HERE, "voices")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
SR, FPS = 48000, 24


def ff(*a):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *a], check=True)


def read(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def write(p, x):
    x = np.clip(x, -1, 1)
    with wave.open(p, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


track = np.zeros(int((END + 1) * SR), np.float32)
levels = {}
for a, b, who, _, clip in LINES:
    src = os.path.join(V, clip + ".mp3")
    dst = os.path.join(V, clip + ".wav")
    chain = ["silenceremove=start_periods=1:start_threshold=-50dB"]
    if who == "arian":
        chain.append("rubberband=pitch=1.12:formant=preserved")
    chain.append("loudnorm=I=-16:TP=-2:LRA=7")
    if who == "mom_phone":
        chain.append("highpass=f=320,lowpass=f=3400,acompressor=threshold=-20dB:ratio=3")
    ff("-i", src, "-af", ",".join(chain), "-ar", str(SR), "-ac", "1", dst)
    x = read(dst)
    if who == "mom_phone":
        x *= 0.8
    i = int(a * SR)
    track[i:i + len(x)] += x[:len(track) - i]
    # mouth level per film frame (RMS of 1/24 s windows, normalised to the line's peak)
    n = len(x) // (SR // FPS)
    r = np.array([np.sqrt(np.mean(x[k * SR // FPS:(k + 1) * SR // FPS] ** 2)) for k in range(n)])
    r = np.clip(r / (np.percentile(r, 95) + 1e-6), 0, 1)
    levels.setdefault(who, []).append([a, [round(float(v), 3) for v in r]])
    print(f"{clip}: {len(x) / SR:.2f}s (slot {b - a:.2f}s)")
write(os.path.join(OUT, "dialogue.wav"), track)
json.dump(levels, open(os.path.join(OUT, "levels.json"), "w"))
print("ok")
