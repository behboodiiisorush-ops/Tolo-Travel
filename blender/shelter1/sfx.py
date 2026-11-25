"""
Sound effects + ambience for «پناهگاه ۱ — نُه دقیقه» (no voices — those are recorded by hand).

Everything is synthesised with numpy, so there are no third-party sound files.
Writes out/sfx.wav (the film + the card, 48 kHz stereo); post.py / mix_voices.py put it under the video.
"""

import math
import os
import wave

import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from captions import END, FLASH_AFTER, KEY_OF  # noqa: E402

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
    street0 = T["mom2"][0] - 1.4
    arrive = T["guard1"][0] - 0.4
    enter1 = T["jalal1"][0] - 0.1
    close0, close1 = T["guard2"][0], T["guard2"][1] + 0.2
    flash = T["n2"][1] + FLASH_AFTER
    knock0 = T["n3"][0] - 2.4
    house = (t < street0).astype(float)
    street = ((t >= street0) & (t < enter1)).astype(float)
    inside_before = ((t >= enter1) & (t < flash)).astype(float)

    # the emergency alert: the two-tone phone alarm in the dark, then under the house scene
    n = int(0.5 * SR)
    beep = (np.sin(2 * np.pi * 853 * tt(n)) + np.sin(2 * np.pi * 960 * tt(n))) * env(n, 0.01, 0.02)
    k = 0.0
    while k < street0 - 0.5:
        g = 0.35 if k < 3.0 else 0.08
        put(beep, k, g)
        k += 0.62
    # TV snow in the house
    put(norm(band(noise(N), 1500, 9000)) * house * 0.03, 0, 1.0, -0.5)
    heartbeat(0.2, street0, 100, 0.35)

    # the city: air-raid sirens, screaming crowd, car alarms, running feet
    sir = siren(min(flash, END) - 0.5)
    put(sir * 0.6, 0.5, 0.06, -0.6)
    put(siren(max(1.0, flash - street0)), street0, 0.2, 0.5)
    crowd = norm(band(noise(N), 300, 2500)) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 0.8 * t)))
    put(crowd * (street * 0.12 + house * 0.03 + inside_before * 0.05), 0, 1.0, 0.2)
    for k in range(6):  # screams
        nn = int(0.7 * SR)
        f = np.linspace(rng.uniform(900, 1300), rng.uniform(600, 800), nn)
        sc = np.sin(2 * np.pi * np.cumsum(f) / SR) * band(noise(nn), 600, 3000) * env(nn, 0.05, 0.3)
        put(norm(sc), street0 + 1.0 + k * 2.3 + rng.uniform(0, 1), 0.06, rng.uniform(-0.8, 0.8))
    nn = int(1.6 * SR)
    car_alarm = np.sin(2 * np.pi * (1200 + 400 * np.sign(np.sin(2 * np.pi * 3 * tt(nn)))) * tt(nn)) * env(nn, 0.02, 0.1)
    for k in range(4):
        put(car_alarm, street0 + 3 + k * 1.7, 0.05, 0.6)
    footsteps(street0, arrive, 4.2, 0.25)
    footsteps(street0 + 0.1, arrive, 3.6, 0.13, -0.4)

    # the bunker door: dragged shut, a deep clang, the bolt
    nn = int((close1 - close0) * SR)
    drag = band(noise(nn), 100, 900) * env(nn, 0.1, 0.1)
    put(norm(drag), close0, 0.25)
    nn = int(1.5 * SR)
    clang = sum(np.sin(2 * np.pi * f * tt(nn)) for f in (92, 147, 233, 411)) * np.exp(-tt(nn) * 3)
    put(norm(clang + band(noise(nn), 40, 600) * np.exp(-tt(nn) * 8)), close1 - 0.05, 0.8)
    put(norm(band(noise(int(0.15 * SR)), 800, 5000)) * env(int(0.15 * SR), 0.002, 0.1), close1 + 0.5, 0.4)
    # outside goes muffled once the door is shut
    # the bomb: a white silence, then the shockwave arrives and the ground shakes
    put(explosion(6.0, 3.0), flash + 0.35, 1.0)
    put(norm(band(noise(int(4 * SR)), 20, 120)) * np.exp(-tt(int(4 * SR)) * 0.9), flash + 0.3, 0.8)
    for k in range(10):  # dust and debris on the ceiling
        put(band(noise(int(0.2 * SR)), 1000, 6000) * env(int(0.2 * SR), 0.005, 0.15), flash + 1.0 + k * 0.25, 0.08,
            rng.uniform(-0.7, 0.7))
    put(norm(band(noise(int(0.3 * SR)), 2000, 8000)) * env(int(0.3 * SR), 0.005, 0.2), flash + 0.5, 0.3)  # bulb pops
    # ringing ears, then silence
    nn = int(5 * SR)
    put(np.sin(2 * np.pi * 4100 * tt(nn)) * np.exp(-tt(nn) * 0.7), flash + 1.2, 0.05)
    # in the dark: breathing, the torch click, the radio, three knocks on the steel door
    for k in range(int((END - flash - 3) / 1.3)):
        nn = int(0.4 * SR)
        put(band(noise(nn), 400, 3500) * env(nn, 0.1, 0.2), flash + 3 + k * 1.3, 0.06, 0.3)
    click = band(noise(int(0.03 * SR)), 2000, 8000) * env(int(0.03 * SR), 0.001, 0.02)
    put(norm(click), T["lena3"][0] - 0.95, 0.5, 0.3)
    nn = int((T["radio1"][1] - T["radio1"][0] + 2.0) * SR)
    static = band(noise(nn), 800, 6000) * (0.5 + 0.5 * (rng.random(nn) > 0.6)) * env(nn, 0.3, 0.6)
    put(static, T["radio1"][0] - 1.0, 0.08, -0.4)
    nn = int(0.35 * SR)
    knock = band(noise(nn), 50, 700) * np.exp(-tt(nn) * 18) + sum(np.sin(2 * np.pi * f * tt(nn)) for f in (180, 290)) * np.exp(-tt(nn) * 15) * 0.3
    for k in range(3):
        put(norm(knock), knock0 + k * 0.7, 0.55)

    # drone: rising through the run, cut by the flash; back, low, in the dark
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0), (1, 0.04), (street0, 0.05), (arrive, 0.08), (flash - 0.05, 0.1), (flash, 0),
                           (flash + 4, 0), (flash + 6, 0.05), (END - 0.3, 0.08), (END, 0), (END + 10, 0)]), 0, 1.0)
    wind = norm(band(noise(N), 120, 1200))
    put(wind * curve([(0, 0), (END - 0.2, 0), (END, 0.05), (END + 7.4, 0.05), (END + 8, 0)]), 0, 1.0)

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
