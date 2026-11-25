"""
Sound effects + ambience for «واگن آخر ۵ — شهر خاموش» (no voices — those are recorded by hand).

Everything is synthesised with numpy, so there are no third-party sound files.
Writes out/sfx.wav (the film + the card, 48 kHz stereo); post.py / mix_voices.py put it under the video.
"""

import math
import os
import wave

import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from captions import END, KEY_OF  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = END + 8.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


# ---------------------------------------------------------------- helpers

def tt(n):
    return np.arange(n) / SR


def noise(n):
    return rng.standard_normal(n)


def band(x, lo, hi):
    """Band-pass by zeroing FFT bins (fine for offline sound design)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def env(n, a=0.01, r=0.3):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def norm(x):
    m = np.max(np.abs(x))
    return x / m if m > 0 else x


def put(x, t0, gain=1.0, pan=0.0):
    """Mix x at time t0 (s). pan -1 = left, +1 = right."""
    i = int(t0 * SR)
    if i >= N:
        return
    x = x[: N - i]
    gl, gr = gain * math.sqrt((1 - pan) / 2), gain * math.sqrt((1 + pan) / 2)
    L[i:i + len(x)] += x * gl
    R[i:i + len(x)] += x * gr


def curve(points, n=N):
    """Piecewise-linear automation from [(t, value), ...]."""
    ts, vs = zip(*points)
    return np.interp(tt(n), ts, vs)


# ---------------------------------------------------------------- sounds

def explosion(length=3.0, size=1.0):
    n = int(length * SR)
    boom = band(noise(n), 20, 400) * np.exp(-tt(n) * 1.6 / size)
    crack = band(noise(n), 400, 5000) * np.exp(-tt(n) * 9)
    sub = np.sin(2 * np.pi * 45 * tt(n)) * np.exp(-tt(n) * 2.5)
    return norm(boom * 1.0 + crack * 0.35 + sub * 0.6) * env(n, 0.005, 0.8)


def whistle(length=1.6):
    n = int(length * SR)
    t = tt(n)
    tone = sum(np.sin(2 * np.pi * f * t) / (k + 1) for k, f in enumerate((587, 740, 880)))
    breath = band(noise(n), 1500, 6000) * 0.15
    vib = 1 + 0.05 * np.sin(2 * np.pi * 6 * t)
    return norm((tone + breath) * vib) * env(n, 0.06, 0.4)


def siren(length=6.0):
    n = int(length * SR)
    t = tt(n)
    f = 450 + 350 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 2.4))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph)
    return norm(x) * env(n, 0.8, 0.8)


def jet(length=1.6):
    n = int(length * SR)
    t = tt(n)
    roar = band(noise(n), 60, 3000)
    e = np.exp(-((t - length * 0.45) / (length * 0.22)) ** 2)
    return norm(roar) * e


def clack_track(speed):
    """Wheel clacks: two quick knocks per rail joint, rate follows train speed (m/s array)."""
    out = np.zeros(N)
    pos = np.cumsum(speed) / SR
    joints = np.floor(pos / 18.0)
    idx = np.nonzero(np.diff(joints) > 0)[0]
    k = band(noise(int(0.06 * SR)), 80, 1800) * np.exp(-tt(int(0.06 * SR)) * 60)
    for i in idx:
        for d in (0.0, 0.11 * 8.0 / max(speed[i], 1.0)):
            j = i + int(d * SR)
            if j + len(k) < N:
                out[j:j + len(k)] += k
    return norm(out)


def heartbeat(t0, t1, bpm, gain):
    beat = np.sin(2 * np.pi * 55 * tt(int(0.12 * SR))) * np.exp(-tt(int(0.12 * SR)) * 30)
    t = t0
    while t < t1:
        put(beat, t, gain)
        put(beat * 0.7, t + 0.22, gain)
        t += 60.0 / bpm


def footsteps(t0, t1, rate, gain, pan=0.0):
    step = band(noise(int(0.08 * SR)), 60, 2500) * np.exp(-tt(int(0.08 * SR)) * 45)
    t = t0
    while t < t1:
        put(step, t, gain * rng.uniform(0.7, 1.0), pan)
        t += 1.0 / rate


def tone(freq, length, gain=1.0):
    n = int(length * SR)
    return np.sin(2 * np.pi * freq * tt(n)) * env(n, 0.01, 0.02) * gain


def growl(length, pitch=1.0):
    n = int(length * SR)
    tt_ = tt(n)
    f0 = (70 + 25 * np.sin(2 * np.pi * 1.3 * tt_) + 10 * rng.standard_normal(n).cumsum() / SR) * pitch
    buzz = np.sign(np.sin(2 * np.pi * np.cumsum(f0) / SR)) * 0.6 + band(noise(n), 100, 1200)
    form = band(buzz, 200, 900) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 2.1 * tt_)))
    return norm(form) * env(n, 0.15, 0.4)


def build():
    t = tt(N)
    T = KEY_OF
    brake0 = T["rahim2"][0] - 0.3
    stop = T["rahim2"][0] + 2.2
    v = np.interp(t, [0, T["n2"][0] - 1, T["n2"][0] + 1, brake0, stop, END + 10], [8, 8, 5, 5, 0, 0])
    # the train: rumble and wheel clacks while it runs
    put(norm(band(noise(N), 25, 200)) * (0.04 + 0.02 * v) * (v > 0.05), 0, 1.0)
    put(clack_track(np.maximum(v, 0)) * np.clip(v / 8, 0, 1) * 0.35, 0, 1.0, 0.2)
    # the brakes: a long screech, the jolt, the hiss
    n = int((stop - brake0) * SR)
    sq = np.sin(2 * np.pi * np.cumsum(np.linspace(3200, 2200, n)) / SR) * env(n, 0.2, 0.4)
    put(sq + 0.4 * band(noise(n), 2000, 7000) * env(n, 0.2, 0.4), brake0, 0.16)
    clunk = band(noise(int(0.6 * SR)), 30, 500) * np.exp(-tt(int(0.6 * SR)) * 9)
    put(norm(clunk), stop - 0.1, 0.8)
    put(band(noise(int(1.5 * SR)), 2000, 9000) * env(int(1.5 * SR), 0.02, 1.0), stop + 0.2, 0.12, -0.3)
    # the dead city: no birds, only wind, a far siren that never stops, a creaking sign
    wind = norm(band(noise(N), 120, 1300)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t))
    put(wind * 0.07, 0, 1.0, -0.3)
    put(siren(END) * 0.4, 0.0, 0.03, -0.8)
    # the figures outside: low groans, more and closer after the train stops
    for k in range(5):
        put(band(growl(1.4, rng.uniform(0.85, 1.1)), 80, 600), T["n2"][0] + k * 1.7, 0.08, -0.7)
    for k in range(10):
        put(growl(1.5, rng.uniform(0.85, 1.15)), T["me1"][0] - 1.6 + k * 1.1, 0.12 + 0.03 * k, rng.uniform(-0.9, -0.3))
    footsteps(T["me1"][0] - 1.6, END, 2.2, 0.1, -0.6)
    # a hand on the glass at the very end
    put(norm(band(noise(int(0.2 * SR)), 200, 2500)) * env(int(0.2 * SR), 0.005, 0.15), END - 2.0, 0.4, -0.6)
    # the radio crackle on Rahim's lines
    for key in ("rahim1", "rahim3"):
        a, b = T[key]
        put(band(noise(int(0.12 * SR)), 1000, 5000), a - 0.35, 0.15, 0.4)
    # heartbeat from the stop to the end; tension pad; the card: only wind
    heartbeat(stop, END, 112, 0.35)
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.03), (T["n2"][0], 0.05), (stop, 0.08), (END - 0.3, 0.11), (END, 0), (END + 10, 0)]),
        0, 1.0)
    put(wind * curve([(0, 0), (END - 0.2, 0), (END, 0.08), (END + 7.4, 0.08), (END + 8, 0)]), 0, 1.0)

    fade = curve([(0, 1), (END + 7.6, 1), (END + 7.9, 0), (END + 10, 0)])
    out = np.stack([L * fade, R * fade], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


def write(path, data):
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "sfx.wav")
    write(p, build())
    print(p)
