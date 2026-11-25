"""
Sound effects + ambience for «تک‌تیرانداز ۱ — نقطهٔ قرمز» (no voices — those are recorded by hand).

Everything is synthesised with numpy, so there are no third-party sound files.
Writes out/sfx.wav (the film + the card, 48 kHz stereo); post.py / mix_voices.py put it under the video.
"""

import math
import os
import wave

import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from captions import END, KEY_OF, scope_windows  # noqa: E402

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


def build():
    t = tt(N)
    T = KEY_OF
    scopes = scope_windows()
    scoped = np.zeros(N)
    for a, b in scopes:
        scoped[(t >= a) & (t < b)] = 1.0
    roof = 1 - scoped

    # wind at 230 m: strong on the roof, a low hiss behind the scope
    wind = norm(band(noise(N), 100, 1600)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t) ** 2)
    put(wind * (0.05 + 0.13 * roof), 0, 1.0, 0.2)
    # the city far below: traffic hum, a horn now and then, the crowd and the fountain (faint, through the scope)
    city = norm(band(noise(N), 60, 700))
    put(city * 0.05, 0, 1.0, -0.2)
    for k in range(6):
        nh = int(0.5 * SR)
        horn = (np.sin(2 * np.pi * 420 * tt(nh)) + np.sin(2 * np.pi * 523 * tt(nh))) * env(nh, 0.02, 0.1)
        put(horn, 3 + k * 7.3 + rng.uniform(0, 2), 0.02, rng.uniform(-0.8, 0.8))
    crowd = norm(band(noise(N), 300, 2000)) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.5 * t)))
    put(crowd * scoped * 0.035, 0, 1.0)
    put(norm(band(noise(N), 1500, 7000)) * scoped * 0.015, 0, 1.0, 0.3)   # fountain
    # the scope: a metal click every time it zooms
    click = band(noise(int(0.04 * SR)), 1500, 7000) * env(int(0.04 * SR), 0.001, 0.03)
    for tc in (scopes[1][0] + 0.1, T["me2"][0], T["me3"][0], T["girl1"][0] - 1.2, T["n2"][0] - 1.6):
        put(norm(click), tc, 0.35)
        put(norm(click) * 0.6, tc + 0.07, 0.35)
    # the bolt, quietly, before the scope goes up again
    put(norm(band(noise(int(0.25 * SR)), 300, 4000)) * env(int(0.25 * SR), 0.005, 0.15), scopes[1][0] - 0.6, 0.4)
    # radio: static and a squelch on every commander line
    for key in ("cmd1", "cmd2", "cmd3"):
        a, b = T[key]
        nn = int((b - a + 0.6) * SR)
        st = band(noise(nn), 800, 6000) * (0.5 + 0.5 * (rng.random(nn) > 0.6)) * env(nn, 0.05, 0.2)
        put(st, a - 0.3, 0.05, 0.5)
        put(band(noise(int(0.1 * SR)), 1000, 5000), a - 0.32, 0.18, 0.5)
        put(band(noise(int(0.1 * SR)), 1000, 5000), b + 0.2, 0.14, 0.5)
    # breathing behind the scope, the heart beating faster from "three seconds" on
    for k in range(int(END / 2.4)):
        nb = int(0.5 * SR)
        put(band(noise(nb), 300, 3000) * env(nb, 0.15, 0.3), 1.0 + k * 2.4, 0.05)
    heartbeat(0.0, T["cmd2"][0], 72, 0.25)
    heartbeat(T["cmd2"][0], END, 118, 0.42)
    # the girl's laugh far away is in the recording; a warm chord under the gift and the hug
    warm = sum(np.sin(2 * np.pi * f * t) for f in (261.6, 329.6, 392.0)) * curve(
        [(0, 0), (T["girl1"][0], 0), (T["man1"][0], 0.025), (T["cmd3"][0], 0.0), (END + 10, 0)])
    put(warm, 0, 1.0)
    # tension pad, then the hard silence of the last look; the card: only wind
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.03), (T["cmd2"][0], 0.06), (T["cmd3"][0], 0.11), (T["n2"][0] - 1.6, 0.11),
                           (T["n2"][0] - 1.4, 0.0), (END + 10, 0)]), 0, 1.0)
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
