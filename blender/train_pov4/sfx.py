"""
Sound effects + ambience for «واگن آخر ۴ — چراغای روشن» (no voices — those are recorded by hand).

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


def build():
    t = tt(N)
    T = KEY_OF
    walk0, walk1 = T["n2"][0] - 0.3, T["me2"][0] - 1.6
    climb1 = T["me2"][0] - 0.2
    border0, border1 = T["mom1"][0] - 1.6, T["lena4"][0] - 1.0
    torch_on = T["me1"][0] + 0.4
    third = ((t >= border0) & (t < border1)).astype(float)
    outside = ((t < climb1) | (t >= T["n5"][0] + 2.5)).astype(float) * (1 - third)
    inside = (1 - outside) * (1 - third)

    # night: crickets and a low wind outside, a creaking quiet inside the wagon
    chirp = np.zeros(N)
    ct = 0.2
    while ct < END:
        n = int(0.05 * SR)
        f0 = rng.uniform(4200, 4800)
        c = np.sin(2 * np.pi * f0 * tt(n)) * env(n, 0.005, 0.03)
        for k in range(3):
            i0 = int((ct + k * 0.07) * SR)
            if i0 + n < N:
                chirp[i0:i0 + n] += c
        ct += rng.uniform(0.35, 0.9)
    put(chirp * (outside * 0.05 + inside * 0.015), 0, 1.0, 0.3)
    wind = norm(band(noise(N), 120, 1200)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.09 * t))
    put(wind * (outside * 0.09 + inside * 0.03), 0, 1.0, -0.2)
    creak = band(noise(N), 300, 1200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t)) ** 6
    put(norm(creak) * inside * 0.05, 0, 1.0, -0.4)

    # our train idling behind us at the start
    idle = sum(np.sin(2 * np.pi * f * t) for f in (48, 96)) * 0.3 + band(noise(N), 40, 160)
    put(norm(idle) * curve([(0, 0.05), (walk0, 0.04), (walk0 + 6, 0.0), (END + 10, 0)]), 0, 1.0, 0.4)

    # the torch clicks on
    click = band(noise(int(0.03 * SR)), 2000, 8000) * env(int(0.03 * SR), 0.001, 0.02)
    put(norm(click), torch_on - 0.05, 0.5, 0.3)
    put(norm(click) * 0.6, torch_on + 0.03, 0.5, 0.3)

    # footsteps on gravel (us and Lena), climbing in, boards inside
    def gravel(t0, t1, rate, gain, pan):
        n = int(0.11 * SR)
        x = t0
        while x < t1:
            cr = band(noise(n), 900, 7000) * np.exp(-tt(n) * 30) + band(noise(n), 80, 600) * np.exp(-tt(n) * 50)
            put(cr, x, gain * rng.uniform(0.7, 1.0), pan)
            x += 1.0 / rate * rng.uniform(0.9, 1.1)
    gravel(walk0, walk1, 2.0, 0.22, 0.0)
    gravel(walk0 + 0.2, walk1, 2.6, 0.14, -0.4)
    clunk = band(noise(int(0.6 * SR)), 30, 500) * np.exp(-tt(int(0.6 * SR)) * 9)
    put(norm(clunk) * 0.6, walk1 + 0.3, 0.5)
    put(norm(clunk) * 0.5, climb1, 0.45)
    put(norm(clunk) * 0.4, climb1 + 0.7, 0.35, -0.3)
    footsteps(T["n5"][0] + 2.5, T["n5"][0] + 3.5, 2.0, 0.15)

    # the border camp: murmur, the floodlight hum, a far siren
    crowd = norm(band(noise(N), 250, 1800)) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.5 * t)))
    put(crowd * third * 0.07, 0, 1.0, -0.3)
    hum = np.sin(2 * np.pi * 100 * t) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.2
    put(hum * third * 0.02, 0, 1.0)
    put(siren(border1 - border0) * 0.4, border0, 0.08, 0.7)
    footsteps(border0 + 0.2, T["gm1"][0] - 0.2, 1.8, 0.12, -0.5)       # grandma's slow steps
    for b in (border0, border1):
        put(tone(200, 0.1, 0.25) * np.exp(-tt(int(0.1 * SR)) * 25), b, 1.0)
    # a soft warm chord when they find each other
    warm = sum(np.sin(2 * np.pi * f * t) for f in (261.6, 329.6, 392.0)) * curve(
        [(0, 0), (T["gm1"][0], 0), (T["mom2"][0], 0.03), (border1, 0.02), (border1 + 0.3, 0), (END + 10, 0)])
    put(warm, 0, 1.0)

    # heartbeat under the last line; the card: only wind
    heartbeat(T["n5"][0], END, 80, 0.3)
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.0), (2, 0.035), (walk1, 0.05), (T["jalal1"][0], 0.03), (border0, 0.04),
                           (border1, 0.05), (END - 0.3, 0.09), (END, 0), (END + 10, 0)]), 0, 1.0)
    put(wind * curve([(0, 0), (END - 0.2, 0), (END, 0.1), (END + 7.4, 0.1), (END + 8, 0)]), 0, 1.0)

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
