"""Sound for «جرقه ۲»: every effect is a real ElevenLabs sound effect (sfx_el/), every line an ElevenLabs voice
(voices/clips, loudness-matched). Effects duck ~13 dB under each line.

    python3 sound.py   -> out/spark2_sfx.wav (effects only), out/spark2_mix.wav (effects + voices)
"""
import os, subprocess, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import END, LINES, CLIPS  # noqa: E402

SR = 48000
CARD = 4.0
TOTAL = END + CARD
N = int(TOTAL * SR)


def read(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return x / max(1e-9, np.abs(x).max())


def onset(x, th=0.15):
    return int(np.argmax(np.abs(x) > th))


def put(track, x, t, gain, align=True):
    i = int(t * SR) - (onset(x) if align else 0)
    a, b = max(0, i), min(len(track), i + len(x))
    if b > a:
        track[a:b] += x[a - i:b - i] * gain


def bed(track, name, t0, t1, gain, fade=1.0):
    x = read(os.path.join(HERE, "sfx_el", name + ".mp3"))
    n, xf = int((t1 - t0) * SR), int(fade * SR)
    out, pos = np.zeros(n + len(x)), 0
    while pos < n:
        y = x.copy()
        y[:xf] *= np.linspace(0, 1, xf)
        y[-xf:] *= np.linspace(1, 0, xf)
        out[pos:pos + len(y)] += y
        pos += len(y) - xf
    out = out[:n]
    out[:xf] *= np.linspace(0, 1, xf)
    out[-xf:] *= np.linspace(1, 0, xf)
    put(track, out, t0, gain, align=False)


def fx(track, name, t, gain):
    put(track, read(os.path.join(HERE, "sfx_el", name + ".mp3")), t, gain)


def effects():
    tr = np.zeros(N)
    bed(tr, "kitchen", 0.0, 10.0, 0.25)
    fx(tr, "glass_zap", 7.0, 0.8)
    fx(tr, "flicker", 7.05, 0.5)
    bed(tr, "hallway", 10.0, 17.0, 0.45)
    fx(tr, "entrance", 16.6, 0.45)
    bed(tr, "courtyard", 17.0, TOTAL, 0.3)
    fx(tr, "touch", 32.0, 1.0)
    fx(tr, "visitor", 36.0, 0.9)
    return tr


def voices():
    v = np.zeros(N)
    for (a, b, who, _), name in zip(LINES, CLIPS):
        x = read(os.path.join(HERE, "voices", "clips", name + ".wav")) * 0.9
        put(v, x, a, 1.0)
    return v


def duck(fx_track, v):
    """effects about -13 dB under every line (smooth 120 ms envelope)"""
    env = np.convolve(np.abs(v) > 0.02, np.ones(int(0.12 * SR)) / int(0.12 * SR), mode="same")
    env = np.clip(env * 3, 0, 1)
    return fx_track * (1 - env * (1 - 10 ** (-13 / 20)))


def write(path, mono):
    mono = mono / max(1e-9, np.max(np.abs(mono))) * 0.89
    st = np.stack([mono, mono], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    e, v = effects(), voices()
    write(os.path.join(HERE, "out", "spark2_sfx.wav"), e)
    write(os.path.join(HERE, "out", "spark2_mix.wav"), duck(e * 0.35, v) + v)
    print("ok")
