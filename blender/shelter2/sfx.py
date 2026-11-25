"""
Sound effects + ambience for «پناهگاه ۲ — چراغ سبز» (no voices — those are recorded by hand).

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
    """A zombie growl: low buzzing noise through a moving formant, rough and uneven."""
    n = int(length * SR)
    tt_ = tt(n)
    f0 = (70 + 25 * np.sin(2 * np.pi * 1.3 * tt_) + 10 * rng.standard_normal(n).cumsum() / SR) * pitch
    buzz = np.sign(np.sin(2 * np.pi * np.cumsum(f0) / SR)) * 0.6 + band(noise(n), 100, 1200)
    form = band(buzz, 200, 900) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 2.1 * tt_)))
    return norm(form) * env(n, 0.15, 0.4)


def build():
    t = tt(N)
    T = KEY_OF
    green0 = T["mom1"][0] - 1.4
    open0, open1 = T["guard2"][1] - 0.2, T["n3"][0] + 1.4
    growl0 = T["me2"][0] - 2.0
    lunge0 = T["guard3"][0] - 0.5
    close0, close1 = T["guard3"][0] + 0.4, T["lena3"][0] - 1.4
    outside = curve([(0, 0), (open0, 0), (open1, 1), (close0, 1), (close1, 0), (END + 10, 0)])

    # inside: the ventilation hum and the dim lamp buzz, all the time
    hum = norm(band(noise(N), 60, 300)) * 0.5 + np.sin(2 * np.pi * 50 * t) * 0.3
    put(norm(hum) * 0.05, 0, 1.0)
    # three knocks in the dark, as episode 1 ended
    nn = int(0.35 * SR)
    knock = band(noise(nn), 50, 700) * np.exp(-tt(nn) * 18) + sum(np.sin(2 * np.pi * f * tt(nn)) for f in (180, 290)) * np.exp(-tt(nn) * 15) * 0.3
    for k in range(3):
        put(norm(knock), 0.3 + k * 0.7, 0.6)
    # breathing, tired coughs
    for k in range(int(green0 / 2.2)):
        n2 = int(0.4 * SR)
        put(band(noise(n2), 400, 3500) * env(n2, 0.1, 0.2), 3 + k * 2.2, 0.04, rng.uniform(-0.6, 0.6))
    # beep: the light turns green
    for k in range(2):
        put(tone(1320, 0.12, 0.35), green0 + k * 0.18)
    # murmur when everyone stands
    put(norm(band(noise(int(3 * SR)), 300, 2000)) * env(int(3 * SR), 0.3, 1.0), T["mom1"][0] - 0.2, 0.05)
    # the door: wheel creak, a long metal grind, the gust of outside air
    put(norm(band(noise(int(1.0 * SR)), 600, 2500)) * env(int(1.0 * SR), 0.1, 0.2), open0 - 0.8, 0.15)
    nn = int((open1 - open0) * SR)
    grind = np.sin(2 * np.pi * np.cumsum(np.linspace(140, 95, nn)) / SR) * 0.5 + band(noise(nn), 80, 900)
    put(norm(grind) * env(nn, 0.2, 0.4), open0, 0.3)
    wind = norm(band(noise(N), 120, 1300)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t))
    put(wind * outside * 0.11, 0, 1.0, -0.2)
    put(norm(band(noise(int(1.5 * SR)), 200, 3000)) * env(int(1.5 * SR), 0.1, 1.0), open1 - 0.6, 0.12)
    # Lena's quick feet on the gravel, ours after her
    footsteps(T["lena2"][0] - 0.2, T["lena2"][0] + 1.1, 4.5, 0.12, 0.2)
    footsteps(T["me1"][0] - 0.2, T["me1"][0] + 0.6, 3.5, 0.15)
    # the zombie: dragging feet, growls, the lunge
    footsteps(growl0, lunge0, 1.3, 0.12, -0.2)
    for k in range(int((lunge0 - growl0) / 1.6) + 1):
        put(growl(1.3, rng.uniform(0.9, 1.1)), growl0 + k * 1.6, 0.35 * (0.6 + 0.4 * k / 3), -0.1)
    put(growl(1.6, 1.25), lunge0, 0.7)
    put(growl(2.0, 1.1), close0 + 0.5, 0.6)
    # the door shoved shut: scrape, the slam, the bolt
    nn = int((close1 - close0) * SR)
    put(norm(band(noise(nn), 100, 1500)) * env(nn, 0.05, 0.1), close0, 0.3)
    nn = int(1.5 * SR)
    clang = sum(np.sin(2 * np.pi * f * tt(nn)) for f in (92, 147, 233, 411)) * np.exp(-tt(nn) * 3)
    put(norm(clang + band(noise(nn), 40, 600) * np.exp(-tt(nn) * 8)), close1 - 0.05, 0.85)
    put(norm(band(noise(int(0.15 * SR)), 800, 5000)) * env(int(0.15 * SR), 0.002, 0.1), close1 + 0.4, 0.4)
    # bangs from outside on the steel door, and muffled growls through it
    for k, tb in enumerate((close1 + 0.9, close1 + 1.6, close1 + 2.6, close1 + 4.2, close1 + 6.5)):
        put(norm(clang) * 0.6, tb, 0.5 - 0.06 * k)
    put(band(growl(3.0, 0.9), 80, 500), close1 + 1.0, 0.25)
    # heartbeat from the growl to the end; then only wind on the card
    heartbeat(growl0, END, 110, 0.3)
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.03), (green0, 0.03), (green0 + 0.5, 0.0), (open1, 0.0), (growl0, 0.05),
                           (lunge0, 0.09), (close1, 0.1), (END - 0.3, 0.08), (END, 0), (END + 10, 0)]), 0, 1.0)
    put(wind * curve([(0, 0), (END - 0.2, 0), (END, 0.06), (END + 7.4, 0.06), (END + 8, 0)]), 0, 1.0)

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
