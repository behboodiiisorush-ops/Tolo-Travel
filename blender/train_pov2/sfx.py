"""
Sound effects + ambience for «واگن آخر ۲ — برگشت» (no voices — those are recorded by hand).

Everything is synthesised with numpy, so there are no third-party sound files.
Writes out/sfx.wav (62 s, 48 kHz stereo); post.py / mix_voices.py put it under the video.
"""

import math
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = 62.0
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


# ---------------------------------------------------------------- the mix

def build():
    t = tt(N)
    # the same speeds as part_door.py: creeping back from 2 s, faster from 35 s
    speed = np.interp(t, [0, 2, 6, 35, 39, 52, 62], [0, 0, 0.4, 0.4, 1.05, 1.05, 0])
    on = (t < 52).astype(float)

    # our train: heavy slow wheel knocks, a low rumble that grows; brake hiss at the start
    rumble = norm(band(noise(N), 25, 200)) * (0.05 + 0.25 * speed) * on
    put(rumble, 0, 1.0)
    clacks = clack_track(speed * 9) * np.clip(speed, 0, 1.05) * 0.5 * on
    put(clacks, 0, 1.0, 0.2)
    creak = band(noise(N), 300, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t)) ** 4
    put(norm(creak) * 0.06 * np.clip(speed / 0.4, 0, 1) * on, 0, 1.0, 0.3)
    put(band(noise(int(1.4 * SR)), 2000, 9000) * env(int(1.4 * SR), 0.02, 1.0), 1.6, 0.15, 0.4)
    clunk = band(noise(int(0.6 * SR)), 30, 500) * np.exp(-tt(int(0.6 * SR)) * 9)
    put(norm(clunk), 2.0, 0.8)
    put(norm(clunk) * 0.7, 35.2, 0.6)

    # border ambience: crowd behind the fence, floodlight hum, dogs, wind
    crowd = norm(band(noise(N), 250, 1800)) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.6 * t)))
    put(crowd * curve([(0, 0.07), (30, 0.05), (52, 0.03), (52.1, 0), (62, 0)]), 0, 1.0, -0.6)
    hum = np.sin(2 * np.pi * 100 * t) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.2
    put(hum * 0.02 * on, 0, 1.0, -0.4)
    wind = norm(band(noise(N), 150, 1500)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * t))
    put(wind * 0.07 * on, 0, 1.0, 0.1)
    for tb in (5.3, 5.6, 19.8, 33.1):
        nb = int(0.18 * SR)
        f = np.linspace(520, 300, nb)
        bark = np.sin(2 * np.pi * np.cumsum(f) / SR) * band(noise(nb), 300, 2500) * env(nb, 0.01, 0.1)
        put(norm(bark), tb, 0.1, -0.8)

    # our breathing: slow at first, faster as the train speeds up and in the key line
    bt = 0.3
    while bt < 51:
        n = int(0.55 * SR)
        breath = band(noise(n), 300, 3000) * env(n, 0.18, 0.3)
        g = 0.1 if bt < 30 else 0.14
        put(breath, bt, g)
        bt += 1.6 if bt < 35 else 1.1

    # Lena's footsteps on the platform: walking, then trotting
    footsteps(2.4, 35.0, 1.9, 0.12, -0.3)
    footsteps(35.0, 51.8, 3.4, 0.16, -0.3)

    # whistles: one at the start, one long and close in shot 2 ("the train gets louder")
    put(whistle(1.6), 2.4, 0.3, 0.3)
    put(whistle(2.6), 35.6, 0.55, 0.0)

    # the last wagon, alone: a far, hollow clatter that we hear when we look at it
    far = clack_track(np.full(N, 6.0)) * 0.6
    far = band(far, 100, 1800)
    put(norm(far) * curve([(0, 0), (29.5, 0), (30.5, 0.18), (34.6, 0.18), (35.2, 0.02), (47, 0.02),
                           (48, 0.14), (50, 0.14), (50.6, 0), (62, 0)]), 0, 1.0, 0.0)

    # heartbeat: under the key line, then on the question card, then silence
    heartbeat(40.0, 52.0, 92, 0.35)
    heartbeat(52.0, 61.0, 100, 0.55)
    put(tone(200, 0.12, 0.4) * np.exp(-tt(int(0.12 * SR)) * 20), 52.05, 1.0)  # card thump

    # tension pad that swells towards the key line and the card
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.0), (2, 0.05), (25, 0.06), (30, 0.07), (40, 0.08), (45, 0.11), (52, 0.12),
                           (60.5, 0.12), (61.2, 0), (62, 0)]), 0, 1.0)

    fade = curve([(0, 1), (61.0, 1), (61.3, 0), (62, 0)])
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
